"""Outils communs de téléchargement des données depuis Hugging Face."""

import logging
from pathlib import Path

import pandas as pd
from datasets import load_dataset

from app.config.constants import DEPOT_HUGGING_FACE

logger = logging.getLogger(__name__)


def telecharger_table(fichier_distant: str) -> pd.DataFrame:
    """Télécharge un fichier CSV du dépôt Hugging Face et le renvoie en DataFrame.

    Args:
        fichier_distant: chemin du fichier dans le dépôt, par exemple
            ``"data_cleaned/Airline.csv"``.
    """
    logger.info("Téléchargement de %s depuis %s", fichier_distant, DEPOT_HUGGING_FACE)
    jeu = load_dataset(DEPOT_HUGGING_FACE, data_files=fichier_distant, split="train")
    return jeu.to_pandas()


def sauvegarder_csv(donnees: pd.DataFrame, chemin: Path) -> None:
    """Enregistre un DataFrame en CSV en créant le dossier parent si besoin."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    donnees.to_csv(chemin, index=False)
    logger.info("%d lignes enregistrées dans %s", len(donnees), chemin)
