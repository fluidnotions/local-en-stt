import csv
import json
from pathlib import Path
from typing import Optional, Iterable, Tuple, Any


class FileUtils:
    @staticmethod
    def _find_dir_upwards(target: str, start_path: Optional[Path] = None) -> Path:
        """
        Search upwards from start_path (or CWD) for a directory named `target`.
        Raises FileNotFoundError if not found.
        """
        current = Path(start_path or Path.cwd()).resolve()
        while True:
            candidate = current / target
            if candidate.exists() and (candidate.is_dir() or candidate.is_file()):
                return candidate
            if current.parent == current:
                break  # reached root
            current = current.parent
        raise FileNotFoundError(f"Directory/file '{target}' not found upwards from {start_path or Path.cwd()}")

    @staticmethod
    def _resolve_path(path_or_dirname: str, start_path: Optional[Path] = None) -> Path:
        # If it’s an absolute or relative path and exists, use it. Otherwise, treat as dir name to find upwards.
        p = Path(path_or_dirname)
        if p.exists():
            return p.resolve()
        return FileUtils._find_dir_upwards(path_or_dirname, start_path)
    
    @staticmethod
    def project_root():
        git_dir = FileUtils._find_dir_upwards(".git")
        return git_dir.parent

    @staticmethod
    def ds_root():
        return FileUtils.project_root() / "data_sources"
        

    @staticmethod
    def csv_dump(filepath: Path, rows: Iterable[Tuple]):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", newline="") as fh:
            csv.writer(fh).writerows(rows)

    @staticmethod
    def backup_json(filepath: Path, data: Any):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(data, indent=2, default=str))