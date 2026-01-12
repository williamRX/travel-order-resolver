#!/usr/bin/env python3
"""
API FastAPI pour le système d'extraction d'intentions de voyage.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List
import sys
import io

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
    route: Optional[List[str]] = None  # Itinéraire complet avec étapes (si pathfinding activé)
    route_distance: Optional[float] = None  # Distance totale en km
    route_time: Optional[float] = None  # Temps estimé en heures


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
                <strong>POST /process_csv</strong> - Traiter un fichier CSV
                <br><code>Format entrée: sentenceID,sentence | Format sortie: sentenceID,Departure,Destination ou sentenceID,INVALID</code>
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


@app.post("/process_csv")
async def process_csv(file: UploadFile = File(...)):
    """
    Traite un fichier CSV et retourne les résultats au format spécifié.
    
    Format d'entrée : sentenceID,sentence (une ligne par phrase)
    Format de sortie VALIDE : sentenceID,Departure,Destination
    Format de sortie INVALIDE : sentenceID,INVALID
    
    Args:
        file: Fichier CSV à traiter
        
    Returns:
        Fichier CSV avec les résultats
    """
    print(f"📥 Réception d'un fichier CSV: {file.filename}")
    
    if pipeline is None:
        print("❌ Pipeline non initialisé")
        raise HTTPException(
            status_code=503,
            detail="Pipeline non initialisé. Vérifiez les logs du serveur."
        )
    
    # Vérifier que c'est un fichier CSV
    if not file.filename or not file.filename.endswith('.csv'):
        print(f"⚠️  Fichier invalide: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un fichier CSV (.csv)"
        )
    
    try:
        print(f"📖 Lecture du fichier: {file.filename}")
        # Lire le contenu du fichier
        content = await file.read()
        print(f"✅ Fichier lu: {len(content)} bytes")
        text_content = content.decode('utf-8')
        print(f"✅ Texte décodé: {len(text_content)} caractères")
        
        # Créer un buffer pour la sortie
        output_buffer = io.StringIO()
        
        # Traiter ligne par ligne
        input_lines = text_content.strip().split('\n')
        print(f"📝 Nombre de lignes à traiter: {len(input_lines)}")
        
        for line_number, line in enumerate(input_lines, 1):
            line = line.strip()
            
            # Ignorer les lignes vides
            if not line:
                continue
            
            # Parser la ligne : sentenceID,sentence
            parts = line.split(',', 1)  # Split seulement sur la première virgule
            
            if len(parts) != 2:
                # Format invalide, retourner INVALID
                sentence_id = parts[0] if parts else str(line_number)
                output_buffer.write(f"{sentence_id},INVALID\n")
                continue
            
            sentence_id, sentence = parts
            sentence = sentence.strip()
            
            # Vérifier que la phrase n'est pas vide
            if not sentence:
                output_buffer.write(f"{sentence_id},INVALID\n")
                continue
            
            try:
                # Utiliser le pipeline pour prédire
                result = pipeline.predict(sentence)
                
                if result["valid"]:
                    # Phrase valide
                    departure = result.get("departure", "") or ""
                    arrival = result.get("arrival", "") or ""
                    route = result.get("route", None)
                    
                    # Si on a au moins une destination, on considère comme valide
                    if departure or arrival:
                        # Si pathfinding activé et route trouvée, utiliser le format avec étapes
                        if route and len(route) > 0:
                            # Format: sentenceID,Departure,Step1,Step2,...,Destination
                            output_buffer.write(f"{sentence_id},{','.join(route)}\n")
                        else:
                            # Format classique: sentenceID,Departure,Destination
                            output_buffer.write(f"{sentence_id},{departure},{arrival}\n")
                    else:
                        # Pas de destinations trouvées, considérer comme INVALID
                        output_buffer.write(f"{sentence_id},INVALID\n")
                else:
                    # Phrase invalide : sentenceID,INVALID
                    output_buffer.write(f"{sentence_id},INVALID\n")
                    
            except Exception as e:
                # Erreur lors du traitement, considérer comme INVALID
                output_buffer.write(f"{sentence_id},INVALID\n")
        
        # Obtenir le contenu du buffer
        output_content = output_buffer.getvalue()
        print(f"✅ Traitement terminé: {len(output_content)} caractères générés")
        
        # Créer une réponse CSV
        output_bytes = output_content.encode('utf-8')
        
        print(f"📤 Envoi de la réponse CSV")
        return Response(
            content=output_bytes,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=results_{file.filename}"
            }
        )
        
    except UnicodeDecodeError as e:
        print(f"❌ Erreur de décodage UTF-8: {e}")
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être encodé en UTF-8"
        )
    except Exception as e:
        import traceback
        print(f"❌ Erreur lors du traitement: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

