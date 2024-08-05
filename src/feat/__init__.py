import importlib.metadata

try:
    __version__ = importlib.metadata.version("feat-feedback-tool")
except importlib.metadata.PackageNotFoundError:
    __version__ = None
