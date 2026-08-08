from fastapi import Header
from pydantic import BaseModel

class UsuarioActual(BaseModel):
    id: str
    empresa_id: str
    rol: str

async def get_current_user(authorization: str = Header(default=None)) -> UsuarioActual:
    """Stub: devuelve siempre el mismo usuario de prueba.
    En producción, aquí va la validación real de JWT (Auth0/Firebase)."""
    # Reemplaza estos UUIDs con los de tu empresa de prueba en Neon
    return UsuarioActual(
        id="550e8400-e29b-41d4-a716-446655440001",
        empresa_id="cc189ae0-1d23-4145-9768-f3b6f5e20253",
        rol="inspector"
    )
