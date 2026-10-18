import os
import sys
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

chemin_script = os.path.dirname(os.path.abspath(__file__))
chemin_env = os.path.join(chemin_script, "..", "..", "config", "variables.env")

load_dotenv(chemin_env)

serveur = os.getenv("DATABRICKS_SERVER_HOSTNAME")
chemin = os.getenv("DATABRICKS_HTTP_PATH")
jeton = os.getenv("DATABRICKS_TOKEN")

print("Test de lecture du serveur :", serveur)

if serveur is None:
    print("Erreur : Le script ne trouve pas les mots de passe.")
    sys.exit()

connexion = sql.connect(
    server_hostname=serveur,
    http_path=chemin,
    access_token=jeton
)

# Remplace la ligne suivante par le chemin exact copié depuis Databricks
requete = "SELECT * FROM groupbwt_airport_flight_delay_schedule_change_dataset.flights.flights"

curseur = connexion.cursor()
curseur.execute(requete)
lignes = curseur.fetchall()
colonnes = [colonne[0] for colonne in curseur.description]

donnees = pd.DataFrame(lignes, columns=colonnes)
curseur.close()

chemin_export = os.path.join(chemin_script, "..", "..", "data", "raw", "vols_bruts.csv")
donnees.to_csv(chemin_export, index=False)
connexion.close()

print("Extraction validée et avertissement corrigé.")