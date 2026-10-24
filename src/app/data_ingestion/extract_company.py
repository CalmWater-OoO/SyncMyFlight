"""Extraction de la table des compagnies aériennes.

Exécution depuis la racine du projet :
    uv run python src/app/data_ingestion/extract_company.py
"""

import logging

from app.config.paths import FICHIER_COMPAGNIES
from app.data_ingestion.telechargement import sauvegarder_csv, telecharger_table


def main() -> None:
    """Télécharge la table des compagnies et l'enregistre dans ``data/raw``."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    sauvegarder_csv(telecharger_table("data_cleaned/Carriers.csv"), FICHIER_COMPAGNIES)


if __name__ == "__main__":
    main()
