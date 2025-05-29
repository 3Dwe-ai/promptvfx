"""WebGL-based Gaussian splat rendering. This is still under developmentt."""

from __future__ import annotations

import time

import tyro

from animation import write_animation_functions
from gui import Gui
from scene import Scene
from src import viser
from state import State


def main() -> None:
    server = viser.ViserServer()
    scene = Scene(server.scene)
    state = State(scene, server.gui)
    gui = Gui(server, state, scene)
    state.attach(gui)

    try:
        while True:
            time.sleep(10.0)
    finally:
        state.remove_gs_handles()
        write_animation_functions()


if __name__ == "__main__":
    tyro.cli(main)
