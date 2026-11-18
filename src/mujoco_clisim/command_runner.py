import mujoco
from pyfun import Iter

from mujoco_clisim.actuator_commands import actuator_commands
from mujoco_clisim.common import Command, Unknown
from mujoco_clisim.force_commands import force_commands
from mujoco_clisim.qpos_commands import qpos_commands


class CommandRunner:
    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        self._model = model
        self._data = data
        self._cmds: list[Command] = []

        self._cmds += qpos_commands(data)
        self._cmds += force_commands(data)
        self._cmds += actuator_commands(data)

        self._cmds.append(Unknown())

    def help(self) -> None:
        for cmd in self._cmds[:-1]:
            print(cmd.help())

    def run(self, command: str) -> None:
        Iter(self._cmds).find(lambda cmd: cmd.is_match(command)).map(
            lambda cmd: cmd.run()
        )
