# SAFEVISION AI Backend v2 (Limpio)

## Instalación rápida

```bash
# 1. Copia .env
cp .env.example .env
# Edita .env con tu DATABASE_URL de Neon y ANTHROPIC_API_KEY

# 2. Crea venv
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Levanta el servidor
uvicorn app.main:app --reload
```

Abre `http://localhost:8000/docs` para probar.

## Configuración previa en Neon

1. Crea una empresa y una sede en tu BD Neon:

```sql
INSERT INTO empresas (id, nombre, nit, plan, fecha_registro)
VALUES ('cc189ae0-1d23-4145-9768-f3b6f5e20253', 'Empresa Test', '123456789', 'piloto', NOW());

INSERT INTO sedes (id, empresa_id, nombre, ciudad, direccion)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'cc189ae0-1d23-4145-9768-f3b6f5e20253', 'Sede Principal', 'Bogotá', 'Calle 1');
```

2. En `app/core/security.py`, reemplaza los UUIDs del stub con los de arriba.

## Para probar en Swagger

- **sede_id**: `550e8400-e29b-41d4-a716-446655440000`
- **categoria**: `extintores`
- **ubicacion_descripcion**: `sotano`
- **foto**: cualquier `.jpg` de un extintor

¡Listo!
