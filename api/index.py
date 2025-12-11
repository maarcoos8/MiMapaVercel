"""
Entry point para Vercel Serverless Functions
Adapta FastAPI para funcionar como serverless usando Mangum
"""
from mangum import Mangum
import sys
from pathlib import Path

# Añadir backend al path para poder importar app
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app

# Handler para Vercel
handler = Mangum(app, lifespan="off")
