import os
import pandas as pd

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_vols = os.path.join(chemin_script, "..", "..", "data", "raw", "vols_bruts.csv")
chemin_meteo = os.path.join(chemin_script, "..", "..", "data", "raw", "meteo_complete.csv")

vols = pd.read_csv(chemin_vols)
meteo = pd.read_csv(chemin_meteo)

# Conversion au format date
meteo["time"] = pd.to_datetime(meteo["time"])
vols["scheduled_time"] = pd.to_datetime(vols["scheduled_time"])

# Arrondi de l'heure du vol à l'heure pile
vols["heure_arrondie"] = vols["scheduled_time"].dt.floor("h")

# Fusion des deux tables
vols_enrichis = pd.merge(
    vols,
    meteo,
    left_on=["departure_airport", "heure_arrondie"],
    right_on=["code_aeroport", "time"],
    how="left"
)

# Sauvegarde du résultat
chemin_export = os.path.join(chemin_script, "..", "..", "data", "interim", "vols_avec_meteo.csv")
vols_enrichis.to_csv(chemin_export, index=False)

nb_avec_meteo = vols_enrichis["time"].notna().sum()
if nb_avec_meteo == 0:
    print("Avertissement : aucune correspondance météo. Vérifiez le recouvrement des dates.")
else:
    print(f"Jointure validée : météo associée à {nb_avec_meteo} vols.")