import imghdr
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


def prepare_image(raw_img, filename_prefix="image"):
    if not raw_img:
        return None

    # Caso 1 — já chegou como bytes (raro, mas seguro)
    if isinstance(raw_img, (bytes, bytearray)):
        img_bytes = bytes(raw_img)

    # Caso 2 — chegou como dict (SEU CASO ATUAL)
    elif isinstance(raw_img, dict):
        try:
            # ordena pelas chaves numéricas
            ordered_bytes = [
                raw_img[str(i)] if str(i) in raw_img else raw_img[i]
                for i in range(len(raw_img))
            ]
            img_bytes = bytes(ordered_bytes)
        except Exception:
            raise ValidationError("Falha ao reconstruir bytes da imagem")

    else:
        raise ValidationError(f"Formato de imagem não suportado: {type(raw_img)}")

    # Detecta tipo real da imagem (png, jpeg, etc)
    img_type = imghdr.what(None, img_bytes)
    if not img_type:
        raise ValidationError("Arquivo recebido não é uma imagem válida")

    filename = f"{filename_prefix}.{img_type}"
    return ContentFile(img_bytes, name=filename)
