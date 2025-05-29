import time

from animation import Animation, VisionAngle
from examples import EXAMPLE_ACCELERATION, EXAMPLE_BREATHING, EXAMPLE_COLOR_SHIFT, EXAMPLE_EXPLOSION, EXAMPLE_LAVA_MELTING, EXAMPLE_LSD
from generator import Generator, GeneratorConfig
from renderer import Renderer
from scene import Scene
from src import viser
from src.viser._gui_api import GuiApi
from src.viser._viser import ViserServer
from state import Observer, State
from text_utils import (
    build_function_inspector_markdown,
)
from viser._gui_handles import GuiModalHandle


class Gui(Observer):
    def __init__(self, server: ViserServer, state: State, scene: Scene):
        self.state: State = state
        self.server: ViserServer = server
        self.api: GuiApi = server.gui
        self.scene: Scene = scene
        self.generator: Generator | None = None

        # Set Dark Mode
        self.api.configure_theme(dark_mode=True, show_logo=False)

        # Add Gui Elements
        self.tab_group = self.api.add_tab_group()
        ## Animation Tab
        with self.tab_group.add_tab("Animation"):
            self.title_md = self.api.add_markdown("Title: **N/A**")

            self.duration_md = self.api.add_markdown("Duration: **N/A**")

            self.generator_btn = self.api.add_button(label="♻ New Animation")
            self.generator_btn.on_click(lambda _: self._open_generator())

            self.improve_btn = self.api.add_button(
                label="⇪ Improve Current",
                disabled=True,
            )
            self.improve_btn.on_click(lambda _: self._open_improve_menu())

            self.details_btn = self.api.add_button(
                "Details",
                icon=viser.Icon.LIST_DETAILS,
                disabled=True,
            )
            self.details_btn.on_click(lambda _: self._open_details())

            self.examples_btn = self.api.add_button(
                "Examples",
                icon=viser.Icon.FOLDER_OPEN,
            )
            self.examples_btn.on_click(lambda _: self._open_examples())

            self.fps_btn_grp = self.api.add_button_group(
                f"FPS ({self.state.fps})", ["8", "24", "50"]
            )
            self.fps_btn_grp.on_click(lambda _: self._sync_fps())

            self.speed_btn_grp = self.api.add_button_group(
                label=f"Speed ({self.state.speed})",
                options=[".25x", ".5x", "1x", "2x"],
            )
            self.speed_btn_grp.on_click(lambda _: self._sync_speed())

            self.frame_slider = self.api.add_slider(
                label="Frame",
                min=0,
                max=self.state.total_frames - 1,
                step=1,
                initial_value=0,
            )
            self.frame_slider.on_update(lambda _: self._sync_frame())

            self.play_btn = server.gui.add_button(
                "Play", color="green", icon=viser.Icon.PLAYER_PLAY
            )
            self.play_btn.on_click(lambda _: self._start_playback())

            self.stop_btn = self.api.add_button(
                "Stop", color="red", visible=False, icon=viser.Icon.PLAYER_STOP
            )
            self.stop_btn.on_click(lambda _: self._stop_playback())
        ## Scene Tab
        with self.tab_group.add_tab("Scene"):
            self.world_axis_cbox = self.api.add_checkbox(
                "World Axis", initial_value=False
            )

            @self.world_axis_cbox.on_update
            def _(_) -> None:
                self.scene.api.world_axes.visible = self.world_axis_cbox.value

            self.background_cbox = self.api.add_checkbox(
                "Background", initial_value=True
            )

            @self.background_cbox.on_update
            def _(_) -> None:
                self.state.background_visible = self.background_cbox.value

            with self.api.add_folder("Example Scenes"):
                self.api.add_button("Bear").on_click(lambda _: self.state.load_bear())
                self.api.add_button("Bulldozer").on_click(
                    lambda _: self.state.load_bulldozer()
                )
                self.api.add_button("Horse").on_click(lambda _: self.state.load_horse())
                self.api.add_button("Vase").on_click(lambda _: self.state.load_vase())
        ## Render Tab
        with self.tab_group.add_tab("Render"):
            self.render_btn = self.api.add_button("Render", icon=viser.Icon.PHOTO)
            self.render_btn.on_click(lambda event: self._render(event))

    def update(self, changed_attribute_name: str):
        match changed_attribute_name:
            case "animation":
                title = self.state.active_animation.title
                self.title_md.content = f"Title: **{title}**"
                duration = self.state.active_animation.duration
                self.duration_md.content = f"Duration: **{duration}s**"
                max_frame = self.state.total_frames - 1
                self.frame_slider.max = max_frame
            case "fps":
                fps = self.state.fps
                self.fps_btn_grp.label = f"FPS ({fps})"
                max_frame = self.state.total_frames - 1
                self.frame_slider.max = max_frame
            case "speed":
                speed = self.state.speed
                self.speed_btn_grp.label = f"Speed ({speed})"

    def _open_generator(self):
        with self.api.add_modal(title="♻ New Animation") as popout:
            title_txt = self.api.add_text("Title", initial_value="")
            description_txt = self.api.add_text("Description", "")
            duration_slider = self.api.add_slider(
                label="Duration",
                min=1,
                max=10,
                step=1,
                initial_value=1,
            )

            with self.api.add_folder("🔥"):
                design_temperature_slider = self.api.add_slider(
                    label="Design Temperature",
                    min=0.00,
                    max=2.00,
                    step=0.01,
                    initial_value=1.0,
                )
                coding_temperature_slider = self.api.add_slider(
                    label="Code Temperature",
                    min=0.00,
                    max=2.00,
                    step=0.01,
                    initial_value=1.0,
                )

            with self.api.add_folder("👁️"):
                vision_angles_dropdown = self.api.add_dropdown(
                    "Vision",
                    options=["none", "front-left", "front + back + sides", "all"],
                    initial_value="none",
                )
                auto_sample_number = self.api.add_number("Auto Samples", 1, min=1)

            generate_btn = self.api.add_button("🛠 Generate")

            @generate_btn.on_click
            def _(event: viser.GuiEvent) -> None:
                client = event.client
                assert client is not None

                if not description_txt.value:
                    client.add_notification("⚠", "Empty Description", auto_close=True, color="yellow")
                    return

                popout.close()
                generator_config = GeneratorConfig(
                    animation_title=title_txt.value,
                    animation_description=description_txt.value,
                    animation_duration=duration_slider.value,
                    design_temperature=design_temperature_slider.value,
                    code_temperature=coding_temperature_slider.value,
                    vision_angles=self._vision_angles_from_dropdown(
                        vision_angles_dropdown.value
                    ),
                    n_samples=auto_sample_number.value,
                )
                generator = Generator(generator_config, client, self.api, self.state)
                generator.auto_sample()

                self.generator = generator
                self.state.animation_evolution = generator.output
                self.state.active_animation = generator.output.final_animation

                self.improve_btn.disabled = False
                self.details_btn.disabled = False

            self._add_close_popout_btn(popout)

    def _open_improve_menu(self) -> None:
        with self.api.add_modal("") as popout:
            auto_improve_btn = self.api.add_button("Auto Improve", icon=viser.Icon.BRAIN)

            @auto_improve_btn.on_click
            def _(_) -> None:
                popout.close()
                assert self.generator is not None
                self.generator.auto_improve()
                self.state.active_animation = self.generator.output.final_animation

            feedback_btn = self.api.add_button("Feedback Improve", icon=viser.Icon.WRITING)

            @feedback_btn.on_click
            def _(_) -> None:
                popout.close()
                self._open_feedback()

            self._add_close_popout_btn(popout)

    def _open_feedback(self):
        with self.api.add_modal("") as popout:
            input_txt = self.api.add_text("Feedback", "")
            improve_btn = self.api.add_button("⮞ Submit")

            @improve_btn.on_click
            def _(event: viser.GuiEvent) -> None:
                if not input_txt.value:
                    assert event.client is not None
                    event.client.add_notification("⚠", "Empty Feedback", auto_close=True, color="yellow")
                    return
                assert self.generator is not None
                popout.close()
                self.generator.feedback_improve(input_txt.value)
                self.state.active_animation = self.generator.output.final_animation

            self._add_close_popout_btn(popout)

    def _open_details(self):
        def change_and_close(animation: Animation, popout: GuiModalHandle):
            popout.close()
            self.state.active_animation = animation

        with self.api.add_modal("") as popout:
            with self.api.add_folder("Animation Evolution"):
                for idx, animation in enumerate(
                    self.state.animation_evolution.auto_sampled_animations
                ):
                    self.api.add_button(f"Sample {idx+1}").on_click(
                        lambda _, anim=animation: change_and_close(anim, popout)
                    )
                for idx, animation in enumerate(
                    self.state.animation_evolution.auto_improved_animations
                ):
                    self.api.add_button(f"Auto-Improve {idx+1}").on_click(
                        lambda _, anim=animation: change_and_close(anim, popout)
                    )
                for idx, animation in enumerate(
                    self.state.animation_evolution.feedback_to_animation.values()
                ):
                    self.api.add_button(f"Feedback-Improve {idx+1}").on_click(
                        lambda _, anim=animation: change_and_close(anim, popout)
                    )

            functions_btn = self.api.add_button(
                "Active Functions", icon=viser.Icon.FUNCTION
            )

            @functions_btn.on_click
            def _(_) -> None:
                popout.close()
                self._open_active_functions()

            self._add_close_popout_btn(popout)

    def _open_examples(self) -> None:
        with self.api.add_modal("") as popout:

            explosion_btn = self.api.add_button(
                "💥 Example Explosion (1s)"
            )

            @explosion_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_EXPLOSION

            lsd_btn = self.api.add_button(
                "💮 Example LSD (1s)"
            )

            @lsd_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_LSD

            acceleration_btn = self.api.add_button(
                "🚕 Example Acceleration (2s)"
            )

            @acceleration_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_ACCELERATION

            breathing_btn = self.api.add_button(
                "🌬️ Example Breathing (3s)"
            )

            @breathing_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_BREATHING

            color_shift_btn = self.api.add_button(
                "🌈 Example Color Shift (4s)"
            )

            @color_shift_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_COLOR_SHIFT

            lava_melting_btn = self.api.add_button(
                "🌋 Example Lava Melting (5s)"
            )

            @lava_melting_btn.on_click
            def _(_) -> None:
                popout.close()
                self.state.active_animation = EXAMPLE_LAVA_MELTING

            self._add_close_popout_btn(popout)

    def _sync_fps(self):
        self._stop_playback()
        self.state.fps = int(self.fps_btn_grp.value)

    def _sync_speed(self):
        self.state.speed = float(self.speed_btn_grp.value[:-1])

    def _sync_frame(self):
        self.state.visible_frame = self.frame_slider.value

    def _start_playback(self):
        self.play_btn.disabled = True
        self.stop_btn.visible = True
        self.state.playing = True
        while self.state.playing:
            frame = int(self.frame_slider.value)
            min_frame = int(self.frame_slider.min)
            max_frame = int(self.frame_slider.max)
            if frame == max_frame:
                self.frame_slider.value = min_frame
            else:
                self.frame_slider.value = frame + 1
            sleep_factor = 1 / self.state.speed
            seconds_per_frame = sleep_factor / self.state.fps
            time.sleep(seconds_per_frame)
        self.play_btn.disabled = False

    def _stop_playback(self):
        self.stop_btn.visible = False
        self.play_btn.disabled = False
        self.state.playing = False
        self.frame_slider.value = 0

    def _render(self, event: viser.GuiEvent):
        client = event.client
        assert client is not None
        renderer = Renderer(client, self.api, self.state)
        renderer.render_animation()

    def _open_active_functions(self):
        centers_code = self.state.active_animation.centers_code
        rgbs_code = self.state.active_animation.rgbs_code
        opacities_code = self.state.active_animation.opacities_code
        markdown = build_function_inspector_markdown(
            centers_code, rgbs_code, opacities_code
        )

        with self.api.add_modal("") as popout:
            self.api.add_markdown(markdown)
            self._add_close_popout_btn(popout)

    def _vision_angles_from_dropdown(self, dropdown_value: str) -> list[VisionAngle]:
        match dropdown_value:
            case "front-left":
                return ["front-left"]
            case "front + back + sides":
                return ["front", "back", "left", "right"]
            case "all":
                return [
                    "front",
                    "front-left",
                    "left",
                    "back-left",
                    "back",
                    "back-right",
                    "right",
                    "front-right",
                ]
            case _:
                return []

    def _add_close_popout_btn(self, popout: GuiModalHandle) -> None:
        close_btn = self.api.add_button("", color="red", icon=viser.Icon.X)
        close_btn.on_click(lambda _: popout.close())
