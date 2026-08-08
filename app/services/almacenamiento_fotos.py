"""Almacenamiento de fotos - stub por ahora.
En producción: conectar a Cloudflare R2 o AWS S3."""

async def subir_foto(foto_bytes: bytes, empresa_id: str) -> str:
    """Stub: devuelve un URL fake. En producción, aquí va el código real."""
    # Por ahora, solo guardamos en memoria un fake URL
    # En producción: uploadear a S3/R2 y devolver el URL real
    return f"s3://safevision-bucket/empresa-{empresa_id}/foto-{id(foto_bytes)}.jpg"
