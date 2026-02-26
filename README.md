# GetSmallVersion

A robust Python-based directory comparison and automated Copyright management tool designed for firmware development workflows.

## 🌟 Key Features

- **Bidirectional Comparison**: Precisely identifies `Added`, `Removed`, and `Modified` files between two source trees.
- **Automated Environment Cleanup**: Automatically wipes the output directory before each run to ensure no stale data remains.
- **Copyright Transformation**:
  - Automatically updates the year to the current year (**2026**).
  - Supports converting legacy formats (e.g., `Copyright (c) 2013-2023`) to modern standards.
  - Optional flag to switch to the **New Format** (removes `(c)` and commas).
- **Flexible Configuration**: Supports both YAML configuration files and Command Line Interface (CLI) arguments.
- **Custom Filters**: Exclude specific directories (like `.git`), files, or extensions (like `.log` or `.tmp`).

## 🌟 Introduction

`GetSmallVersion` is a specialized utility to compare two folders and extract the differences into `Original` and `Modified` subdirectories. It also features a powerful Regex-based engine to update and reformat Insyde Software Corp. Copyright headers automatically.

---

## 🚀 Quick Start

Get up and running in less than a minute.


### 1. Install Dependencies
This tool requires `PyYAML`. Install it via pip:
```bash
pip install pyyaml
```
### 2. Run a Basic Comparison
Compare two folders and save results to the default output directory (./MyDiffOutput):
```Bash
python diff_extractor.py ./folder_v1 ./folder_v2
```
### 3. Update Copyright with New Format
Automatically update the year and apply the simplified format (no (c), no comma):
```Bash
python diff_extractor.py ./folder_v1 ./folder_v2 -u -n -v
```
## ⚙️ Configuration (SmallVersion.yaml)
You can manage complex settings through a YAML configuration file:

YAML
output_root: "./MyDiffOutput"
verbose: true
update_copyright: true
new_copyright_format: true  # If true: Copyright 2026 Insyde...
exclude_dirs:
  - ".git"
  - "__pycache__"
exclude_exts:
  - ".log"
  - ".tmp"
  - ".obj"

## 📂 Output Structure
The tool organizes output as follows:

Original/: Files from Folder A that were modified or deleted in Folder B.

Modified/: New files from Folder B or modified files (with updated Copyright).