from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.routers import inspecciones

app = FastAPI(
    title="SAFEVISION AI Backend",
    description="API para auditoría automatizada de SG-SST",
    version="0.1.0"
)

# AGREGAR ESTO ↓
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# HASTA AQUÍ ↑

# Registrar routers
app.include_router(inspecciones.router)

# Servir carpeta de uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/")
async def root():
    return {"message": "SAFEVISION AI Backend - ve a /docs para probar"}