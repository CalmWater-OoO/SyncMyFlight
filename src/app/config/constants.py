"""Constantes partagées du projet."""

import os
from typing import Final

# Base de données : la variable d'environnement DATABASE_URL est prioritaire.
URL_BDD_PAR_DEFAUT: Final[str] = "postgresql+psycopg://postgres:password@localhost:5432/db_vols"
URL_BDD: Final[str] = os.getenv("DATABASE_URL", URL_BDD_PAR_DEFAUT)

# Source des données brutes (Hugging Face)
DEPOT_HUGGING_FACE: Final[str] = "Algo0o/flight_delay"

# Échantillonnage stratifié des vols : nombre de vols tirés par mois
TAILLE_ECHANTILLON_PAR_MOIS: Final[int] = 41_666
GRAINE_ALEATOIRE: Final[int] = 42

# Seuil (en minutes) au-delà duquel un vol est considéré comme retardé
SEUIL_RETARD_MINUTES: Final[int] = 15
