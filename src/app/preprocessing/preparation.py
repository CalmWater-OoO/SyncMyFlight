"""Préparation des données et ingénierie des caractéristiques.

Ce module extrait les vols depuis la vue ``vue_vols_complets``, les nettoie,
crée la variable cible et les caractéristiques, puis enregistre le jeu
d'entraînement au format Parquet. Il fournit aussi le préprocesseur
scikit-learn, qui doit être ajusté uniquement sur le jeu d'entraînement
(dans l'étape de modélisation) pour éviter toute fuite de données.

Exécution depuis la racine du projet :
    uv run python src/app/preprocessing/preparation.py
"""

import logging
from typing import Final

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sqlalchemy import Engine, create_engine

from app.config.constants import SEUIL_RETARD_MINUTES, URL_BDD
from app.config.paths import FICHIER_ENTRAINEMENT

logger = logging.getLogger(__name__)

# Colonnes extraites de la vue : on ne charge que le nécessaire pour limiter la mémoire
COLONNES_SQL: Final[list[str]] = [
    "FL_DATE",
    "OP_UNIQUE_CARRIER",
    "ORIGIN",
    "DEST",
    "CRS_DEP_TIME",
    "DISTANCE",
    "ARR_DELAY",
    "CANCELLED",
    "DIVERTED",
    "t2m_C",
    "v10",
    "snc",
]

COLONNE_CIBLE: Final[str] = "RETARD_15"
COLONNES_METEO: Final[list[str]] = ["t2m_C", "v10", "snc"]
COLONNES_CATEGORIELLES_FAIBLES: Final[list[str]] = ["OP_UNIQUE_CARRIER"]
COLONNES_CATEGORIELLES_FORTES: Final[list[str]] = ["ORIGIN", "DEST"]
COLONNES_NUMERIQUES: Final[list[str]] = [
    "DISTANCE",
    *COLONNES_METEO,
    "MOIS",
    "JOUR_SEMAINE",
    "HEURE_DEP",
]
COLONNES_A_SUPPRIMER: Final[list[str]] = [
    "ARR_DELAY",
    "CRS_DEP_TIME",
    "FL_DATE",
    "CANCELLED",
    "DIVERTED",
]


def charger_vols(moteur: Engine) -> pd.DataFrame:
    """Extrait l'ensemble des vols depuis la vue consolidée."""
    colonnes = ", ".join(f'"{colonne}"' for colonne in COLONNES_SQL)
    requete = f"SELECT {colonnes} FROM public.vue_vols_complets;"
    logger.info("Chargement des vols depuis PostgreSQL")
    return pd.read_sql(requete, moteur)


def filtrer_vols_exploites(vols: pd.DataFrame) -> pd.DataFrame:
    """Conserve les vols ni annulés ni déroutés, dont le retard d'arrivée est connu."""
    masque = (vols["CANCELLED"] == 0) & (vols["DIVERTED"] == 0)
    return vols.loc[masque].dropna(subset=["ARR_DELAY"]).copy()


def creer_caracteristiques(vols: pd.DataFrame) -> pd.DataFrame:
    """Crée la variable cible et les caractéristiques temporelles."""
    vols = vols.copy()
    vols[COLONNE_CIBLE] = (vols["ARR_DELAY"] >= SEUIL_RETARD_MINUTES).astype(int)

    dates = pd.to_datetime(vols["FL_DATE"])
    vols["MOIS"] = dates.dt.month
    vols["JOUR_SEMAINE"] = dates.dt.dayofweek
    vols["HEURE_DEP"] = vols["CRS_DEP_TIME"] // 100
    return vols


def imputer_meteo(vols: pd.DataFrame) -> pd.DataFrame:
    """Remplace les valeurs météo manquantes par la médiane de chaque variable."""
    vols = vols.copy()
    vols[COLONNES_METEO] = vols[COLONNES_METEO].fillna(vols[COLONNES_METEO].median())
    return vols


def preparer_donnees(vols: pd.DataFrame) -> pd.DataFrame:
    """Enchaîne le filtrage, la création des caractéristiques et l'imputation."""
    vols = filtrer_vols_exploites(vols)
    vols = creer_caracteristiques(vols)
    vols = imputer_meteo(vols)
    return vols.drop(columns=COLONNES_A_SUPPRIMER)


def configurer_preprocesseur() -> ColumnTransformer:
    """Construit le préprocesseur scikit-learn (encodage et normalisation).

    Le préprocesseur n'est pas ajusté ici : il doit l'être sur le seul jeu
    d'entraînement, dans un ``Pipeline``, car le ``TargetEncoder`` utilise la cible.
    """
    return ColumnTransformer(
        transformers=[
            (
                "compagnies",
                OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"),
                COLONNES_CATEGORIELLES_FAIBLES,
            ),
            ("aeroports", TargetEncoder(cv=5, smooth="auto"), COLONNES_CATEGORIELLES_FORTES),
            ("numeriques", StandardScaler(), COLONNES_NUMERIQUES),
        ],
        remainder="drop",
    )


def main() -> None:
    """Prépare le jeu d'entraînement et l'enregistre au format Parquet."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    moteur = create_engine(URL_BDD)
    try:
        vols_bruts = charger_vols(moteur)
    finally:
        moteur.dispose()
    logger.info("Lignes extraites : %d", len(vols_bruts))

    jeu_entrainement = preparer_donnees(vols_bruts)

    FICHIER_ENTRAINEMENT.parent.mkdir(parents=True, exist_ok=True)
    jeu_entrainement.to_parquet(FICHIER_ENTRAINEMENT, index=False, engine="pyarrow")

    logger.info(
        "Jeu d'entraînement enregistré : %d lignes, %d colonnes -> %s",
        *jeu_entrainement.shape,
        FICHIER_ENTRAINEMENT,
    )
    logger.info(
        "Proportion de vols retardés : %.2f %%", jeu_entrainement[COLONNE_CIBLE].mean() * 100
    )


if __name__ == "__main__":
    main()
