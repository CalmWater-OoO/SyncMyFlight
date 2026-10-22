"""Chemins du projet, centralisés pour tous les modules."""

from pathlib import Path
from typing import Final

RACINE_PROJET: Final[Path] = Path(__file__).resolve().parents[3]

DOSSIER_DATA: Final[Path] = RACINE_PROJET / "data"
DOSSIER_RAW: Final[Path] = DOSSIER_DATA / "raw"
DOSSIER_PROCESSED: Final[Path] = DOSSIER_DATA / "processed"
DOSSIER_MODELES: Final[Path] = RACINE_PROJET / "models"

FICHIER_VOLS_BRUTS: Final[Path] = DOSSIER_RAW / "echantillon_complet_2025.csv"
FICHIER_COMPAGNIES: Final[Path] = DOSSIER_RAW / "compagnies.csv"
FICHIER_METEO: Final[Path] = DOSSIER_RAW / "meteo_complete.csv"
FICHIER_ENTRAINEMENT: Final[Path] = DOSSIER_PROCESSED / "donnees_entrainement.parquet"
