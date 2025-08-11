import os
from enum import Enum, auto


class StorageDir(Enum):
    STORE = auto()

    @property
    def path(self) -> str:
        return self.name.lower()


class Extensions(Enum):
    TXT = auto()
    PDF = auto()
    PNG = auto()
    JPG = auto()
    JPEG = auto()
    GIF = auto()

    @property
    def path(self) -> str:
        return self.name.lower()


def get_file_path(file_hash) -> str | None:
    if len(file_hash) < 2:
        return None
    subdir = file_hash[:2]
    return os.path.join(StorageDir.STORE.path, subdir, file_hash)


def allowed_file(filename) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in {e.path for e in Extensions}
