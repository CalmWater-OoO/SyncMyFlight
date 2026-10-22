"""Module principal de l'API backend pour la prédiction des retards aériens."""

import os
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Chargement de la configuration
load_dotenv(os.path.join(os.path.dirname(__file__), "config", "variables.env"))

URL_BASE_DONNEES = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/db_vols"
)

# Initialisation du moteur de base de données avec pool de connexions
moteur: Engine = create_engine(URL_BASE_DONNEES, pool_size=10, max_overflow=20, pool_pre_ping=True)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI) -> AsyncGenerator[None]:
    """Gère le démarrage et l'arrêt propre des connexions du serveur."""
    yield
    moteur.dispose()


app = FastAPI(
    title="API Prédiction Retards Aériens",
    description="Backend pour requêter la vue consolidée PostgreSQL et alimenter le frontend.",
    version="1.0.0",
    lifespan=cycle_de_vie,
)

# Configuration sécurisée du middleware CORS
ORIGINES_AUTORISEES = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_AUTORISEES,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Schémas de données Pydantic compatibles Python 3.9
class VolSortie(BaseModel):
    """Représentation d'un vol renvoyé par l'API."""

    date_vol: date = Field(..., alias="FL_DATE", description="Date du vol")
    compagnie: str | None = Field(None, alias="carrier_name", description="Nom du transporteur")
    ville_depart: str = Field(..., alias="ORIGIN_CITY_NAME", description="Ville de départ")
    ville_arrivee: str = Field(..., alias="DEST_CITY_NAME", description="Ville d'arrivée")
    retard_arrivee: float | None = Field(None, alias="ARR_DELAY", description="Retard en minutes")
    temperature_celsius: float | None = Field(None, alias="t2m_C", description="Température au sol")

    model_config = {"populate_by_name": True}


class ReponseVols(BaseModel):
    """Structure de la réponse pour la liste des vols."""

    total: int = Field(..., description="Nombre d'enregistrements retournés")
    vols: list[VolSortie] = Field(..., description="Liste des données de vol")


class ReponseStatut(BaseModel):
    """Structure de vérification de l'état du serveur."""

    statut: str
    base_de_donnees: str


def obtenir_connexion() -> Generator[Connection]:
    """Fournit une connexion à la base de données et garantit sa fermeture."""
    connexion = moteur.connect()
    try:
        yield connexion
    finally:
        connexion.close()


# Routes de l'API
@app.get(
    "/",
    response_model=ReponseStatut,
    status_code=status.HTTP_200_OK,
    summary="État de santé de l'API",
)
def verifier_statut() -> dict:
    """Point de contrôle pour valider l'accessibilité du service."""
    return {"statut": "en ligne", "base_de_donnees": "PostgreSQL connecté"}


@app.get(
    "/vols",
    response_model=ReponseVols,
    status_code=status.HTTP_200_OK,
    summary="Récupérer un extrait de vols consolidés",
)
def lister_vols(
    connexion: Annotated[Connection, Depends(obtenir_connexion)],
    limite: Annotated[int, Query(ge=1, le=100, description="Nombre maximum de résultats")] = 10,
) -> dict:
    """Retourne la liste des vols combinés avec les compagnies et la météo."""
    requete = text("""
        SELECT 
            "FL_DATE", 
            carrier_name, 
            "ORIGIN_CITY_NAME", 
            "DEST_CITY_NAME", 
            "ARR_DELAY", 
            "t2m_C"
        FROM public.vue_vols_complets
        ORDER BY "FL_DATE" DESC
        LIMIT :limite;
    """)

    try:
        curseur = connexion.execute(requete, {"limite": limite})
        lignes = [dict(ligne) for ligne in curseur.mappings()]
        return {"total": len(lignes), "vols": lignes}
    except SQLAlchemyError as erreur:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'accès à la base de données : {str(erreur)}",
        ) from erreur
