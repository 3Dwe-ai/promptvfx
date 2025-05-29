import uuid

import numpy as np

from splat_utils import SplatFile
from viser._scene_api import SceneApi
from viser._scene_handles import GaussianSplatHandle


class Scene:
    def __init__(self, scene_api: SceneApi):
        self.api: SceneApi = scene_api

        # Black background images, because else renders use a white skybox
        self._add_black_box()
        # Make Axis Bigger
        self.api.world_axes.axes_length = 1.0
        self.api.world_axes.axes_radius = 0.01

    def add_splat(
        self,
        name: str,
        splat: SplatFile,
        position: tuple[float, float, float] = (0, 0, 0),
    ) -> GaussianSplatHandle:
        return self.api.add_gaussian_splats(
            name=name + "_" + str(uuid.uuid4()),
            centers=splat["centers"],
            rgbs=splat["rgbs"],
            opacities=splat["opacities"],
            covariances=splat["covariances"],
            position=position,
        )

    def _add_black_box(self) -> None:
        black_image = np.zeros((1, 1, 3), dtype=np.uint8)
        self.api.add_image(
            "black_box_floor",
            black_image,
            render_width=100.0,
            render_height=100.0,
            position=(0, 0, -25),
        )
        self.api.add_image(
            "black_box_front",
            black_image,
            render_width=50.0,
            render_height=100.0,
            position=(50, 0, 0),
            wxyz=(0.7071, 0, 0.7071, 0),
        )
        self.api.add_image(
            "black_box_back",
            black_image,
            render_width=50.0,
            render_height=100.0,
            position=(-50, 0, 0),
            wxyz=(0.7071, 0, 0.7071, 0),
        )
        self.api.add_image(
            "black_box_right",
            black_image,
            render_width=100.0,
            render_height=50.0,
            position=(0, 50, 0),
            wxyz=(0.7071, 0.7071, 0, 0),
        )
        self.api.add_image(
            "black_box_left",
            black_image,
            render_width=100.0,
            render_height=50.0,
            position=(0, -50, 0),
            wxyz=(0.7071, 0.7071, 0, 0),
        )
