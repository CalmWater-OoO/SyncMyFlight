import os
import pandas as pd
import airportsdata
from meteostat import Stations, Hourly

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_vols = os.path.join(chemin_script, "..", "..", "data", "raw", "vols_bruts.csv")

vols = pd.read_csv(chemin_vols)

# Les vols sont horodatés par scheduled_time et identifient le départ en IATA.
aeroports = vols["departure_airport"].dropna().astype(str).str.upper().unique()
horaires = pd.to_datetime(vols["scheduled_time"], errors="coerce").dropna()
if horaires.empty:
    raise ValueError("Aucune heure de vol valide dans la colonne 'scheduled_time'.")

debut = horaires.min().floor("h").to_pydatetime()
fin = (horaires.max().floor("h") + pd.Timedelta(hours=1)).to_pydatetime()
correspondance_iata = airportsdata.load("IATA")

toutes_les_meteos = []
stations = Stations()
toutes_les_stations = stations.fetch()

for code in aeroports:
    aeroport = correspondance_iata.get(code)
    code_icao = aeroport.get("icao") if aeroport else None
    if not code_icao:
        print(f"Aucun code ICAO trouvé pour {code}; aéroport ignoré.")
        continue

    station_trouvee = toutes_les_stations[toutes_les_stations["icao"] == code_icao]
    
    if not station_trouvee.empty:
        id_station = station_trouvee.index[0]
        meteo_aeroport = Hourly(id_station, debut, fin)
        df_meteo = meteo_aeroport.fetch()
        if df_meteo.empty:
            print(f"Aucune observation météo disponible pour {code}.")
            continue
        
        df_meteo = df_meteo.reset_index()
        df_meteo["code_aeroport"] = code
        toutes_les_meteos.append(df_meteo)
    else:
        print(f"Aucune station Meteostat trouvée pour {code} ({code_icao}).")

# Regroupe toutes les données dans une seule grande table
if not toutes_les_meteos:
    raise RuntimeError("Aucune donnée météo extraite pour les aéroports de départ.")

meteo_complete = pd.concat(toutes_les_meteos)

chemin_export = os.path.join(chemin_script, "..", "..", "data", "raw", "meteo_complete.csv")
meteo_complete.to_csv(chemin_export, index=False)
print(f"Météo extraite pour {meteo_complete['code_aeroport'].nunique()} aéroports : {chemin_export}")