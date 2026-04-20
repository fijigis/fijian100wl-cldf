# Fijian Language 100 Word List CLDF converter

## Requirements

- Python: 3.8+
- uv
- Dependencies: See [pyproject.toml](./pyproject.toml).

## Getting Started

Get the Excel data source (not included in this repository) and run the Python script'

```shell
$ uv run python convert.py
```

This will create a subdirectory `fijian100wl` and outputs CSV and JSON files there.
