"""
Módulo de almacenamiento de fotos
Gestiona subida de imágenes a Cloudinary
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


async def subir_foto(foto_bytes: bytes, empresa_id: str) -> str:
    """
    Sube foto a Cloudinary y devuelve URL
    
    Args:
        foto_bytes: Bytes de la foto
        empresa_id: ID de la empresa (para organizar carpetas)
    
    Returns:
        URL pública de Cloudinary
    
    Raises:
        Exception si falla el upload
    """
    try:
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            foto_bytes,
            folder=f"safevision/{empresa_id}",
            resource_type="auto"
        )
        
        # Devolver URL pública
        return result['secure_url']
    
    except Exception as e:
        print(f"❌ Error subiendo foto a Cloudinary: {e}")
        raise Exception(f"No se pudo guardar la foto: {str(e)}")


def eliminar_foto_inspeccion(foto_public_id: str) -> dict:
    """
    Eliminar foto de Cloudinary
    
    Args:
        foto_public_id: ID público de la foto (guardado en BD)
    
    Returns:
        {"success": bool, "error": str (si falla)}
    """
    
    try:
        cloudinary.uploader.destroy(foto_public_id)
        return {"success": True}
    
    except Exception as e:
        print(f"❌ Error eliminando foto: {str(e)}")
        return {
            "success": False,
            "error": str(e),
        }


def obtener_url_foto(foto_public_id: str) -> str:
    """Obtener URL pública de una foto guardada"""
    return cloudinary.CloudinaryResource(foto_public_id).build_url()