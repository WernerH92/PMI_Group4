# Combined Assignment 2A/2B and 3A handoff

Copy this folder as a whole. It is a standalone `pmi_lib` package with the
Assignment 2A/2B readers, writer, converter, and CLI as well as the Assignment
3A native filters and spheres.

Do not add virtual environments, egg-info folders, Python caches, or compiled
native libraries. Each recipient must run the editable-install command from
`README.md`; that builds the correct native library for their operating system.

The package uses `(y, x)` for 2D images and `(z, y, x)` for 3D images, with
spacing in the same order. Do not install a separate project that also provides
`pmi_lib` into the same virtual environment: use this combined handoff instead.
