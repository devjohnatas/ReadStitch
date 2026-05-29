"""Custom exceptions for ReadStitch application."""


class ReadStitchError(Exception):
    """Base exception for all ReadStitch errors."""
    pass


class DirectoryException(ReadStitchError):
    """Raised when there's an issue with directory operations."""
    pass


class ProfileException(ReadStitchError):
    """Raised when there's an issue with profile operations."""
    pass


class ImageProcessingError(ReadStitchError):
    """Raised when image processing fails."""
    pass


class WatermarkError(ReadStitchError):
    """Raised when watermark application fails."""
    pass
