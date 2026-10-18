import os
import pandas as pd
from datasets import load_dataset

base_meteo = load_dataset("Algo0o/flight_delay", data_files="data_cleaned/Weather.csv", split="train")

donnees_meteo = base_meteo.to_pandas()

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_export = os.path.join(chemin_script, "..", "..", "data", "raw", "meteo_complete.csv")

donnees_meteo.to_csv(chemin_export, index=False)
print("Table meteo importee avec succes.")