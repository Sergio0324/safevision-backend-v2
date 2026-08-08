from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import inspecciones

app = FastAPI(
    title="SAFEVISION AI Backend",
    description="API para auditoría automatizada de SG-SST",
    version="0.1.0"
)

# Registrar routers
app.include_router(inspecciones.router)

@app.get("/health")
async def health():
    """Health check."""
    return JSONResponse({"status": "ok"})

@app.get("/")
async def root():
    return {"message": "SAFEVISION AI Backend - ve a /docs para probar"}
