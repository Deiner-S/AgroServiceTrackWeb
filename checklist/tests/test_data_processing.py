import pytest
from django.core.exceptions import ValidationError

from checklist.utils.data_processing import prepare_image


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\x99c\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\xb1"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_prepare_image_returns_none_for_empty_value():
    assert prepare_image(None) is None


def test_prepare_image_accepts_raw_bytes():
    image = prepare_image(PNG_BYTES, filename_prefix="assinatura")

    assert image is not None
    assert image.name == "assinatura.png"


def test_prepare_image_accepts_dict_payload():
    raw_img = {index: byte for index, byte in enumerate(PNG_BYTES)}

    image = prepare_image(raw_img, filename_prefix="checklist")

    assert image is not None
    assert image.name == "checklist.png"


def test_prepare_image_raises_for_invalid_dict_payload():
    raw_img = {"a": 1}

    with pytest.raises(ValidationError, match="Falha ao reconstruir bytes da imagem"):
        prepare_image(raw_img)


def test_prepare_image_raises_for_unsupported_type():
    with pytest.raises(ValidationError, match="Formato de imagem"):
        prepare_image("nao-suportado")


def test_prepare_image_raises_for_invalid_image_bytes():
    with pytest.raises(ValidationError, match="imagem"):
        prepare_image(b"not-an-image")
