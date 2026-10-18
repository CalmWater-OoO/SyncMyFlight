from sqlalchemy import create_engine, text

moteur = create_engine('postgresql://postgres:password@localhost:5432/db_vols')

requete_fk = """
ALTER TABLE public.table_vols
ADD CONSTRAINT fk_compagnie
FOREIGN KEY ("OP_UNIQUE_CARRIER")
REFERENCES public.table_compagnies("iata_code");
"""

with moteur.connect() as connexion:
    connexion.execute(text(requete_fk))
    connexion.commit()

print("Clé étrangère créée avec succès.")