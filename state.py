from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from weakref import WeakSet

from animation import (
    Animation,
    AnimationEvolution,
    import_animation_functions,
    write_animation_functions,
)
from scene import Scene
from splat_utils import SplatFile, compute_splat_at_t, load_splat
from src.viser._scene_handles import GaussianSplatHandle
from viser import GuiApi


class Observer(ABC):
    @abstractmethod
    def update(self, changed_attribute_name: str):
        pass


class Subject:
    def __init__(self):
        self._observers: WeakSet[Observer] = WeakSet()

    def attach(self, observer: Observer) -> None:
        self._observers.add(observer)

    def notify(self, changed_attribute: str) -> None:
        for observer in self._observers:
            observer.update(changed_attribute)


class State(Subject):
    def __init__(self, scene: Scene, gui_api: GuiApi):
        super().__init__()

        self.gui_api = gui_api
        self.scene = scene

        self._object_data: SplatFile
        self._fps: int = 8
        self._speed: float = 1.0
        self._visible_frame: int = 0
        self._background_visible: bool = True
        self._active_animation: Animation = Animation()
        self.animation_evolution = AnimationEvolution()
        self.frame_to_handle: dict[int, GaussianSplatHandle] = {}
        self.background_handle: GaussianSplatHandle | None = None
        self.playing: bool = False

        write_animation_functions(self.active_animation)
        self.load_vase()

    @property
    def object_data(self) -> SplatFile:
        return self._object_data

    @object_data.setter
    def object_data(self, value: SplatFile) -> None:
        self._object_data = value
        self._reload_splats()

    @property
    def active_animation(self) -> Animation:
        return self._active_animation

    @active_animation.setter
    def active_animation(self, animation: Animation) -> None:
        self._active_animation = animation
        self._reload_splats()
        self.notify("animation")

    @property
    def visible_frame(self) -> int:
        return self._visible_frame

    @visible_frame.setter
    def visible_frame(self, value: int) -> None:
        wrapped_value = value % self.total_frames
        self.frame_to_handle[self.visible_frame].visible = False
        self.frame_to_handle[wrapped_value].visible = True
        self._visible_frame = wrapped_value

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int) -> None:
        self._fps = value
        self._reload_splats()
        self.notify("fps")

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        self._speed = value
        self.notify("speed")

    @property
    def total_frames(self) -> int:
        return self.fps * self.active_animation.duration

    @property
    def background_visible(self) -> bool:
        return self._background_visible

    @background_visible.setter
    def background_visible(self, value: bool) -> None:
        self._background_visible = value
        if self.background_handle:
            self.background_handle.visible = value

    def remove_gs_handles(self) -> None:
        for gs_handle in self.frame_to_handle.values():
            if gs_handle:
                gs_handle.remove()
        self.frame_to_handle.clear()

    def next_frame(self):
        max_frame = self.total_frames - 1
        if self.visible_frame == max_frame:
            self.visible_frame = 0
        else:
            self.visible_frame = self.visible_frame + 1

    def load_vase(self) -> None:
        self._load_scene(
            Path("data/objects/vase.splat"),
            Path("data/backgrounds/vase_bg.splat"),
            (-0.39, 0.04, -1.33),
        )

    def load_bulldozer(self) -> None:
        self._load_scene(
            Path("data/objects/bulldozer.splat"),
            Path("data/backgrounds/bulldozer_bg.splat"),
            (-0.05, 0.3, -0.48),
        )

    def load_bear(self) -> None:
        self._load_scene(
            Path("data/objects/bear.splat"),
            Path("data/backgrounds/bear_bg.splat"),
            (-2.23, 0.36, -0.16),
        )

    def load_horse(self) -> None:
        self._load_scene(
            Path("data/objects/horse.splat"),
            Path("data/backgrounds/horse_bg.splat"),
            (-0.82, -2.375, 0.785),
        )

    def _reload_splats(self) -> None:
        self.remove_gs_handles()
        write_animation_functions(self.active_animation)
        self._add_animation_splats()
        self.visible_frame = 0

    def _add_animation_splats(self) -> None:
        splat = self.object_data
        assert splat is not None

        loading_md = self.gui_api.add_markdown("*Loading Frames...*")
        progress_bar = self.gui_api.add_progress_bar(0.0, animated=True)

        animation_functions = import_animation_functions()
        seconds_per_frame = 1.0 / self.fps
        try:
            for frame in range(self.total_frames):
                t = frame * seconds_per_frame
                splat_at_t = compute_splat_at_t(t, splat, animation_functions)
                gs_handle = self.scene.add_splat(f"splat_at_{t}", splat_at_t)
                gs_handle.visible = frame == self.visible_frame
                self.frame_to_handle[frame] = gs_handle
                progress_bar.value = ((frame + 1) / self.fps) * 100
        except Exception:
            progress_bar.remove()
            loading_md.remove()
            raise

        progress_bar.remove()
        loading_md.remove()

    def _load_scene(
        self, obj_path: Path, bg_path: Path, bg_position: tuple[float, float, float]
    ) -> None:
        if self.background_handle:
            self.background_handle.remove()

        status = self.gui_api.add_markdown("*Loading Background...*")
        progress = self.gui_api.add_progress_bar(33, animated=True)
        bg_data = load_splat(bg_path)
        progress.value = 66
        self.background_handle = self.scene.add_splat(
            "splat_background", bg_data, bg_position
        )
        self.background_handle.visible = self.background_visible
        progress.remove()
        status.remove()

        self.object_data = load_splat(obj_path)
