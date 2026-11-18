from typing import override

import mujoco

from mujoco_clisim.common import Command, GetData, GetDataIdx, SetData, SetDataIdx


class GetQfrc(GetData):
    def __init__(self, data: mujoco.MjData) -> None:
        super().__init__(data, attr="", cmd="qfrc")

    @override
    def run(self) -> None:
        net_force = self._data.qfrc_smooth + self._data.qfrc_constraint
        print(net_force)


def force_commands(data: mujoco.MjData) -> list[Command]:
    return [
        GetData(data, "qfrc_actuator"),
        GetDataIdx(data, "qfrc_actuator"),
        GetData(data, "qfrc_passive"),
        GetDataIdx(data, "qfrc_passive"),
        GetData(data, "qfrc_applied"),
        GetDataIdx(data, "qfrc_applied"),
        SetData(data, "qfrc_applied"),
        SetDataIdx(data, "qfrc_applied"),
        GetData(data, "qfrc_bias"),
        GetDataIdx(data, "qfrc_bias"),
        GetData(data, "qfrc_smooth"),
        GetDataIdx(data, "qfrc_smooth"),
        GetData(data, "qfrc_constraint"),
        GetDataIdx(data, "qfrc_constraint"),
        GetQfrc(data),
    ]
