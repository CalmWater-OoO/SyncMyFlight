"""Extraction des relevés météorologiques.

Exécution depuis la racine du projet :
    uv run python src/app/data_ingestion/extract_meteo.py
"""

import logging

from app.config.paths import FICHIER_METEO
from app.data_ingestion.telechargement import sauvegarder_csv, telecharger_table


def main() -> None:
    """Télécharge la table météo et l'enregistre dans ``data/raw``."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    sauvegarder_csv(telecharger_table("data_cleaned/Weather.csv"), FICHIER_METEO)


if __name__ == "__main__":
    main()
