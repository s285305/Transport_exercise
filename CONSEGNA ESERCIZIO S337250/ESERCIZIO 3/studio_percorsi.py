import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import ast

# 1. Caricamento Dati
print("1. Caricamento CSV...")
df = pd.read_csv('Corse_Torino_PERCORSO.csv')

# Drop rows where percorso is outside Torino area
print("Filtraggio righe fuori dall'area di Torino...")
print(f"Righe iniziali: {len(df)}")
df = df[df['PERCORSO'].str.contains('7.6') & df['PERCORSO'].str.contains('45.0')]
print(f"{len(df)} righe dopo il filtraggio per l'area di Torino.")

# 2. Pre-processing Date
print("2. Elaborazione temporale...")
df['DATAORA_INIZIO'] = pd.to_datetime(df['DATAORA_INIZIO'], format='mixed')
df['DATE'] = df['DATAORA_INIZIO'].dt.date  # Solo la data (es. 2024-01-15)
df['MONTH'] = df['DATAORA_INIZIO'].dt.month
df['WEEKDAY'] = df['DATAORA_INIZIO'].dt.dayofweek # 0=Lun, 6=Dom

# -------------------------------------------------------------------------
# ALGORITMO DI SELEZIONE DEL "GIORNO TIPO" (Metodo FHWA/AWT simplified)
# -------------------------------------------------------------------------
print("3. Analisi statistica per trovare il 'Giorno Rappresentativo' di ogni mese...")

# Filtriamo solo Martedì (1), Mercoledì (2), Giovedì (3)
# Questo rimuove il "rumore" di weekend, lunedì e venerdì.
df_midweek = df[df['WEEKDAY'].isin([1, 2, 3])].copy()

# Se in un mese non ci sono abbastanza dati Mar-Gio, usiamo tutti i feriali (0-4)
if df_midweek.empty:
    df_midweek = df[df['WEEKDAY'] < 5].copy()

# Calcoliamo quanti viaggi ci sono per ogni singolo giorno specifico
daily_counts = df_midweek.groupby(['MONTH', 'DATE']).size().reset_index(name='TRIPS')

# Calcoliamo la MEDIA dei viaggi per ogni MESE
monthly_means = daily_counts.groupby('MONTH')['TRIPS'].mean().reset_index(name='MEAN_TRIPS')

selected_dates = []

print("\n--- GIORNI SELEZIONATI (I più vicini alla media mensile) ---")
for index, row in monthly_means.iterrows():
    m = row['MONTH']
    avg = row['MEAN_TRIPS']
    
    # Prendiamo i giorni di quel mese
    days_in_month = daily_counts[daily_counts['MONTH'] == m].copy()
    
    # Calcoliamo la differenza assoluta rispetto alla media
    # (|Viaggi_Giorno_X - Media_Mese|)
    days_in_month['DIFF'] = (days_in_month['TRIPS'] - avg).abs()
    
    # Troviamo il giorno con la differenza minima (il più rappresentativo)
    best_day_row = days_in_month.loc[days_in_month['DIFF'].idxmin()]
    best_date = best_day_row['DATE']
    
    print(f"Mese {int(m)}: Giorno {best_date} (Viaggi: {best_day_row['TRIPS']} vs Media: {int(avg)})")
    selected_dates.append(best_date)

# -------------------------------------------------------------------------

# 3. Filtriamo il dataset originale tenendo SOLO i giorni selezionati
print(f"\n4. Filtraggio dataset su {len(selected_dates)} giorni rappresentativi...")
df_final = df[df['DATE'].isin(selected_dates)].copy()

# 4. Parsing Geometria (Funzione Robusta)
def parse_geom(geom_str):
    try:
        if pd.isna(geom_str): return None
        data = ast.literal_eval(geom_str)
        if isinstance(data, dict): coords = data.get('coordinates', [])
        elif isinstance(data, list): coords = data
        else: return None
        
        if len(coords) >= 2: return LineString(coords)
    except: return None

print("5. Generazione geometrie...")
df_final['geometry'] = df_final['PERCORSO'].apply(parse_geom)
df_final = df_final.dropna(subset=['geometry'])

# 5. Salvataggio GeoPackage
# Aggiungiamo una colonna stringa per la data per facilitare l'uso in QGIS
df_final['DATA_RIF'] = df_final['DATE'].astype(str)

gdf = gpd.GeoDataFrame(
    df_final[['ID_VEICOLO', 'OPERATORE', 'MONTH', 'DATA_RIF', 'geometry']], 
    geometry='geometry', 
    crs="EPSG:4326"
)

output_file = "Torino_Giorni_Rappresentativi.gpkg"
print(f"6. Salvataggio in {output_file}...")

# Salviamo tutto in un unico layer
gdf.to_file(output_file, driver="GPKG", layer="giorni_tipo")

print("Finito! Il file contiene solo 1 giorno per mese (quello statisticamente più medio).")