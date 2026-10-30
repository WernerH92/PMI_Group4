# PMI Group 4 — Assignments 2A/2B and 3A

This fixed package combines both Assignment 2A/2B with Assignment 3A filters and spheres.

## Windows (PowerShell)

Install MinGW-w64/GCC first and ensure `gcc` is on `PATH`.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Linux / WSL

```bash
sudo apt update
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run the Assignment 3A PDF checks after installation:

```bash
python -c "from pmi_lib.test import test_filters, test_spheres; test_filters(); test_spheres()"
```
