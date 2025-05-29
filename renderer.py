import base64
import os
import time

import imageio
import numpy as np

import src.viser.transforms as tf
from animation import VisionAngle
from state import State
from text_utils import snake_case
from viser import ClientHandle, GuiApi

angle_to_wxyz: dict[VisionAngle, np.ndarray] = {
    "front": np.array(
        (
            -0.36265065445334876,
            0.6108337481676532,
            0.6051993021378332,
            -0.35930549622277347,
        ),
        dtype=np.float64,
    ),
    "front-left": np.array(
        (
            -0.19225236907057855,
            0.32382193097241246,
            0.7965697836536122,
            -0.47292173071036364,
        ),
        dtype=np.float64,
    ),
    "left": np.array(
        (
            -0.000585919369139853,
            0.0009868983275798675,
            0.8598738798453849,
            -0.5105052335577261,
        ),
        dtype=np.float64,
    ),
    "back-left": np.array(
        (
            0.2121473625128815,
            -0.35733223424885696,
            0.7821110775173719,
            -0.4643376286390795,
        ),
        dtype=np.float64,
    ),
    "back": np.array(
        (
            0.3562054170310423,
            -0.5999776570944623,
            0.6159633708233828,
            -0.36569610015568493,
        ),
        dtype=np.float64,
    ),
    "back-right": np.array(
        (
            -0.4652921560875437,
            0.7837188440329271,
            -0.3537920811950952,
            0.21004558142160615,
        ),
        dtype=np.float64,
    ),
    "right": np.array(
        (
            0.5105032759584313,
            -0.8598705825461803,
            -0.0025776889566837473,
            0.001530368271109303,
        ),
        dtype=np.float64,
    ),
    "front-right": np.array(
        (
            -0.47432806819048334,
            0.7989385602809844,
            0.31793276035163853,
            -0.18875598140991362,
        ),
        dtype=np.float64,
    ),
}


angle_to_position: dict[VisionAngle, np.ndarray] = {
    "front": np.array(
        (2.875022217052737, -0.02664319904713948, 1.567904330328208), dtype=np.float64
    ),
    "front-left": np.array(
        (2.0060873966827777, 2.0596300556212106, 1.567904330379932), dtype=np.float64
    ),
    "left": np.array(
        (0.006599741612243951, 2.875138092780652, 1.5679043303799316), dtype=np.float64
    ),
    "back-left": np.array(
        (-2.1735037556652226, 1.882111588949201, 1.5679043303799316), dtype=np.float64
    ),
    "back": np.array(
        (-2.8741519708057517, 0.07558477268025747, 1.567904330379932), dtype=np.float64
    ),
    "back-right": np.array(
        (-2.156394225933029, -1.9016904457640853, 1.5679043303799325), dtype=np.float64
    ),
    "right": np.array(
        (0.017237860639105432, -2.8750939924302124, 1.567904330379933), dtype=np.float64
    ),
    "front-right": np.array(
        (1.9754608460919139, -2.089022990468399, 1.567904330379933), dtype=np.float64
    ),
}

SLEEP = 1


class Renderer:
    def __init__(self, client: ClientHandle, gui_api: GuiApi, state: State):
        self.client = client
        self.gui_api = gui_api
        self.state = state

    def render_animation(self) -> None:
        status = self.gui_api.add_markdown("*Saving Frames...*")
        progress = self.gui_api.add_progress_bar(10, animated=True)
        fps = 24
        self.state.fps = fps
        rendered_images: list[np.ndarray] = []
        # Start at front angle
        self._set_camera_angle("front")
        self.state.visible_frame = 0
        time.sleep(SLEEP)
        rendered_images.append(self.client.get_render(height=1080, width=1920))
        # Move through remaining angles
        wxyzs = list(angle_to_wxyz.values())
        positions = list(angle_to_position.values())
        steps_per_move = int(1.25 * fps)
        for wxyz, position in zip(wxyzs[1:], positions[1:]):
            for _ in self._move_camera(wxyz, position, steps_per_move):
                self.state.next_frame()
                time.sleep(SLEEP)
                rendered_images.append(self.client.get_render(height=1080, width=1920))
            progress.value += 10
        # Move back to front angle
        for _ in self._move_camera(wxyzs[0], positions[0], steps_per_move):
            self.state.next_frame()
            time.sleep(SLEEP)
            rendered_images.append(self.client.get_render(height=1080, width=1920))
        # Write images to disk
        status.content = "*Writing JPGs...*"
        progress.value += 10
        animation = self.state.active_animation
        subdirectory = render_subdirectory(animation.title, animation.duration)
        output_dir = f"render/{subdirectory}/final/{fps}"
        self._write_images(images=rendered_images, output_dir=output_dir)
        progress.remove()
        status.remove()

    def render_angles(self, angles: list[VisionAngle], output_dir: str) -> list[str]:
        "Returns base64 encoded images from the provided angles."
        renders = []
        for angle in angles:
            self._set_camera_angle(angle)
            time.sleep(SLEEP)
            rgb_array = self.client.get_render(height=1080, width=1920)
            image_path = f"{output_dir}/{angle}.jpg"
            self._write_image(rgb_array, image_path)
            render = self._base64_encode_image(image_path)
            renders.append(render)
        return renders

    def render_first_frames(self, image_dir: str) -> list[str]:
        "Returns base64 encoded renders of the first n animation frames."
        first_frames = []
        self.state.fps = 8
        self._set_camera_angle("front-left")
        n_frames = self.state.active_animation.duration * 8
        for i in range(n_frames):
            self.state.visible_frame = i
            self.client.flush()
            time.sleep(SLEEP)
            image = self.client.get_render(height=1080, width=1920)
            image_path = image_dir + f"/img_{i}.jpg"
            self._write_image(image, image_path)
            base64_image = self._base64_encode_image(image_path)
            first_frames.append(base64_image)
        self.state.visible_frame = 0
        return first_frames

    def _move_camera(self, wxyz: np.ndarray, position: np.ndarray, steps: int):
        T_world_current = tf.SE3.from_rotation_and_translation(
            tf.SO3(self.client.camera.wxyz), self.client.camera.position
        )
        T_world_target = tf.SE3.from_rotation_and_translation(
            tf.SO3(wxyz), position
        ) @ tf.SE3.from_translation(np.array([0.0, 0.0, -0.5]))
        T_current_target = T_world_current.inverse() @ T_world_target
        for j in range(1, steps):
            T_world_set = T_world_current @ tf.SE3.exp(
                T_current_target.log() * j / (steps - 1.0)
            )
            with self.client.atomic():
                self.client.camera.wxyz = T_world_set.rotation().wxyz
                self.client.camera.position = T_world_set.translation()
            self.client.flush()
            yield

    def _set_camera_angle(self, angle: VisionAngle) -> None:
        wxyz = angle_to_wxyz[angle]
        position = angle_to_position[angle]
        starting_target = tf.SE3.from_rotation_and_translation(
            tf.SO3(wxyz), position
        ) @ tf.SE3.from_translation(np.array([0.0, 0.0, -0.5]))
        with self.client.atomic():
            self.client.camera.wxyz = starting_target.rotation().wxyz
            self.client.camera.position = starting_target.translation()

    def _base64_encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _write_images(self, images, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        for idx, image in enumerate(images):
            imageio.imwrite(f"{output_dir}/img_{idx}.jpg", image)

    def _write_image(self, image: np.ndarray, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        imageio.imwrite(path, image)


def render_subdirectory(animation_title: str, animation_duration: int) -> str:
    return f"{snake_case(animation_title)}_{animation_duration}s"
