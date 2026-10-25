# PMI Group 4 — Assignment 3A

Run these commands from this directory. The native compiler must be available
on `PATH` before installing the package.

## Windows (PowerShell)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Linux

```bash
sudo apt update
sudo apt install build-essential
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

## macOS

```bash
xcode-select --install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```
