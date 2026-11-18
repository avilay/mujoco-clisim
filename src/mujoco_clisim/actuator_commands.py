import mujoco

from mujoco_clisim.common import Command, GetData, GetDataIdx, SetData, SetDataIdx


def actuator_commands(data: mujoco.MjData) -> list[Command]:
    return [
        GetData(data, "ctrl"),
        GetDataIdx(data, "ctrl"),
        SetData(data, "ctrl"),
        SetDataIdx(data, "ctrl"),
        GetData(data, "actuator_length"),
        GetDataIdx(data, "actuator_length"),
        GetData(data, "actuator_velocity"),
        GetDataIdx(data, "actuator_velocity"),
        GetData(data, "actuator_force"),
        GetDataIdx(data, "actuator_force"),
    ]
