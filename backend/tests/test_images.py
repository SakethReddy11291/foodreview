from app.services.images import looks_like_image


def test_real_image_headers():
    assert looks_like_image(b"\xff\xd8\xff\xe0" + b"0" * 20)
    assert looks_like_image(b"\x89PNG\r\n\x1a\n" + b"0" * 20)
    assert looks_like_image(b"RIFF\x00\x00\x00\x00WEBPVP8 ")


def test_fake_files_rejected():
    assert not looks_like_image(b"")
    assert not looks_like_image(b"just some text pretending to be a photo")
