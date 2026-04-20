# Fijian Language 100 Word List CLDF converter

## Requirements

- Python: 3.8+
- uv
- Dependencies: See [pyproject.toml](./pyproject.toml).

```shell
$ uv lock
$ uv sync
$ uv cldfbench catconfig
```

## Getting Started

Put the Excel data source (not included in this repository) in the `raw/` directory and run the Python script'

```shell
$ uv run cldfbench makecldf cldfbench_fijian100wl.py
```

This will create a subdirectory `cldf/` and outputs CSV and JSON files there.
