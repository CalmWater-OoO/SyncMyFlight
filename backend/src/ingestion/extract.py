import os
import pandas as pd
from datasets import load_dataset

base = load_dataset("Algo0o/flight_delay", data_files="data_cleaned/Airline.csv", split="train")

donnees = base.to_pandas()

donnees["FL_DATE"] = pd.to_datetime(donnees["FL_DATE"])
donnees["MOIS"] = donnees["FL_DATE"].dt.month

echantillon = donnees.groupby("MOIS").sample(n=41666, random_state=42)

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_export = os.path.join(chemin_script, "..", "..", "data", "raw", "echantillon_complet_2025.csv")

echantillon.to_csv(chemin_export, index=False)
print("Base stratifiee avec toutes les colonnes generee.")