import pandas as pd
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
esercizio_1_path = root_dir / "ESERCIZIO 1"
if str(esercizio_1_path) not in sys.path:
    sys.path.insert(0, str(esercizio_1_path))

from unione import normalizza

df_a = normalizza(pd.read_csv("OPERATORE A/Corse_Torino_LIME.csv"), "LIME")
df_b = normalizza(pd.read_csv("OPERATORE B/Corse_Torino_VOID.csv"), "VOID")
df_c = normalizza(pd.read_csv("OPERATORE C/Corse_Torino_BIRD.csv"), "BIRD")

data_all = pd.concat([df_a, df_b, df_c], ignore_index=True)
data_all=data_all.drop(columns=["ID_ORGANIZZAZIONE"], errors="ignore")

def estrai_percorso(df_raw, operatore):
    if "PERCORSO" not in df_raw.columns:
        return pd.DataFrame()
    return df_raw[["ID_VEICOLO", "DATAORA_INIZIO", "DATAORA_FINE", "PERCORSO"]].assign(OPERATORE=operatore)

percorso_a = estrai_percorso(pd.read_csv("OPERATORE A/Corse_Torino_LIME.csv"), "LIME")
percorso_b = estrai_percorso(pd.read_csv("OPERATORE B/Corse_Torino_VOID.csv"), "VOID")
percorso_c = estrai_percorso(pd.read_csv("OPERATORE C/Corse_Torino_BIRD.csv"), "BIRD")

percorso_all = pd.concat([percorso_a, percorso_b, percorso_c], ignore_index=True)
percorso_all.to_csv("Corse_Torino_PERCORSO.csv", index=False)


print(data_all.head())
print(data_all.info())
print(data_all.columns)