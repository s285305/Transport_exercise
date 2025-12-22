import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

cols_finali = [
    "ID_ORGANIZZAZIONE",
    "ID_VEICOLO",
    "DATAORA_INIZIO",
    "DATAORA_FINE",
    "LATITUDINE_INIZIO_CORSA",
    "LONGITUTIDE_INIZIO_CORSA",
    "LATITUDINE_FINE_CORSA",
    "LONGITUTIDE_FINE_CORSA",
    # "PERCORSO",   # la gestiamo separata
    "DISTANZA_KM",
    "DURATA_MIN",
    "RISERVATO",
    "BATTERIA_INIZIO_CORSA",
    "BATTERIA_FINE_CORSA",
    "OPERATORE",
]

def normalizza(df, operatore):
    # rinomina colonne specifiche per operatore
    if operatore == "VOID":
        df = df.rename(columns={
            "Targa veicolo": "ID_VEICOLO",
            "Data inizio corsa": "DATAORA_INIZIO",
            "Data fine corsa": "DATAORA_FINE",
            "Lat inizio corsa_coordinate": "LATITUDINE_INIZIO_CORSA",
            "Lon inizio corsa_coordinate": "LONGITUTIDE_INIZIO_CORSA",
            "Lat fine corsa_coordinate": "LATITUDINE_FINE_CORSA",
            "Lon fine corsa_coordinate": "LONGITUTIDE_FINE_CORSA",
            "KM Tot": "DISTANZA_KM",
            "Tempo Tot": "DURATA_MIN",
            "Prenotazione": "RISERVATO",
            "Batteria inizio": "BATTERIA_INIZIO_CORSA",
            "Batteria fine": "BATTERIA_FINE_CORSA",
        })
        df["ID_ORGANIZZAZIONE"] = pd.NA

    elif operatore == "BIRD":
        df = df.rename(columns={
            "ID_VEICOLO": "ID_VEICOLO",
            "DATAORA_INIZIO": "DATAORA_INIZIO",
            "DATAORA_FINE": "DATAORA_FINE",
            "LATITUDINE_INIZIO_CORSA": "LATITUDINE_INIZIO_CORSA",
            "LONGITUTIDE_INIZIO_CORSA": "LONGITUTIDE_INIZIO_CORSA",
            "LATITUDINE_FINE_CORSA": "LATITUDINE_FINE_CORSA",
            "LONGITUTIDE_FINE_CORSA": "LONGITUTIDE_FINE_CORSA",
            "DISTANZA_KM": "DISTANZA_KM",
            "DURATA_MIN": "DURATA_MIN",
            "RISERVATO": "RISERVATO",
        })
        df["ID_ORGANIZZAZIONE"] = pd.NA
        df["BATTERIA_INIZIO_CORSA"] = pd.NA
        df["BATTERIA_FINE_CORSA"] = pd.NA

    elif operatore == "LIME":
        
        df = df.rename(columns={
            "ID_VEICOLO": "ID_VEICOLO",
            "DATAORA_INIZIO": "DATAORA_INIZIO",
            "DATAORA_FINE": "DATAORA_FINE",
            "LATITUDINE_INIZIO_CORSA": "LATITUDINE_INIZIO_CORSA",
            "LONGITUTIDE_INIZIO_CORSA": "LONGITUTIDE_INIZIO_CORSA",
            "LATITUDINE_FINE_CORSA": "LATITUDINE_FINE_CORSA",
            "LONGITUTIDE_FINE_CORSA": "LONGITUTIDE_FINE_CORSA",
            "DISTANZA_KM": "DISTANZA_KM",
            "DURATA_MIN": "DURATA_MIN",
            "RISERVATO": "RISERVATO",
            "BATTERIA_INIZIO_CORSA": "BATTERIA_INIZIO_CORSA",
            "BATTERIA_FINE_CORSA": "BATTERIA_FINE_CORSA",
            "ID_ORGANIZZAZIONE": "ID_ORGANIZZAZIONE",
        })

     # rimuovi PERCORSO dal main
    df = df.drop(columns=["PERCORSO"], errors="ignore")

    # aggiungi eventuali colonne mancanti
    for c in cols_finali:
        if c not in df.columns:
            df[c] = pd.NA

    # ordina le colonne nello stesso ordine
    return df[cols_finali]

