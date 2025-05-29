import time
from dataclasses import dataclass

from animation import Animation, AnimationEvolution, VisionAngle
from llm_utils import (
    generate_abstract_summary,
    generate_animation_score,
    generate_auto_improved_centers_code,
    generate_auto_improved_opacities_code,
    generate_auto_improved_rgbs_code,
    generate_centers_behavior,
    generate_centers_code,
    generate_feedback_improved_centers_code,
    generate_feedback_improved_opacities_code,
    generate_feedback_improved_rgbs_code,
    generate_opacities_behavior,
    generate_opacities_code,
    generate_rgbs_behavior,
    generate_rgbs_code,
)
from renderer import Renderer, render_subdirectory
from state import State
from viser import ClientHandle, GuiApi


@dataclass
class GeneratorConfig:
    animation_title: str
    animation_description: str
    animation_duration: int
    design_temperature: float
    code_temperature: float
    vision_angles: list[VisionAngle]
    n_samples: int


class Generator:
    def __init__(
        self,
        config: GeneratorConfig,
        client: ClientHandle,
        gui_api: GuiApi,
        state: State,
    ):
        self.config = config
        self.client = client
        self.gui_api = gui_api
        self.state = state
        self.output = AnimationEvolution()
        self.subdirectory = render_subdirectory(
            config.animation_title, config.animation_duration
        )

    def auto_sample(self) -> None:
        status = self.gui_api.add_markdown("*Auto Sampling...*")
        sub_status = self.gui_api.add_markdown("")

        # Step 1: Get Vision Images
        sub_status.content = "*Rendering Vision Angles...*"
        vision_images = self._render_vision_angles()

        # Step 2: Generate Samples With Score
        samples: list[Animation] = []
        n_samples = self.config.n_samples
        for i in range(n_samples):
            sub_status.content = f"*Generating Sample {i + 1}/{n_samples}...*"
            sample = self._generate_animation(vision_images)
            samples.append(sample)
            if n_samples > 1:
                sub_status.content = f"*Scoring Sample {i+1}...*"
                progress = self.gui_api.add_progress_bar(100, animated=True)
                sample_dir = f"render/{self.subdirectory}/auto_sample/sample_{i}"
                score = self._score_animation(sample, sample_dir)
                sample.score = score
                progress.remove()
        self.output.auto_sampled_animations = samples

        # Step 3: Choose Best Sample
        score_to_animation = {sample.score: sample for sample in samples}
        max_score = max(score_to_animation.keys())
        self.output.final_animation = score_to_animation[max_score]

        sub_status.remove()
        status.remove()

    def auto_improve(self) -> None:
        status = self.gui_api.add_markdown("*Auto Improving...*")
        sub_status = self.gui_api.add_markdown("")

        base_animation = self.output.final_animation
        description = self.config.animation_description
        code_temperature = self.config.code_temperature

        ## Step 1: Render Base Animation
        sub_status.content = "*Rendering Base Animation...*"
        self.state.active_animation = base_animation
        time.sleep(1)
        self.state.visible_frame = 0
        time.sleep(1)
        renderer = Renderer(self.client, self.gui_api, self.state)
        i = len(self.output.auto_improved_animations)
        base_animation_dir = f"render/{self.subdirectory}/auto_improve/base_animation_{i}"
        base_animation_frames = renderer.render_first_frames(base_animation_dir)

        ## Step 2.1: Improve `compute_centers`
        sub_status.content = "*Improving `compute_centers`...*"
        progress = self.gui_api.add_progress_bar(1, animated=True)
        base_centers_code = base_animation.centers_code
        improved_centers_code = ""
        while True:
            improved_centers_code = generate_auto_improved_centers_code(
                base_centers_code, base_animation_frames, description, code_temperature
            )
            if self._is_working_centers_code(improved_centers_code):
                break

        ## Step 2.2: Improve `compute_rgbs`
        sub_status.content = "*Improving `compute_rgbs`...*"
        progress.value = 34
        base_rgbs_code = base_animation.rgbs_code
        improved_rgbs_code = ""
        while True:
            improved_rgbs_code = generate_auto_improved_rgbs_code(
                base_rgbs_code, base_animation_frames, description, code_temperature
            )
            if self._is_working_rgbs_code(improved_rgbs_code):
                break

        ## Step 2.3: Improve `compute_opacities`
        sub_status.content = "*Improving `compute_opacities`...*"
        progress.value = 67
        base_opacities_code = base_animation.opacities_code
        improved_opacities_code = ""
        while True:
            improved_opacities_code = generate_auto_improved_opacities_code(
                base_opacities_code, base_animation_frames, description, code_temperature
            )
            if self._is_working_opacities_code(improved_opacities_code):
                break
        progress.remove()

        # Step 3: Save Improved Animation
        improved_animation = Animation(
            title=base_animation.title,
            description=base_animation.description,
            duration=base_animation.duration,
            abstract_summary=base_animation.abstract_summary,
            centers_behavior=base_animation.centers_behavior,
            rgbs_behavior=base_animation.rgbs_behavior,
            opacities_behavior=base_animation.opacities_behavior,
            centers_code=improved_centers_code,
            rgbs_code=improved_rgbs_code,
            opacities_code=improved_opacities_code,
        )
        self.output.auto_improved_animations.append(improved_animation)
        self.output.final_animation = improved_animation

        sub_status.remove()
        status.remove()

    def feedback_improve(self, feedback: str) -> None:
        status = self.gui_api.add_markdown("*Feedback Improving...*")
        sub_status = self.gui_api.add_markdown("")

        base_animation = self.output.final_animation
        code_temperature = self.config.code_temperature
        description = self.config.animation_description
        
        ## Step 1: Render Base Animation
        sub_status.content = "*Rendering Base Animation...*"
        self.state.active_animation = base_animation
        time.sleep(1)
        self.state.visible_frame = 0
        time.sleep(1)
        renderer = Renderer(self.client, self.gui_api, self.state)
        image_dir = f"render/{self.subdirectory}/feedback/input_{len(self.output.feedback_to_animation)}"
        first_frames = renderer.render_first_frames(image_dir)

        ## Step 2.1: Improve `compute_centers`
        sub_status.content = "*Improving `compute_centers`...*"
        progress = self.gui_api.add_progress_bar(1, animated=True)
        base_centers_code = base_animation.centers_code
        improved_centers_code = ""
        while True:
            improved_centers_code = generate_feedback_improved_centers_code(
                feedback, base_centers_code, first_frames, description, code_temperature
            )
            if self._is_working_centers_code(improved_centers_code):
                break

        ## Step 2.2: Improve `compute_rgbs`
        sub_status.content = "*Improving `compute_rgbs`...*"
        progress.value = 34
        base_rgbs_code = base_animation.rgbs_code
        improved_rgbs_code = ""
        while True:
            improved_rgbs_code = generate_feedback_improved_rgbs_code(
                feedback, base_rgbs_code, first_frames, description, code_temperature
            )
            if self._is_working_rgbs_code(improved_rgbs_code):
                break

        ## Step 2.3: Improve `compute_opacities`
        sub_status.content = "*Improving `compute_opacities`...*"
        progress.value = 67
        base_opacities_code = base_animation.opacities_code
        improved_opacities_code = ""
        while True:
            improved_opacities_code = generate_feedback_improved_opacities_code(
                feedback, base_opacities_code, first_frames, description, code_temperature
            )
            if self._is_working_opacities_code(improved_opacities_code):
                break
        progress.remove()

        # Step 3: Save Improved Animation
        improved_animation = Animation(
            title=base_animation.title,
            duration=base_animation.duration,
            abstract_summary=base_animation.abstract_summary,
            centers_behavior=base_animation.centers_behavior,
            rgbs_behavior=base_animation.rgbs_behavior,
            opacities_behavior=base_animation.opacities_behavior,
            centers_code=improved_centers_code,
            rgbs_code=improved_rgbs_code,
            opacities_code=improved_opacities_code,
        )

        self.output.feedback_to_animation[feedback] = improved_animation
        self.output.final_animation = improved_animation

        sub_status.remove()
        status.remove()

    def _generate_animation(self, images: list[str] = []) -> Animation:
        title = self.config.animation_title
        description = self.config.animation_description
        duration = self.config.animation_duration
        design_temperature = self.config.design_temperature
        code_temperature = self.config.code_temperature

        # Design Phase
        status = self.gui_api.add_markdown("(1/7) *Interpreting Description...*")
        progress = self.gui_api.add_progress_bar(value=12, animated=True)
        abstract_summary = generate_abstract_summary(
            description, duration, design_temperature, images
        )

        status.content = "(2/7) *Designing Centers Behavior...*"
        progress.value = 24
        centers_behavior = generate_centers_behavior(
            abstract_summary, design_temperature, images
        )

        status.content = "(3/7) *Designing RGBs Behavior...*"
        progress.value = 36
        rgbs_behavior = generate_rgbs_behavior(
            abstract_summary, design_temperature, images
        )

        status.content = "(4/7) *Designing Opacities Behavior...*"
        progress.value = 48
        opacities_behavior = generate_opacities_behavior(
            abstract_summary, design_temperature, images
        )

        # Code Phase
        status.content = "(5/7) *Generating `compute_centers`...*"
        progress.value = 60
        centers_code = ""
        while True:
            centers_code = generate_centers_code(
                centers_behavior, duration, code_temperature, images
            )
            if self._is_working_centers_code(centers_code):
                break

        status.content = "(6/7) *Generating `compute_rgbs`...*"
        progress.value = 72
        rgbs_code = ""
        while True:
            rgbs_code = generate_rgbs_code(
                rgbs_behavior, duration, code_temperature, images
            )
            if self._is_working_rgbs_code(rgbs_code):
                break

        status.content = "(7/7) *Generating `compute_opacities`...*"
        progress.value = 85
        opacities_code = ""
        while True:
            opacities_code = generate_opacities_code(
                opacities_behavior, duration, code_temperature, images
            )
            if self._is_working_opacities_code(opacities_code):
                break

        progress.remove()
        status.remove()

        return Animation(
            title,
            description,
            duration,
            abstract_summary,
            centers_behavior,
            rgbs_behavior,
            opacities_behavior,
            centers_code,
            rgbs_code,
            opacities_code,
        )

    def _render_vision_angles(self) -> list[str]:
        angles = self.config.vision_angles
        renderer = Renderer(self.client, self.gui_api, self.state)
        angle_images_dir = f"render/{self.subdirectory}/vision_angles"
        angle_images = renderer.render_angles(angles, angle_images_dir)
        return angle_images

    def _score_animation(self, animation: Animation, image_dir: str) -> int:
        self.state.active_animation = animation
        time.sleep(1)
        self.state.visible_frame = 0
        time.sleep(1)
        renderer = Renderer(self.client, self.gui_api, self.state)
        first_frames = renderer.render_first_frames(image_dir)
        score = generate_animation_score(first_frames, animation.description)
        return score

    def _is_working_centers_code(self, centers_code: str) -> bool:
        try:
            self.state.active_animation = Animation(duration=self.config.animation_duration, centers_code=centers_code)
        except Exception:
            return False
        return True

    def _is_working_rgbs_code(self, rgbs_code: str) -> bool:
        try:
            self.state.active_animation = Animation(duration=self.config.animation_duration, rgbs_code=rgbs_code)
        except Exception:
            return False
        return True

    def _is_working_opacities_code(self, opacities_code: str) -> bool:
        try:
            self.state.active_animation = Animation(duration=self.config.animation_duration, opacities_code=opacities_code)
        except Exception:
            return False
        return True
