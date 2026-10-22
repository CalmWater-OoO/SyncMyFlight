"""Extraction des vols et constitution d'un échantillon stratifié par mois.

Exécution depuis la racine du projet :
    uv run python src/app/data_ingestion/extract.py
"""

import logging

import pandas as pd

from app.config.constants import GRAINE_ALEATOIRE, TAILLE_ECHANTILLON_PAR_MOIS
from app.config.paths import FICHIER_VOLS_BRUTS
from app.data_ingestion.telechargement import sauvegarder_csv, telecharger_table

logger = logging.getLogger(__name__)


def echantillonner_par_mois(vols: pd.DataFrame) -> pd.DataFrame:
    """Tire le même nombre de vols pour chaque mois, afin d'équilibrer les saisons."""
    vols = vols.copy()
    vols["FL_DATE"] = pd.to_datetime(vols["FL_DATE"])
    vols["MOIS"] = vols["FL_DATE"].dt.month
    return vols.groupby("MOIS").sample(n=TAILLE_ECHANTILLON_PAR_MOIS, random_state=GRAINE_ALEATOIRE)


def main() -> None:
    """Télécharge les vols, les échantillonne puis les enregistre dans ``data/raw``."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    vols = telecharger_table("data_cleaned/Airline.csv")
    sauvegarder_csv(echantillonner_par_mois(vols), FICHIER_VOLS_BRUTS)


if __name__ == "__main__":
    main()
