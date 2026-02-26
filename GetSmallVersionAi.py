import os
import shutil
import filecmp
import argparse
import yaml
import re
from datetime import datetime
from textwrap import dedent

# Default fallback values
DEFAULT_EXCLUDE_DIRS = []
DEFAULT_EXCLUDE_FILES = []
DEFAULT_EXCLUDE_EXTS = []
DEFAULT_VERBOSE = False
DEFAULT_OUTPUT_ROOT = "./MyDiffOutput"
DEFAULT_YAML = "./SmallVersion.yaml"
CURRENT_YEAR = datetime.now().year

def load_config(config_path):
    if not config_path or not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def should_exclude(rel_path, file_name, exclude_dirs, exclude_files, exclude_exts):
    for part in rel_path.split(os.sep):
        if part in exclude_dirs:
            return True
    if file_name in exclude_files:
        return True
    _, ext = os.path.splitext(file_name)
    if ext in exclude_exts:
        return True
    return False

def copy_with_copyright_update(src_path, dst_path):


    try:
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        #
        # m.group(0) whole data.
        # m.group(1) (Copyright\s*\(c\)\s*)\d{{4}}\s*-\s*(\d{{4}}).
        # m.group(2) (\d{{4}}).
        # m.group(3) (,\s*Insyde Software Corp\. All Rights Reserved\.).
        #
        # yyyy - xxxx -> xxxx
        content = re.sub(
            rf"(Copyright\s*\(c\)\s*)\d{{4}}\s*-\s*(\d{{4}})(,\s*Insyde Software Corp\. All Rights Reserved\.)",
            lambda m: f"{m.group(1)}{CURRENT_YEAR}{m.group(3)}" if int(m.group(2)) != CURRENT_YEAR else m.group(0),
            content
        )

        # xxxx -> xxxx
        content = re.sub(
            rf"(Copyright\s*\(c\)\s*)(\d{{4}})(,\s*Insyde Software Corp\. All Rights Reserved\.)",
            lambda m: f"{m.group(1)}{CURRENT_YEAR}{m.group(3)}" if int(m.group(2)) != CURRENT_YEAR else m.group(0),
            content
        )

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        shutil.copy2(src_path, dst_path)


def compare_and_extract(folder_a, folder_b, output_root, exclude_dirs, exclude_files, exclude_exts, verbose, update_copyright):
    original_dir = os.path.join(output_root, "Original")
    modified_dir = os.path.join(output_root, "Modified")

    # Pass 1: folder_a -> folder_b
    for root, _, files in os.walk(folder_a):
        rel_path = os.path.relpath(root, folder_a)
        counterpart_root = os.path.join(folder_b, rel_path)
        for file in files:
            if should_exclude(rel_path, file, exclude_dirs, exclude_files, exclude_exts):
                continue

            path_a = os.path.join(root, file)
            path_b = os.path.join(counterpart_root, file)

            if not os.path.exists(path_b) or not filecmp.cmp(path_a, path_b, shallow=False):
                target_a = os.path.join(original_dir, rel_path, file)
                target_b = os.path.join(modified_dir, rel_path, file)

                os.makedirs(os.path.dirname(target_a), exist_ok=True)
                if os.path.exists(path_b):
                    os.makedirs(os.path.dirname(target_b), exist_ok=True)

                shutil.copy2(path_a, target_a)
                if verbose:
                    print(f"[DIFF] {os.path.join(rel_path, file)} -> Original/")
                if os.path.exists(path_b):
                    if update_copyright:
                        copy_with_copyright_update(path_b, target_b)
                    else:
                        shutil.copy2(path_b, target_b)
                    if verbose:
                        print(f"[DIFF] {os.path.join(rel_path, file)} -> Modified/")

    # Pass 2: folder_b -> folder_a
    for root, _, files in os.walk(folder_b):
        rel_path = os.path.relpath(root, folder_b)
        counterpart_root = os.path.join(folder_a, rel_path)

        for file in files:
            if should_exclude(rel_path, file, exclude_dirs, exclude_files, exclude_exts):
                continue

            path_b = os.path.join(root, file)
            path_a = os.path.join(counterpart_root, file)

            if not os.path.exists(path_a):
                target_b = os.path.join(modified_dir, rel_path, file)
                os.makedirs(os.path.dirname(target_b), exist_ok=True)
                if update_copyright:
                    copy_with_copyright_update(path_b, target_b)
                else:
                    shutil.copy2(path_b, target_b)
                if verbose:
                    print(f"[DIFF] {os.path.join(rel_path, file)} -> Modified/ (only in folder_b)")

def main():
    parser = argparse.ArgumentParser(
        description="Compare two folders and extract differing files into Original/ and Modified/ subfolders",
        epilog=dedent("""\
            *** Example usage:
              python diff_extractor.py ./v1 ./v2 --config config.yaml
              python diff_extractor.py ./v1 ./v2 --exclude-exts .log .tmp -v --update-copyright

            *** Example config.yaml:
              exclude_dirs:
                - .git
                - __pycache__
              exclude_files:
                - README.md
                - LICENSE
              exclude_exts:
                - .log
                - .tmp
              verbose: true
              output_root: ./diff_output
              update_copyright: true
        """),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("folder_a", help="Path to source folder A")
    parser.add_argument("folder_b", help="Path to target folder B")
    parser.add_argument("-c", "--config", default=DEFAULT_YAML, help="Path to YAML config file")

    parser.add_argument("--exclude-dirs", nargs="*", help="Folder names to exclude")
    parser.add_argument("--exclude-files", nargs="*", help="File names to exclude")
    parser.add_argument("--exclude-exts", nargs="*", help="File extensions to exclude (e.g. .log .tmp)")
    parser.add_argument("-o", "--output-root", default=DEFAULT_OUTPUT_ROOT, help="Root output folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print details when differences are found")
    parser.add_argument("-u", "--update-copyright", action="store_true", help="Update copyright year when copying to Modified")

    args = parser.parse_args()
    config = load_config(args.config)

    # Merge CLI args with config (CLI takes priority)
    exclude_dirs = args.exclude_dirs if args.exclude_dirs is not None else config.get("exclude_dirs", DEFAULT_EXCLUDE_DIRS)
    exclude_files = args.exclude_files if args.exclude_files is not None else config.get("exclude_files", DEFAULT_EXCLUDE_FILES)
    exclude_exts  = args.exclude_exts  if args.exclude_exts  is not None else config.get("exclude_exts",  DEFAULT_EXCLUDE_EXTS)
    output_root   = args.output_root   if args.output_root   is not None else config.get("output_root",   DEFAULT_OUTPUT_ROOT)
    verbose       = args.verbose       or config.get("verbose", DEFAULT_VERBOSE)
    update_copyright = args.update_copyright or config.get("update_copyright", False)

    compare_and_extract(
        args.folder_a,
        args.folder_b,
        output_root,
        exclude_dirs,
        exclude_files,
        exclude_exts,
        verbose,
        update_copyright
    )

if __name__ == "__main__":
    main()