df_a = normalizza(pd.read_csv("OPERATORE A/Corse_Torino_LIME.csv"), "LIME")
df_b = normalizza(pd.read_csv("OPERATORE B/Corse_Torino_VOID.csv"), "VOID")
df_c = normalizza(pd.read_csv("OPERATORE C/Corse_Torino_BIRD.csv"), "BIRD")

data_all = pd.concat([df_a, df_b, df_c], ignore_index=True)
data_all=data_all.drop(columns=["ID_ORGANIZZAZIONE"], errors="ignore")

def parse_datetime_generic(data_Str):

    data_Str["DATAORA_INIZIO"] = pd.to_datetime(data_Str["DATAORA_INIZIO"], format='mixed', yearfirst=True)
    data_Str["DATAORA_FINE"] = pd.to_datetime(data_Str["DATAORA_FINE"], format='mixed', yearfirst=True)
    return data_Str

def parse_datetime_void(data_Str):
    data_Str["DATAORA_INIZIO"] = pd.to_datetime(data_Str["DATAORA_INIZIO"], format='%Y%m%d%H%M%S')
    data_Str["DATAORA_FINE"] = pd.to_datetime(data_Str["DATAORA_FINE"], format='%Y%m%d%H%M%S')
    return data_Str

if 'VOID' in data_all['OPERATORE'].values:
    mask_void = data_all['OPERATORE'] == 'VOID'
    data_void = data_all[mask_void]
    data_non_void = data_all[~mask_void]

    data_void = parse_datetime_void(data_void)
    data_non_void = parse_datetime_generic(data_non_void)

    data_all = pd.concat([data_void, data_non_void], ignore_index=True)


print("-" * 30)
print(f"REPORT PULIZIA DATI")
print(f"Righe totali iniziali: {len(data_all)}")

# 1. REPORT "BAD DATA" E PULIZIA
# Teniamo traccia di quanti dati rimuoviamo per ogni step
initial_count = len(data_all)

# A. Rimozione Null essenziali
data_all = data_all.dropna(subset=["ID_VEICOLO", "DATAORA_INIZIO", "DATAORA_FINE"])
rows_after_null = len(data_all)
print(f"Removed due to missing values (Nulls): {initial_count - rows_after_null}")

# B. Incoerenze temporali (Fine < Inizio)
data_all = data_all[data_all["DATAORA_FINE"] > data_all["DATAORA_INIZIO"]]
rows_after_time = len(data_all)
print(f"Removed due to time inconsistencies (End < Start): {rows_after_null - rows_after_time}")

# C. Trasformazione unità di misura
# Assumiamo DURATA in MINUTI -> trasformiamo in SECONDI
data_all["DURATA_SEC"] = data_all["DURATA_MIN"] * 60 
# Assumiamo DISTANZA in KM -> trasformiamo in METRI
data_all["DISTANZA_METRI"] = data_all["DISTANZA_KM"] * 1000

# Evitiamo divisioni per zero
data_all = data_all[data_all["DURATA_SEC"] > 0]

# Calcolo velocità in m/s
data_all["SPEED_MS"] = data_all["DISTANZA_METRI"] / data_all["DURATA_SEC"]

# D. Filtro Velocità (Tra 2 km/h e 25 km/h)
# 25 km/h = ~6.94 m/s (Limite legale monopattini spesso)
# 2 km/h = ~0.56 m/s (Sotto è probabilmente camminata o errore GPS)
rows_before_speed = len(data_all)
data_all = data_all[(data_all["SPEED_MS"] <= 6.94) & (data_all["SPEED_MS"] >= 0.56)]
rows_after_speed = len(data_all)
print(f"Removed due to unrealistic speed (<2km/h or >25km/h): {rows_before_speed - rows_after_speed}")

