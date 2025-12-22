import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely import wkt
from shapely.geometry import Point

# ---------------------------------------------------------
# 1. LOAD AND PREPARE DATA
# ---------------------------------------------------------
print("1. Loading Data...")
ZONES_FILE= "zone_statistiche_csv/zone_statistiche.csv" 

# A. Load Scooter Data
df = pd.read_csv("Corse_Torino_TUTTI.csv")
df['DATAORA_INIZIO'] = pd.to_datetime(df['DATAORA_INIZIO'])
df['DATAORA_FINE'] = pd.to_datetime(df['DATAORA_FINE'])

# B. Load Zones (Map)
try:
    zones_df = pd.read_csv(ZONES_FILE, sep=';', encoding='latin1')
except:
    zones_df = pd.read_csv(ZONES_FILE, sep=';', encoding='cp1252')

zones_df['geometry'] = zones_df['WKT_GEOM'].apply(wkt.loads)
zones_gdf = gpd.GeoDataFrame(zones_df, geometry='geometry')
zones_gdf.set_crs(epsg=3003, inplace=True)
zones_gdf = zones_gdf.to_crs(epsg=4326)

# ---------------------------------------------------------
# 2. CALCULATE PARKING DURATION
# ---------------------------------------------------------
print("2. Calculating Parking Durations (this may take a moment)...")

# Sort by Vehicle and Time to ensure trips are sequential
df.sort_values(by=['ID_VEICOLO', 'DATAORA_INIZIO'], inplace=True)

# Shift columns to get the "Previous End Time" for the same vehicle
df['PREV_END_TIME'] = df.groupby('ID_VEICOLO')['DATAORA_FINE'].shift(1)

# Calculate duration: Current Start - Previous End
df['PARKING_DURATION'] = df['DATAORA_INIZIO'] - df['PREV_END_TIME']

# Convert to minutes
df['PARKING_MINUTES'] = df['PARKING_DURATION'].dt.total_seconds() / 60

# Filter valid parking data
# 1. Remove NaN (First trip of a vehicle has no previous parking)
# 2. Remove negative values (Data errors where overlapping trips occur)
# 3. Optional: Cap huge outliers (e.g., > 24 hours might be maintenance or lost)
df_parking = df.dropna(subset=['PARKING_MINUTES'])
df_parking = df_parking[df_parking['PARKING_MINUTES'] > 0]
df_parking = df_parking[df_parking['PARKING_MINUTES'] < 1440] # Cap at 24 hours for analysis

print(f"   Calculated parking events: {len(df_parking)}")
print(f"   Average Parking Duration: {df_parking['PARKING_MINUTES'].mean():.2f} minutes")

# ---------------------------------------------------------
# 3. SPATIAL JOIN (Where did the parking happen?)
# ---------------------------------------------------------
print("3. Mapping Parking to Zones...")

# where the scooter was parked.
geometry_points = [Point(xy) for xy in zip(df_parking.LONGITUTIDE_INIZIO_CORSA, df_parking.LATITUDINE_INIZIO_CORSA)]
gdf_points = gpd.GeoDataFrame(df_parking, geometry=geometry_points, crs="EPSG:4326")

# Join with Zones
# Using 'DENOM' for the zone name
gdf_joined = gpd.sjoin(gdf_points, zones_gdf[['DENOM', 'geometry']], how="inner", predicate="within")

# ---------------------------------------------------------
# 4. AGGREGATE STATS PER ZONE
# ---------------------------------------------------------
# Calculate avg parking duration per zone
zone_stats = gdf_joined.groupby('DENOM')['PARKING_MINUTES'].mean().reset_index()
zone_stats.columns = ['DENOM', 'AVG_PARKING_MIN']

# Also calculate Trip Counts (Activity) for the overlap visualization
zone_activity = gdf_joined.groupby('DENOM').size().reset_index(name='TRIP_COUNT')

# Merge everything into the map
map_data = zones_gdf.merge(zone_stats, on='DENOM', how='left')
map_data = map_data.merge(zone_activity, on='DENOM', how='left').fillna(0)

# ---------------------------------------------------------
# 5. VISUALIZATION 1: Average Parking Duration Map
# ---------------------------------------------------------
print("4. Generating Parking Map...")

fig, ax = plt.subplots(1, 1, figsize=(12, 12))
map_data.plot(column='AVG_PARKING_MIN', 
              ax=ax, 
              legend=True, 
              cmap='Spectral_r', # Red = Long Parking, Blue = Short Parking
              legend_kwds={'label': "Average Parking Duration (Minutes)"},
              edgecolor='black', linewidth=0.3)

plt.title("Average E-Scooter Parking Duration by Zone")
plt.axis('off')
plt.show()


# ---------------------------------------------------------
# 5.  VISUALIZATION: Overlapping Trends
# ---------------------------------------------------------
print("5. Generating Overlapping Map...")

