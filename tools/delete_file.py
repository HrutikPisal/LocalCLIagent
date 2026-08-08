import shutil

from tools.path_utils import resolve_path, tool_result


def delete_file(path: str) -> str:
    """Delete a file."""

    try:
        target = resolve_path(path)

        if not target.exists():
            return tool_result(False, error="Path does not exist.")

        if target.is_dir():
            return tool_result(False, error="Path is a directory. Only files can be deleted.")

        target.unlink()
        return tool_result(True, path=str(target), message="File deleted.")

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def rename_file(source: str, destination: str) -> str:
    """Rename or move a file within the workspace."""

    try:
        src = resolve_path(source)
        dst = resolve_path(destination)

        if not src.exists():
            return tool_result(False, error="Source path does not exist.")

        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)

        return tool_result(
            True,
            source=str(src),
            destination=str(dst),
            message="File renamed.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def copy_file(source: str, destination: str) -> str:
    """Copy a file to a new location."""

    try:
        src = resolve_path(source)
        dst = resolve_path(destination)

        if not src.exists() or not src.is_file():
            return tool_result(False, error="Source file does not exist.")

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        return tool_result(
            True,
            source=str(src),
            destination=str(dst),
            message="File copied.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def move_file(source: str, destination: str) -> str:
    """Move a file to a new location."""

    try:
        src = resolve_path(source)
        dst = resolve_path(destination)

        if not src.exists():
            return tool_result(False, error="Source path does not exist.")

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

        return tool_result(
            True,
            source=str(src),
            destination=str(dst),
            message="File moved.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
