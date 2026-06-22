#!/usr/bin/env python3
"""Install dotfiles into $HOME via symlinks, auto-detecting the current OS."""

import argparse
import os
import shutil
import sys
from pathlib import Path

_OS_MAP = {"linux": "Linux", "win32": "Windows", "darwin": "MacOSX"}


def _iter_files(src_dir):
    """Yield (src_path, rel_path) for all files under src_dir, following symlinks."""
    for root, _, files in os.walk(src_dir, followlinks=True):
        for name in files:
            src = Path(root) / name
            yield src, src.relative_to(src_dir)


def install_files(src_dir, dst_root):
    """Symlink all files under src_dir into dst_root.

    Preserve directory structure.
    Return count of installed.
    """
    installed = 0

    for src, rel in sorted(_iter_files(src_dir), key=lambda x: x[1]):
        dst = dst_root / rel

        # If the parent directory resolves into the project tree (e.g.
        # ~/.config/nvim is a symlink to Linux/.config/nvim), the file is
        # already managed by git — skip to avoid overwriting project links.
        dst_parent_real = None
        try:
            dst_parent_real = dst.parent.resolve()
            dst_parent_real.relative_to(src_dir.parent)
            print(f"  skip   : {rel} (parent dir in project)")
            continue
        except (ValueError, RuntimeError, OSError):
            # ValueError: not under project — safe to manage
            # RuntimeError/OSError: symlink resolution failed — proceed with
            #   caution (the checks below will handle missing/broken paths).
            pass

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

    for src, rel_path in sorted(_iter_files(src_dir), key=lambda x: x[1]):
        rel = str(rel_path)
        src_files[rel] = src

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
    """Remove symlinks that point into this project.

    Walks dst_root without following directory symlinks to avoid
    entering the project tree and causing hangs or accidental
    modification of project files.  Directory symlinks that resolve
    into the project (legacy artefacts from older installs) are
    removed; file symlinks that resolve into the project are skipped
    (they are project files managed by git).

    Return count removed.
    """
    if not dst_root.is_dir():
        print(f"Target directory not found: {dst_root}")
        return 0

    removed = 0
    seen = set()

    for root, dirs, files in os.walk(dst_root, followlinks=False):
        # Directory symlinks — if they resolve into the project they
        # are legacy install artefacts and should be removed.
        for name in dirs:
            f = Path(root) / name
            if not f.is_symlink():
                continue
            ours = False
            try:
                f.resolve().relative_to(src_dir.parent)
                ours = True  # resolves into project — legacy dir link
            except (ValueError, RuntimeError, OSError):
                target = os.readlink(f)
                if str(src_dir) in target:
                    ours = True  # target string references project
            if not ours:
                continue
            rel = f.relative_to(dst_root)
            if rel not in seen:
                seen.add(rel)
                print(f"  remove: {rel} (dir link)")
                f.unlink()
                removed += 1

        # File symlinks — only remove those whose target string
        # references the source directory.  (followlinks=False already
        # prevents os.walk from reaching project files via dir symlinks,
        # so no resolve guard is needed here.)
        for name in files:
            f = Path(root) / name
            if not f.is_symlink():
                continue
            target = os.readlink(f)
            if str(src_dir) in target:
                rel = f.relative_to(dst_root)
                if rel in seen:
                    continue
                seen.add(rel)
                print(f"  remove: {rel}")
                f.unlink()
                removed += 1

    # Phase 2: remove known source-pair symlinks that os.walk may have
    # missed (e.g. when the parent directory is a real dir but the
    # symlink's parent resolved into the project via a dir symlink).
    for src, rel_path in sorted(
        _iter_files(src_dir), key=lambda x: x[1], reverse=True
    ):
        dst = dst_root / rel_path
        if dst.is_symlink() and str(rel_path) not in seen:
            target = os.readlink(dst)
            if str(src_dir) in target:
                print(f"  remove: {rel_path}")
                dst.unlink()
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
        help=
        "remove symlinks pointing to this project (never deletes real files/dirs)",
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
