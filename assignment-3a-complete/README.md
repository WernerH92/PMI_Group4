# Assignment 3A Bundle

This folder contains the necessary functions and instructions for the Assignment 3A bilateral filter, sphere implementations, the testing functions from the PDF assignment, and seven automated tests. Run the
commands below from this folder in a clean environment. Python 3.12+ and a C
compiler are required.

## Windows (PowerShell)

Install Python and MinGW-w64/GCC first, and ensure `gcc` is on `PATH`.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## macOS

```bash
xcode-select --install
python3 -m venv .venv
source .venv/bin/activate
```

## Linux / WSL

```bash
sudo apt update
sudo apt install -y build-essential python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

## Install and run

With the virtual environment activated:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -c "from pmi_lib.test import test_filters, test_spheres; test_filters(); test_spheres()"
```

All seven automated tests should pass. The bilateral MSE difference should be
near zero and all the sphere comparisons should be `0.0`.
