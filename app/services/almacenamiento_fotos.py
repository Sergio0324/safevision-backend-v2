import os
import uuid
from pathlib import Path

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

async def subir_foto(foto_bytes: bytes, empresa_id: str) -> str:
       nombre_archivo = f"{uuid.uuid4()}.jpg"
       ruta_completa = UPLOADS_DIR / nombre_archivo
       
       with open(ruta_completa, "wb") as f:
           f.write(foto_bytes)
       
       return f"http://192.168.20.71:8000/uploads/{nombre_archivo}"