# E. Filtro Location (Coordinate fuori Torino)
# Approssimazione box Torino (latitudine e longitudine) 
rows_before_location = len(data_all)
data_all = data_all[
    (data_all["LATITUDINE_INIZIO_CORSA"] >= 44.9) & (data_all["LATITUDINE_INIZIO_CORSA"] <= 45.1) &
    (data_all["LONGITUTIDE_INIZIO_CORSA"] >= 7.5) & (data_all["LONGITUTIDE_INIZIO_CORSA"] <= 7.8) &
    (data_all["LATITUDINE_FINE_CORSA"] >= 44.9) & (data_all["LATITUDINE_FINE_CORSA"] <= 45.1) &
    (data_all["LONGITUTIDE_FINE_CORSA"] >= 7.5) & (data_all["LONGITUTIDE_FINE_CORSA"] <= 7.8)
]
rows_after_location = len(data_all)
print(f"Removed due to out-of-bounds locations (outside Torino area): {rows_before_location - rows_after_location}")

# F Rimozione duplicati esatti
rows_before_duplicates = len(data_all)
data_all = data_all.drop_duplicates()
rows_after_duplicates = len(data_all)
print(f"Removed exact duplicate rows: {rows_before_duplicates - rows_after_duplicates}")

print(f"Righe totali FINALI dopo pulizia: {len(data_all)}")
print("-" * 30)

# ---------------------------------------------------------
# 2. MOBILITY TRENDS (Settimana, Mese, Anno)
# ---------------------------------------------------------
print("\nGenerazione grafici trend temporali...")

# Creiamo colonne di supporto temporale
data_all['Year'] = data_all['DATAORA_INIZIO'].dt.year
data_all['Month_Year'] = data_all['DATAORA_INIZIO'].dt.to_period('M')
data_all['Week_Year'] = data_all['DATAORA_INIZIO'].dt.to_period('W')

# Aggregazione
trend_year = data_all.groupby('Year').size()
trend_month = data_all.groupby('Month_Year').size()
trend_week = data_all.groupby('Week_Year').size()

# Visualizzazione (Esempio per Mese)
plt.figure(figsize=(12, 6))
trend_month.plot(kind='line', marker='o', color='b')
plt.title("Trend Mobilità Mensile")
plt.xlabel("Mese")
plt.ylabel("Numero Viaggi")
plt.grid(True)
plt.show()

#week plot
plt.figure(figsize=(12, 6))
trend_week.plot(kind='line', marker='o', color='b')
plt.title("Trend Mobilità Settimanale")
plt.xlabel("Settimana")
plt.ylabel("Numero Viaggi")
plt.grid(True)
plt.show()

#♠year plot
plt.figure(figsize=(12, 6))
trend_year.plot(kind='line', marker='o', color='b')
plt.title("Trend Mobilità Annuale")
plt.xlabel("Anno")
plt.ylabel("Numero Viaggi")
plt.grid(True)
plt.show()


# ---------------------------------------------------------
# 3. ANALISI VEICOLI UNICI E PATTERN
# ---------------------------------------------------------
veicoli_per_operatore = data_all.groupby('OPERATORE')['ID_VEICOLO'].nunique()
print("\n--- Numero veicoli unici per Operatore ---")
print(veicoli_per_operatore)

# Pattern settimanali e orari (Heatmap o grafico a linee)
data_all['DayOfWeek'] = data_all['DATAORA_INIZIO'].dt.day_name()
data_all['Hour'] = data_all['DATAORA_INIZIO'].dt.hour

# Ordine giorni settimana
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
data_all['DayOfWeek'] = pd.Categorical(data_all['DayOfWeek'], categories=days_order, ordered=True)

# Pivot table per heatmap (Giorno vs Ora)
pivot_usage = data_all.groupby(['DayOfWeek', 'Hour']).size().unstack()

plt.figure(figsize=(12, 6))

try:
    sns.heatmap(pivot_usage, cmap="YlOrRd", linewidths=.5)
    plt.title("Intensità utilizzo: Giorno della settimana vs Ora")
except NameError:
    print("Error")
plt.show()


output_path = "Corse_Torino_TUTTI.csv"
data_all.to_csv(output_path, index=False)