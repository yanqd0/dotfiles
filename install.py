#!/usr/bin/env python3
"""Install dotfiles into $HOME via symlinks, auto-detecting the current OS."""

import argparse
import os
import shutil
import sys
from pathlib import Path

_OS_MAP = {"linux": "Linux", "win32": "Windows", "darwin": "MacOSX"}


def install_files(src_dir, dst_root):
    """Symlink all files under src_dir into dst_root.

    Preserve directory structure.
    Return count of installed.
    """
    installed = 0

    for src in sorted(src_dir.rglob("*")):
        if not src.is_file():
            continue

        rel = src.relative_to(src_dir)
        dst = dst_root / rel

        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.is_symlink():
            if os.readlink(dst) == str(src):
                print(f"  skip   : {rel} (correct)")
                continue
            print(f"  fix    : {rel} -> {src}")
            dst.unlink()
        elif dst.exists():
            print(f"  skip   : {rel} (existing file)")
            continue
        else:
            print(f"  install: {rel}")

        dst.symlink_to(src)
        installed += 1

    return installed


def _validate(src_dir, dst_root):
    passed = 0
    failed = 0
    src_files = {}
    dst_files = {}

    for src in sorted(src_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        src_files[str(rel)] = src

    for f in sorted(dst_root.rglob("*")):
        if not f.is_symlink():
            continue
        target = os.readlink(f)
        rel = str(f.relative_to(dst_root))
        if str(src_dir) in target:
            if rel in dst_files:
                print(f"  ✗ {rel} (duplicate)")
                failed += 1
                continue
            dst_files[rel] = f

    for rel, src in sorted(src_files.items()):
        dst = dst_root / rel
        if not dst.exists():
            print(f"  ✗ {rel} (missing)")
            failed += 1
            continue
        if not dst.is_symlink():
            print(f"  ✗ {rel} (not a symlink)")
            failed += 1
            continue
        if os.readlink(dst) != str(src):
            print(f"  ✗ {rel} -> {os.readlink(dst)} (expected: {src})")
            failed += 1
            continue
        print(f"  ✓ {rel}")
        passed += 1

    extra = set(dst_files) - set(src_files)
    for rel in sorted(extra):
        print(f"  ✗ {rel} (extra)")
        failed += 1

    return passed, failed


def _revert(src_dir, dst_root):
    """Remove symlinks that point to src_dir or broken.

    Return count removed.
    """
    if not dst_root.is_dir():
        print(f"Target directory not found: {dst_root}")
        return 0

    removed = 0
    for f in sorted(dst_root.rglob("*"), reverse=True):
        if f.is_symlink():
            target = os.readlink(f)
            if str(src_dir) in target or not f.exists():
                rel = f.relative_to(dst_root)
                print(f"  remove: {rel}")
                f.unlink()
                removed += 1

    return removed


def _run_test(src_dir):
    root = Path("/tmp/my-dotfiles")
    dst_root = root / "home"

    print(f"=== Install test ({dst_root}) ===\n")

    installed = install_files(src_dir, dst_root)
    print(f"\nInstalled {installed} files.\n")

    print("=== Validation ===")
    passed, failed = _validate(src_dir, dst_root)

    print(f"\nClean up {root} ...")
    shutil.rmtree(root)

    result = "PASSED" if failed == 0 else "FAILED"
    print(f"\n=== Test {result}: {passed} passed, {failed} failed ===")
    sys.exit(0 if failed == 0 else 1)


def main():
    """Symlink dotfiles into $HOME.

    Auto-detects OS to pick the right source directory.
    """
    os_name = _OS_MAP.get(sys.platform, 'Unknown')
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "--os",
        choices=sorted(_OS_MAP.values()),
        default=os_name,
        help=f"source directory name (default: {os_name or 'unknown'})",
    )
    parser.add_argument(
        "--root",
        "-r",
        default="~",
        help="target root directory (default: ~)",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="install to /tmp/my-dotfiles/, validate, then clean up",
    )
    action.add_argument(
        "--revert",
        action="store_true",
        help="remove symlinks pointing to this repo, and broken symlinks",
    )
    args = parser.parse_args()

    if not args.os:
        print(f"Unsupported platform: {sys.platform}", file=sys.stderr)
        print(
            "Use --os to specify 'Linux', 'Windows', or 'MacOSX'.",
            file=sys.stderr,
        )
        sys.exit(1)

    src_dir = Path(__file__).resolve().parent / args.os
    if not src_dir.is_dir():
        print(f"Source directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)

    dst_root = Path(args.root).expanduser()
    if args.test:
        _run_test(src_dir)
    elif args.revert:
        removed = _revert(src_dir, dst_root)
        print(f"\nDone. {removed} symlinks removed.")
    else:
        installed = install_files(src_dir, dst_root)
        print(f"\nDone. {installed} files installed.")


if __name__ == "__main__":
    main()
