# Bundled Python runtime

The public site's `runtime/` files are copied unchanged from the official `pyodide@314.0.7` npm package. These third-party notices apply to those runtime components.

- Pyodide contributors and Mozilla: Mozilla Public License 2.0. See `PYODIDE-LICENSE.txt`.
- Python 3.14.2: see `PYTHON-LICENSE.txt`, copied from the matching CPython release.
- Corresponding Python source: https://github.com/python/cpython/tree/v3.14.2
- Corresponding Pyodide source: https://github.com/pyodide/pyodide/tree/314.0.7
- Distribution: https://www.npmjs.com/package/pyodide/v/314.0.7

No Pyodide runtime file is modified by this build. The checker uses the bundled standard library and does not install additional Python packages.
