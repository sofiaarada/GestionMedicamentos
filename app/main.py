from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import engine, Base, get_db
from app.routers import predicciones
from app.models import models

from app.routers import categorias, medicamentos, lotes, movimientos,analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gestion de Medicamentos",
    description="Backend para control de inventario y prediccion de demanda con Machine Learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(categorias.router)
app.include_router(medicamentos.router)
app.include_router(lotes.router)
app.include_router(movimientos.router)
app.include_router(analytics.router)
app.include_router(predicciones.router)

# Servir archivos estáticos (CSS, JS)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_path):
    # Montar CSS
    css_path = os.path.join(frontend_path, "css")
    if os.path.exists(css_path):
        app.mount("/css", StaticFiles(directory=css_path), name="css")
    
    # Montar JS
    js_path = os.path.join(frontend_path, "js")
    if os.path.exists(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")
    
    # Montar Static general
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return{
        "status"  : "success",
        "mensaje" : "Bienvenido a la API de Gestion de Medicamentos Servidor y BD conectados correctamente"
    }

# Servir templates HTML (debe ir al final para no interceptar otras rutas)
@app.get("/{path:path}")
async def serve_templates(path: str):
    """Sirve los archivos HTML del frontend"""
    # No servir archivos que no sean HTML
    if not path.endswith('.html') and '.' in path:
        return {"error": "Tipo de archivo no soportado"}
    
    template_path = os.path.join(frontend_path, "templates", path if path else "index.html")
    
    if os.path.exists(template_path) and template_path.endswith(".html"):
        return FileResponse(template_path)
    
    # Si no existe, devuelve el index por defecto
    index_path = os.path.join(frontend_path, "templates", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Página no encontrada"}