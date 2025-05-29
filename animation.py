import importlib
import sys
from dataclasses import dataclass, field
from types import ModuleType
from typing import Literal

VisionAngle = Literal[
    "front",
    "front-left",
    "left",
    "back-left",
    "back",
    "back-right",
    "right",
    "front-right",
]

DEFAULT_CENTERS_CODE = """
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    return centers.copy()
""".strip()

DEFAULT_RGBS_CODE = """
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    return rgbs.copy()
""".strip()

DEFAULT_OPACITIES_CODE = """
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    return opacities.copy()
""".strip()


@dataclass
class Animation:
    title: str = ""
    description: str = ""
    duration: int = 1
    abstract_summary: str = ""
    centers_behavior: str = ""
    rgbs_behavior: str = ""
    opacities_behavior: str = ""
    centers_code: str = DEFAULT_CENTERS_CODE
    rgbs_code: str = DEFAULT_RGBS_CODE
    opacities_code: str = DEFAULT_OPACITIES_CODE
    score: int = -1


@dataclass
class AnimationEvolution:
    auto_sampled_animations: list[Animation] = field(default_factory=list)
    auto_improved_animations: list[Animation] = field(default_factory=list)
    feedback_to_animation: dict[str, Animation] = field(default_factory=dict)
    final_animation: Animation = field(default_factory=Animation)


def write_animation_functions(animation: Animation = Animation()) -> None:
    centers_code = animation.centers_code
    rgbs_code = animation.rgbs_code
    opacities_code = animation.opacities_code
    with open("animation_functions.py", "w") as file:
        file.write("import numpy as np")
        file.write("\n\n\n")
        file.write(centers_code)
        file.write("\n\n")
        file.write(rgbs_code)
        file.write("\n\n")
        file.write(opacities_code)
        file.write("\n")


def import_animation_functions() -> ModuleType:
    if "animation_functions" in sys.modules:
        del sys.modules["animation_functions"]
    return importlib.import_module("animation_functions")
