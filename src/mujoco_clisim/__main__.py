import os
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue

import fire
import mujoco
import mujoco.viewer
from pyfun import Maybe, Some, maybe, wrap_exc

from mujoco_clisim.command_runner import CommandRunner

FPS = 60


def run_ui(q: Queue) -> None:
    try:
        while True:
            cmd = input("> ")
            q.put(cmd)
            q.join()
    except EOFError, KeyboardInterrupt:
        q.put("q")


def main(robotfile: str) -> None:
    fullpath = Path(robotfile).resolve()
    assert fullpath.exists()

    q = Queue()
    queue_read = wrap_exc(q.get, Empty)
    threading.Thread(target=run_ui, args=(q,), daemon=True).start()

    model = mujoco.MjModel.from_xml_path(str(fullpath))
    data = mujoco.MjData(model)

    cmd_runner = CommandRunner(model, data)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        is_paused = False
        sim_start, real_start, num_frames = data.time, time.perf_counter(), 0
        cmd: Maybe[str] = maybe(None)

        while viewer.is_running():
            if is_paused:
                cmd = queue_read()
            else:
                mujoco.mj_step(model, data)
                sim_elapsed = data.time - sim_start
                if (lag := sim_elapsed - (time.perf_counter() - real_start)) > 0:
                    time.sleep(lag)
                cmd = queue_read(block=False)
                if num_frames < sim_elapsed * FPS:
                    num_frames += 1
                    viewer.sync()

            match cmd.map(str.strip).map(str.lower):
                case Some(command):
                    match command:
                        case "p" if not is_paused:
                            is_paused = True
                        case "r" if is_paused:
                            is_paused = False
                            sim_start, real_start = data.time, time.perf_counter()
                            num_frames = 0
                        case "help":
                            cmd_runner.help()
                        case "q":
                            break
                        case "p" | "r":
                            pass
                        case other:
                            cmd_runner.run(other)
                    q.task_done()
                case _:
                    pass


_REEXEC_GUARD = "MUJOCO_CLISIM_REEXEC"


def _ensure_mjpython() -> None:
    """On macOS the passive viewer only works under mjpython, so re-run there."""
    if sys.platform != "darwin" or mujoco.viewer._MJPYTHON is not None:
        return
    if os.environ.get(_REEXEC_GUARD):
        sys.exit("error: could not start under mjpython")
    mjpython = Path(sys.executable).with_name("mjpython")
    if not mjpython.exists():
        sys.exit(f"error: {mjpython} not found; reinstall mujoco")
    os.environ[_REEXEC_GUARD] = "1"
    os.execv(mjpython, [str(mjpython), "-m", "mujoco_clisim", *sys.argv[1:]])


def cli() -> None:
    _ensure_mjpython()
    try:
        print("CLISIM version 1.0")
        fire.Fire(main)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