# A. PREPARE DATA 
gdf_joined['Hour'] = gdf_joined['DATAORA_INIZIO'].dt.hour
peak_data = gdf_joined[(gdf_joined['Hour'] >= 8) & (gdf_joined['Hour'] <= 10)]

# Aggregate
peak_stats = peak_data.groupby('DENOM').agg({
    'PARKING_MINUTES': 'mean',
    'ID_VEICOLO': 'count' # Trip Count
}).reset_index()
peak_stats.columns = ['DENOM', 'PEAK_AVG_PARKING', 'PEAK_TRIP_COUNT']

# Merge with map geometry
peak_map = zones_gdf.merge(peak_stats, on='DENOM', how='left').fillna(0)
# Calculate centroids for bubbles
peak_map['centroid'] = peak_map.geometry.centroid

# B. PLOT SETUP
fig, ax = plt.subplots(1, 1, figsize=(15, 15)) # Larger figure
ax.set_facecolor('#f5f5f5') # Light grey background for the whole plot area


peak_map.plot(column='PEAK_AVG_PARKING', 
              ax=ax, 
              cmap='magma', 
              alpha=0.8,   
              edgecolor='white', linewidth=0.3, 
              legend=True,
              legend_kwds={'label': "Avg Parking Duration (Minutes)", 
                           'orientation': "horizontal", 
                           'pad': 0.05, 'shrink': 0.6}
              )

# LAYER 2: Bubbles (Trip Origins)

max_trips = peak_map['PEAK_TRIP_COUNT'].max()
bubble_sizes = (peak_map['PEAK_TRIP_COUNT'] / max_trips) * 2000 # Scale factor

scatter = ax.scatter(
    peak_map['centroid'].x, 
    peak_map['centroid'].y, 
    s=bubble_sizes, 
    c='#08519c',      
    alpha=0.6,        
    edgecolor='white',
    linewidth=1,
    zorder=2          
)

# C. FINAL TOUCHES
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                              label='Trip Origin Volume (Morning Peak)',
                              markerfacecolor='#08519c', markersize=15, 
                              alpha=0.6, markeredgecolor='white')]
ax.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)

plt.title("Morning Peak Analysis (08:00 - 10:00)\nParking Duration (Background) vs. Trip Demand (Bubbles)", fontsize=14, pad=20)
plt.axis('off')
plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# 6. EXTRA: EVENING PEAK VISUALIZATION (The "Return Trip")
# ---------------------------------------------------------
print("6. Generating Evening Peak Map (17:00 - 20:00)...")

# A. PREPARE DATA (Evening Peak 17:00 - 20:00)
evening_data = gdf_joined[(gdf_joined['Hour'] >= 17) & (gdf_joined['Hour'] <= 20)]

# Aggregate statistics
evening_stats = evening_data.groupby('DENOM').agg({
    'PARKING_MINUTES': 'mean',
    'ID_VEICOLO': 'count' 
}).reset_index()
evening_stats.columns = ['DENOM', 'EV_AVG_PARKING', 'EV_TRIP_COUNT']

# Merge with map geometry
evening_map = zones_gdf.merge(evening_stats, on='DENOM', how='left').fillna(0)
evening_map['centroid'] = evening_map.geometry.centroid

# B. PLOT SETUP
fig, ax = plt.subplots(1, 1, figsize=(15, 15))
ax.set_facecolor('#f5f5f5')

# LAYER 1: Base Choropleth (Parking Duration)
evening_map.plot(column='EV_AVG_PARKING', 
              ax=ax, 
              cmap='magma', 
              alpha=0.8,   
              edgecolor='white', linewidth=0.3,
              legend=True,
              legend_kwds={'label': "Avg Parking Duration (Minutes) - Evening", 
                           'orientation': "horizontal", 
                           'pad': 0.05, 'shrink': 0.6}
              )

# LAYER 2: Bubbles (Trip Origins)
max_ev_trips = evening_map['EV_TRIP_COUNT'].max()
if max_ev_trips > 0:
    bubble_sizes_ev = (evening_map['EV_TRIP_COUNT'] / max_ev_trips) * 2000
else:
    bubble_sizes_ev = 0

scatter = ax.scatter(
    evening_map['centroid'].x, 
    evening_map['centroid'].y, 
    s=bubble_sizes_ev, 
    c='#08519c',     
    alpha=0.6,        
    edgecolor='white',
    linewidth=1,
    zorder=2
)

# C. TITLES AND LEGEND
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                              label='Trip Origin Volume (Evening Peak)',
                              markerfacecolor='#08519c', markersize=15, 
                              alpha=0.6, markeredgecolor='white')]
ax.legend(handles=legend_elements, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)

plt.title("Evening Commute Analysis (17:00 - 20:00)\nParking Duration (Background) vs. Trip Demand (Bubbles)", fontsize=14, pad=20)
plt.axis('off')
plt.tight_layout()
plt.show()

print("Evening Analysis Complete.")

print("Exercise 4 Complete.")