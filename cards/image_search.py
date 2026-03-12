from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageOps


def compute_color_histogram_signature(file_obj: BinaryIO, bins_per_channel: int = 8) -> str:
    """Return normalized RGB histogram as a compact CSV string."""
    original_position = file_obj.tell() if hasattr(file_obj, "tell") else None
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)

    image_bytes = file_obj.read()
    image = Image.open(BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")

    signature_parts: list[str] = []
    for channel_index in (0, 1, 2):
        channel = image.getchannel(channel_index)
        hist = channel.histogram()
        step = max(1, 256 // bins_per_channel)
        buckets = [sum(hist[i : i + step]) for i in range(0, 256, step)]

        total = sum(buckets) or 1
        normalized = [bucket / total for bucket in buckets]
        signature_parts.extend(f"{value:.6f}" for value in normalized)

    if hasattr(file_obj, "seek") and original_position is not None:
        file_obj.seek(original_position)

    return ",".join(signature_parts)
