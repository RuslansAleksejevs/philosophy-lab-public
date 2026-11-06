"""Read an exact native rollout, retaining uncompressed byte/line coordinates.

Plain files are opened directly. Zstandard files are validated in full and
expanded into an anonymous, bounded temporary file only when bytes are needed.
No directories are searched: a missing *.jsonl may use only its *.jsonl.zst
sibling. All source opens reject symlinks, including directory components.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from types import SimpleNamespace

MAX_ROLLOUT_BYTES = 1024 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024


def regular_file(path: Path):
    """Open a regular source through no-follow directory descriptors."""
    path = Path(path).absolute()
    if ".." in path.parts:
        raise ValueError("source path may not contain parent traversal")
    directory = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            try:
                next_directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                         dir_fd=directory)
            except OSError as exc:
                raise ValueError("source directory is unavailable or contains a symlink") from exc
            os.close(directory)
            directory = next_directory
        try:
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=directory)
        except OSError as exc:
            raise ValueError("source is unavailable or a symlink") from exc
    finally:
        os.close(directory)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise ValueError("source must be a regular file")
    return os.fdopen(fd, "rb")


def _storage(st, encoding):
    return {"encoding": encoding, "bytes": st.st_size, "mtime_ns": st.st_mtime_ns,
            "ctime_ns": st.st_ctime_ns, "inode": st.st_ino, "device": st.st_dev}


def _copy_bounded(source, destination, maximum):
    total = 0
    while True:
        chunk = source.read(min(CHUNK_BYTES, maximum - total + 1))
        if not chunk:
            return total
        total += len(chunk)
        if total > maximum:
            raise ValueError("source exceeds bounded uncompressed rollout size")
        destination.write(chunk)


def _decode_zstd(source, destination, maximum):
    try:
        from compression import zstd
    except ImportError:
        # Older supported Python runtimes may use a locally installed decoder.
        # Its stdin is the already checked descriptor, never a pathname/shell.
        executable = shutil.which("zstd")
        if executable is None:
            raise ValueError("zstd source requires Python 3.14+ or the local zstd command")
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen([executable, "--decompress", "--stdout", "--quiet"],
                                       stdin=source, stdout=subprocess.PIPE, stderr=errors)
            try:
                total = _copy_bounded(process.stdout, destination, maximum)
                if process.wait() != 0:
                    raise ValueError("invalid or truncated zstd source")
                return total
            finally:
                process.stdout.close()
                if process.poll() is None:
                    process.kill()
                process.wait()
    try:
        # ZstdFile validates frame endings/checksums, concatenated frames and
        # trailing bytes. Streaming output keeps memory independent of size.
        with zstd.ZstdFile(source, "rb") as decoded:
            return _copy_bounded(decoded, destination, maximum)
    except (EOFError, zstd.ZstdError) as exc:
        raise ValueError("invalid or truncated zstd source") from exc


class RolloutFile:
    def __init__(self, path, stream, maximum):
        self.path = path
        self.raw = stream
        self.maximum = maximum
        self.encoding = "zstd" if path.name.endswith(".zst") else "plain"
        self.logical_name = path.name[:-4] if self.encoding == "zstd" else path.name
        self.before = os.fstat(stream.fileno())
        self.expanded = None
        self.logical_size = None

    def storage_signature(self):
        """Physical identity used only with a previously verified content cursor."""
        return _storage(self.before, self.encoding)

    def verify_unchanged(self):
        if self.encoding != "zstd":
            return
        expected = self.storage_signature()
        if _storage(os.fstat(self.raw.fileno()), self.encoding) != expected:
            raise ValueError("compressed source mutated during reading")
        # Detect replacement/unlink as well as in-place changes; no symlink
        # fallback is permitted for a physical source already opened.
        with regular_file(self.path) as current:
            if _storage(os.fstat(current.fileno()), self.encoding) != expected:
                raise ValueError("compressed source replaced during reading")

    def _stream(self):
        if self.encoding == "plain":
            return self.raw
        if self.expanded is None:
            expanded = tempfile.TemporaryFile()
            try:
                self.logical_size = _decode_zstd(self.raw, expanded, self.maximum)
                self.verify_unchanged()
                expanded.seek(0)
            except BaseException:
                expanded.close()
                raise
            self.expanded = expanded
        return self.expanded

    def logical_stat(self):
        if self.encoding == "plain":
            return os.fstat(self.raw.fileno())
        self._stream()
        self.verify_unchanged()
        return SimpleNamespace(st_size=self.logical_size, st_mtime_ns=self.before.st_mtime_ns,
                               st_ctime_ns=self.before.st_ctime_ns, st_ino=self.before.st_ino,
                               st_dev=self.before.st_dev)

    def read(self, size=-1):
        return self._stream().read(size)

    def readline(self, size=-1):
        return self._stream().readline(size)

    def seek(self, *args):
        return self._stream().seek(*args)

    def tell(self):
        return self._stream().tell()

    def close(self):
        if self.expanded is not None:
            self.expanded.close()
        self.raw.close()


@contextlib.contextmanager
def rollout_file(path, *, max_bytes=MAX_ROLLOUT_BYTES):
    if type(max_bytes) is not int or max_bytes < 1:
        raise ValueError("positive maximum uncompressed rollout size required")
    path = Path(path).absolute()
    try:
        raw = regular_file(path)
    except ValueError as exc:
        # Permission errors, symlinks and special files never select a fallback.
        if (not path.name.endswith(".jsonl")
                or str(exc) != "source is unavailable or a symlink"
                or not isinstance(exc.__cause__, FileNotFoundError)):
            raise
        path = path.with_name(path.name + ".zst")
        raw = regular_file(path)
    source = RolloutFile(path, raw, max_bytes)
    try:
        yield source
        source.verify_unchanged()
    finally:
        source.close()
