"""Chargement des données brutes dans PostgreSQL.

Ce module lit les fichiers CSV de ``data/raw``, les insère sous forme de tables
relationnelles, crée les contraintes d'intégrité puis la vue consolidée
``vue_vols_complets`` utilisée par l'étape de préparation des données.

Exécution depuis la racine du projet :
    uv run python src/app/data_ingestion/insertion.py
"""

import logging
from pathlib import Path
from typing import Final

import pandas as pd
from sqlalchemy import Engine, create_engine, text

from app.config.constants import URL_BDD
from app.config.paths import FICHIER_COMPAGNIES, FICHIER_METEO, FICHIER_VOLS_BRUTS

FICHIER_VUE: Final[Path] = Path(__file__).resolve().parent / "vue_vols_complets.sql"

# PostgreSQL accepte au plus 65 535 paramètres par requête : on garde une marge.
LIMITE_PARAMETRES: Final[int] = 60_000

# Correspondance table SQL -> fichier CSV, dans l'ordre d'insertion
TABLES_SOURCES: Final[dict[str, Path]] = {
    "table_compagnies": FICHIER_COMPAGNIES,
    "table_meteo": FICHIER_METEO,
    "table_vols": FICHIER_VOLS_BRUTS,
}

REQUETE_CLE_PRIMAIRE: Final[str] = """
    ALTER TABLE public.table_compagnies
    ADD PRIMARY KEY ("iata_code");
"""

REQUETE_CLE_ETRANGERE: Final[str] = """
    ALTER TABLE public.table_vols
    ADD CONSTRAINT fk_compagnie
    FOREIGN KEY ("OP_UNIQUE_CARRIER")
    REFERENCES public.table_compagnies ("iata_code");
"""

logger = logging.getLogger(__name__)


def creer_moteur() -> Engine:
    """Crée le moteur SQLAlchemy vers la base PostgreSQL du projet."""
    return create_engine(URL_BDD)


def supprimer_vue(moteur: Engine) -> None:
    """Supprime la vue consolidée, qui empêcherait le remplacement des tables."""
    with moteur.begin() as connexion:
        connexion.execute(text("DROP VIEW IF EXISTS public.vue_vols_complets;"))


def lire_csv(chemin: Path) -> pd.DataFrame:
    """Lit un fichier CSV.

    Raises:
        FileNotFoundError: si le fichier est absent.
    """
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")
    return pd.read_csv(chemin)


def inserer_table(donnees: pd.DataFrame, nom_table: str, moteur: Engine) -> None:
    """Insère un DataFrame dans PostgreSQL en remplaçant la table existante.

    Les lignes sont envoyées par paquets dont la taille dépend du nombre de
    colonnes, afin de respecter la limite de paramètres de PostgreSQL.
    """
    taille_paquet = max(1, LIMITE_PARAMETRES // len(donnees.columns))
    donnees.to_sql(
        nom_table,
        moteur,
        if_exists="replace",
        index=False,
        chunksize=taille_paquet,
        method="multi",
    )
    logger.info("%s : %d lignes insérées", nom_table, len(donnees))


def creer_contraintes_et_vue(moteur: Engine) -> None:
    """Crée la clé primaire, la clé étrangère et la vue consolidée en une transaction."""
    requete_vue = FICHIER_VUE.read_text(encoding="utf-8")
    with moteur.begin() as connexion:
        connexion.execute(text(REQUETE_CLE_PRIMAIRE))
        connexion.execute(text(REQUETE_CLE_ETRANGERE))
        connexion.execute(text(requete_vue))
    logger.info("Contraintes et vue public.vue_vols_complets créées")


def main() -> None:
    """Exécute le chargement complet de la base."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    moteur = creer_moteur()
    try:
        supprimer_vue(moteur)
        for nom_table, chemin in TABLES_SOURCES.items():
            inserer_table(lire_csv(chemin), nom_table, moteur)
        creer_contraintes_et_vue(moteur)
    finally:
        moteur.dispose()

    logger.info("Chargement de la base terminé")


if __name__ == "__main__":
    main()
