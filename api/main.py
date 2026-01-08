#!/usr/bin/env python3
"""
API FastAPI pour le système d'extraction d'intentions de voyage.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import sys

# Ajouter le répertoire parent au path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.pipeline import TravelIntentPipeline

# Initialiser l'API
app = FastAPI(
    title="Travel Intent Extraction API",
    description="API pour extraire les destinations de départ et d'arrivée depuis des phrases",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le pipeline au démarrage
print("🚀 Initialisation du pipeline...")
try:
    pipeline = TravelIntentPipeline()
except Exception as e:
    print(f"❌ Erreur lors du chargement du pipeline: {e}")
    pipeline = None


# Modèles Pydantic pour la validation
class SentenceRequest(BaseModel):
    """Requête avec une phrase à analyser."""
    sentence: str


class SentenceResponse(BaseModel):
    """Réponse avec les résultats de l'analyse."""
    valid: bool
    message: Optional[str]
    departure: Optional[str]
    arrival: Optional[str]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil de l'API."""
    return """
    <html>
        <head>
            <title>Travel Intent Extraction API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🚂 Travel Intent Extraction API</h1>
            <p>API pour extraire les destinations de départ et d'arrivée depuis des phrases.</p>
            <h2>Endpoints disponibles:</h2>
            <div class="endpoint">
                <strong>POST /predict</strong> - Analyser une phrase
                <br><code>{"sentence": "Je vais de Paris à Lyon"}</code>
            </div>
            <div class="endpoint">
                <strong>GET /health</strong> - Vérifier l'état de l'API
            </div>
            <p><a href="/docs">Documentation interactive (Swagger)</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Vérifie l'état de l'API."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline non initialisé")
    return {
        "status": "healthy",
        "pipeline_loaded": pipeline is not None
    }


@app.post("/predict", response_model=SentenceResponse)
async def predict(request: SentenceRequest):
    """
    Analyse une phrase et extrait les destinations de départ et d'arrivée.
    
    Args:
        request: Requête contenant la phrase à analyser
        
    Returns:
        Réponse avec les résultats de l'analyse
    """
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline non initialisé. Vérifiez les logs du serveur."
        )
    
    if not request.sentence or not request.sentence.strip():
        raise HTTPException(
            status_code=400,
            detail="La phrase ne peut pas être vide"
        )
    
    try:
        result = pipeline.predict(request.sentence)
        return SentenceResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

