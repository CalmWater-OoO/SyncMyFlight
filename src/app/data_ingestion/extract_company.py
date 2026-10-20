import os
import pandas as pd
from datasets import load_dataset

base_compagnies = load_dataset("Algo0o/flight_delay", data_files="data_cleaned/Carriers.csv", split="train")

donnees = base_compagnies.to_pandas()

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_export = os.path.join(chemin_script, "..", "..", "..", "data", "raw", "compagnies.csv")

donnees.to_csv(chemin_export, index=False)
print("Table des compagnies extraite avec succès.")

