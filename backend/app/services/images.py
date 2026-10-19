def looks_like_image(data: bytes) -> bool:
    """Check the file's first bytes, because the browser-supplied content type can be faked."""
    return (
        data.startswith(b"\xff\xd8\xff")  # JPEG
        or data.startswith(b"\x89PNG\r\n\x1a\n")  # PNG
        or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")  # WEBP
    )
