import mujoco

from mujoco_clisim.common import (
    Command,
    GetData,
    GetDataIdx,
    SetData,
    SetDataIdx,
)


def qpos_commands(data: mujoco.MjData) -> list[Command]:
    return [
        GetData(data, "qpos"),
        GetDataIdx(data, "qpos"),
        SetData(data, "qpos"),
        SetDataIdx(data, "qpos"),
    ]
