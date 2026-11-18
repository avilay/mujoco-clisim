# mujoco-clisim

A command line simulator for MuJoCo. It loads a MuJoCo model (MJCF XML file), runs it in real time in the MuJoCo viewer, and gives you a `>` prompt in the terminal where you can pause, resume, inspect and change the simulation while it runs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for managing Python and dependencies.
- Python 3.14. uv installs it for you if you don't have it (the version is pinned in `.python-version`).
- A machine with a display, since the tool opens the MuJoCo viewer window.

## Setup

Clone the repository and install the dependencies:

```sh
git clone https://github.com/avilay/mujoco-clisim.git
cd mujoco-clisim
uv sync
```

`uv sync` creates a virtual environment in `.venv` and installs MuJoCo, `fire` and `pyfun-zeromode` at the versions recorded in `uv.lock`.

## Running the simulator

Pass the path to a MuJoCo XML model file. The repository includes two sample 2D arms in `robot-2D/`.

```sh
uv run mujoco-clisim robot-2D/arm-2.xml
```

On macOS the MuJoCo viewer must run under `mjpython`, the special Python launcher installed with MuJoCo. `mujoco-clisim` restarts itself under `mjpython` automatically, so the same command works on every platform.

The viewer window opens and the simulation starts running in real time. The terminal shows:

```
CLISIM version 1.0
>
```

Type commands at the `>` prompt and press Enter. Commands are not case sensitive.

## Commands

| Command | What it does |
| ------- | ------------ |
| `p`     | Pause the simulation. |
| `r`     | Resume a paused simulation. |
| `help`  | List the data commands available for the loaded model. |
| `q`     | Quit. Closing the viewer window, pressing Ctrl+D, or pressing Ctrl+C also quits. |

You can type commands while the simulation is running or while it is paused.

### Data commands

Data commands read and write fields of the simulation state (`mjData`). Each field supports up to four forms:

| Form | Example | What it does |
| ---- | ------- | ------------ |
| `<field>` | `qpos` | Print the whole array. |
| `<field>[idx]` | `qpos[1]` | Print one element. |
| `set <field> <values>` | `set qpos 0 pi/4` | Replace the array with space-separated values. |
| `set <field>[idx] <value>` | `set qpos[0] -pi/2` | Set one element. |

Values can be plain numbers or fractions of pi, written as `pi/N` or `π/N` with an optional leading `-` (for example `pi/3` or `-π/6`).

The fields are grouped as follows:

- **Joint positions:** `qpos` (read and write).
- **Actuators:** `ctrl` (read and write); `actuator_length`, `actuator_velocity` and `actuator_force` (read only).
- **Forces:** `qfrc_applied` (read and write); `qfrc_actuator`, `qfrc_passive`, `qfrc_bias`, `qfrc_smooth` and `qfrc_constraint` (read only). `qfrc` prints the net force, `qfrc_smooth + qfrc_constraint`.
## Editor type checking

MuJoCo's Python bindings are compiled extensions that ship without type stubs, so Pylance and pyright report errors such as `"MjModel" is not a known attribute of module "mujoco"`. To fix this, generate stubs into `typings/`, where Pylance looks by default:

```sh
uv run --with pybind11-stubgen pybind11-stubgen mujoco -o typings --ignore-all-errors
```

Re-run this whenever you change the MuJoCo version.
