"""Module d'extraction complète, de préparation et d'encodage des caractéristiques."""

import os
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# 1. Configuration des chemins et constantes
REPERTOIRE_COURANT: Path = Path(__file__).resolve().parent
DOSSIER_DATA: Path = REPERTOIRE_COURANT.parents[1] / "data"
DOSSIER_PROCESSED: Path = DOSSIER_DATA / "processed"

URL_BDD: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:password@localhost:5432/db_vols"
)

# Liste stricte des colonnes à extraire depuis SQL pour alléger la RAM
COLONNES_SQL: list[str] = [
    '"FL_DATE"',
    '"OP_UNIQUE_CARRIER"',
    '"ORIGIN"',
    '"DEST"',
    '"CRS_DEP_TIME"',
    '"DISTANCE"',
    '"ARR_DELAY"',
    '"CANCELLED"',
    '"DIVERTED"',
    '"t2m_C"',
    '"v10"',
    '"snc"'
]


# 2. Fonctions modulaires
def charger_donnees_completes(moteur_sql: Engine) -> pd.DataFrame:
    """Extrait l'ensemble des vols depuis la vue SQL sans restriction de limite."""
    print("Chargement complet de la base depuis PostgreSQL (cela peut prendre quelques secondes)...")
    colonnes_texte: str = ", ".join(COLONNES_SQL)
    requete = """
    SELECT 
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
        "snc"
    FROM public.vue_vols_complets;
    """
    return pd.read_sql(requete, moteur_sql)


def preparer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les vols, traite les valeurs manquantes et génère les caractéristiques."""
    print("Filtrage et nettoyage des données en cours...")
    
    # Conservation exclusive des vols exploités
    df_filtre = df[(df["CANCELLED"] == 0) & (df["DIVERTED"] == 0)].copy()
    df_filtre = df_filtre.dropna(subset=["ARR_DELAY"])

    # Cible binaire (retard supérieur ou égal à 15 minutes)
    df_filtre["RETARD_15"] = (df_filtre["ARR_DELAY"] >= 15).astype(int)

    # Ingénierie temporelle
    df_filtre["FL_DATE"] = pd.to_datetime(df_filtre["FL_DATE"])
    df_filtre["MOIS"] = df_filtre["FL_DATE"].dt.month
    df_filtre["JOUR_SEMAINE"] = df_filtre["FL_DATE"].dt.dayofweek
    df_filtre["HEURE_DEP"] = df_filtre["CRS_DEP_TIME"] // 100

    # Imputation médiane des indicateurs météo
    colonnes_meteo: list[str] = ["t2m_C", "v10", "snc"]
    for col in colonnes_meteo:
        df_filtre[col] = df_filtre[col].fillna(df_filtre[col].median())

    # Retrait des colonnes sources devenues obsolètes
    colonnes_a_supprimer: list[str] = [
        "ARR_DELAY", "CRS_DEP_TIME", "FL_DATE", "CANCELLED", "DIVERTED"
    ]
    return df_filtre.drop(columns=colonnes_a_supprimer)


def configurer_preprocesseur() -> ColumnTransformer:
    """Définit le pipeline de transformation Scikit-Learn."""
    return ColumnTransformer(
        transformers=[
            ("compagnies", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), ["OP_UNIQUE_CARRIER"]),
            ("aeroports", TargetEncoder(cv=5, smooth="auto"), ["ORIGIN", "DEST"]),
            ("numeriques", StandardScaler(), ["DISTANCE", "t2m_C", "v10", "snc", "MOIS", "JOUR_SEMAINE", "HEURE_DEP"])
        ],
        remainder="drop"
    )


# 3. Exécution principale
def main() -> None:
    moteur: Engine = create_engine(URL_BDD)
    
    # 1. Extraction complète
    df_brut: pd.DataFrame = charger_donnees_completes(moteur)
    print(f"Lignes extraites brutes : {len(df_brut)}")

    # 2. Préparation
    base_preparee: pd.DataFrame = preparer_donnees(df_brut)

    # 3. Sauvegarde au format Parquet
    DOSSIER_PROCESSED.mkdir(parents=True, exist_ok=True)
    chemin_sortie: Path = DOSSIER_PROCESSED / "donnees_entrainement.parquet"
    base_preparee.to_parquet(chemin_sortie, index=False, engine="pyarrow")

    print(f"\nJeu complet préparé et enregistré : {base_preparee.shape[0]} lignes et {base_preparee.shape[1]} colonnes.")
    print(f"Proportion globale de vols retardés : {round(base_preparee['RETARD_15'].mean() * 100, 2)} %\n")

    # 4. Validation du préprocesseur sur l'ensemble complet
    preprocesseur: ColumnTransformer = configurer_preprocesseur()
    X = base_preparee.drop(columns=["RETARD_15"])
    y = base_preparee["RETARD_15"]

    print("Vérification de l'encodage sur l'ensemble de la base...")
    X_transforme = preprocesseur.fit_transform(X, y)
    print(f"Matrice encodée prête : {X_transforme.shape[0]} lignes et {X_transforme.shape[1]} variables numériques.")


if __name__ == "__main__":
    main()