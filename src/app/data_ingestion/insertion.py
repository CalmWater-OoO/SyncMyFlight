import os
import pandas as pd
from sqlalchemy import create_engine

chemin_script = os.path.dirname(os.path.abspath(__file__))

# Connexion à PostgreSQL
moteur = create_engine('postgresql://postgres:password@localhost:5432/db_vols')

# Lecture des fichiers CSV
vols = pd.read_csv(os.path.join(chemin_script, "..", "..", "..", "data", "raw", "echantillon_complet_2025.csv"))
compagnies = pd.read_csv(os.path.join(chemin_script, "..", "..", "..", "data", "raw", "compagnies.csv"))
meteo = pd.read_csv(os.path.join(chemin_script, "..", "..", "..", "data", "raw", "meteo_complete.csv"))

# Insertion sous forme de tables relationnelles
vols.to_sql('table_vols', moteur, if_exists='replace', index=False)
compagnies.to_sql('table_compagnies', moteur, if_exists='replace', index=False)
meteo.to_sql('table_meteo', moteur, if_exists='replace', index=False)

print("Insertion des trois tables réussie dans PostgreSQL.")

