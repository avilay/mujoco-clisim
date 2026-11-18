import time
from pathlib import Path

import fire
import mujoco
import mujoco.viewer
import numpy as np


def main(robot: str):
    if robot in ("arm-2", "arm-3"):
        xmlfile = Path(__file__).resolve().parent / f"{robot}.xml"
    else:
        raise ValueError(f"Unrecognized robot {robot}!")

    model = mujoco.MjModel.from_xml_path(str(xmlfile))
    data = mujoco.MjData(model)

    key_id = model.keyframe("diagram_pose").id
    mujoco.mj_resetDataKeyframe(model, data, key_id)

    cam_id = model.camera("xy_plane_view").id

    with mujoco.viewer.launch_passive(model, data) as viewer:
        # Switch viewer camera to the fixed camera
        with viewer.lock():
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
            viewer.cam.fixedcamid = cam_id

        while viewer.is_running():
            step_start = time.perf_counter()
            mujoco.mj_step(model, data)
            viewer.sync()

            # Run the sim time step

            elapsed = time.perf_counter() - step_start
            if elapsed < model.opt.timestep:
                time.sleep(model.opt.timestep - elapsed)


if __name__ == "__main__":
    fire.Fire(main)
