# Assignment 3A native filters handoff

This folder is a merge-ready transfer package. Its directory layout matches the
group repository root, so preserve the paths when copying its contents.

Included are the native build configuration, the Image and filter changes, the
required C source/header, the assignment demonstration helper, and the
automated regression tests. The `README.md` contains the short platform-specific
build/test commands.

Do not transfer compiled libraries (`.so`, `.dylib`, `.dll`), virtual
environments, `*.egg-info`, or `__pycache__` directories. Each developer must
run the editable installation on their own operating system, which creates the
correct native library for that platform.

After merging, run:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```
