import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import Point
import math

# ---------------------------------------------------------
# 1. SETUP: LOAD DATA
# ---------------------------------------------------------
print("1. Loading Data & Zones...")

# A. Load Trips
df = pd.read_csv("Corse_Torino_TUTTI.csv", low_memory=False)

# B. Load Zones (fixing encoding for Italian chars)
try:
    zones_df = pd.read_csv("zone_statistiche_csv/zone_statistiche.csv", sep=';', encoding='latin1')
except:
    zones_df = pd.read_csv("zone_statistiche_csv/zone_statistiche.csv", sep=',', encoding='latin1')

zones_df['geometry'] = zones_df['WKT_GEOM'].apply(wkt.loads)
zones_gdf = gpd.GeoDataFrame(zones_df, geometry='geometry')
zones_gdf.set_crs(epsg=3003, inplace=True)
zones_gdf = zones_gdf.to_crs(epsg=4326) # Convert to GPS

# ---------------------------------------------------------
# 2. SPATIAL JOIN (Assign Trips to Zones)
# ---------------------------------------------------------
print("2. Mapping Trips to Zones by Operator...")

# Create Geometry for Start Points
geometry_start = [Point(xy) for xy in zip(df.LONGITUTIDE_INIZIO_CORSA, df.LATITUDINE_INIZIO_CORSA)]
gdf_start = gpd.GeoDataFrame(df, geometry=geometry_start, crs="EPSG:4326")

# Join with Zones
# We use 'inner' join to discard trips starting outside the map
gdf_joined = gpd.sjoin(gdf_start, zones_gdf[['DENOM', 'geometry']], how="inner", predicate="within")

# ---------------------------------------------------------
# 3. AGGREGATE BY OPERATOR
# ---------------------------------------------------------
# Get list of unique operators (e.g., ['LIME', 'BIRD', 'VOID'])
operators = gdf_joined['OPERATORE'].unique()
n_operators = len(operators)

print(f"   Found operators: {operators}")

# ---------------------------------------------------------
# 4. GENERATE SIDE-BY-SIDE MAPS
# ---------------------------------------------------------
print("3. Generating Comparison Maps...")

# Create a figure with subplots (1 row, N columns)
fig, axes = plt.subplots(1, n_operators, figsize=(6 * n_operators, 8))
# Ensure axes is a list even if there's only 1 operator
if n_operators == 1: axes = [axes]

# Define a consistent color scale limit across all maps
max_trips_any_zone = 0
for op in operators:
    op_data = gdf_joined[gdf_joined['OPERATORE'] == op]
    counts = op_data['DENOM'].value_counts()
    if not counts.empty:
        max_trips_any_zone = max(max_trips_any_zone, counts.max())

# Loop through each operator and draw their map
for i, op in enumerate(operators):
    ax = axes[i]
    
    # Filter data for this operator
    op_data = gdf_joined[gdf_joined['OPERATORE'] == op]
    
    # Count trips per zone
    trip_counts = op_data['DENOM'].value_counts().reset_index()
    trip_counts.columns = ['DENOM', 'TRIPS']
    
    # Ensure types match for merge
    zones_gdf['DENOM'] = zones_gdf['DENOM'].astype(str)
    trip_counts['DENOM'] = trip_counts['DENOM'].astype(str)
    
    # Merge with map geometry
    op_map = zones_gdf.merge(trip_counts, on='DENOM', how='left').fillna(0)
    
    # Plot
    op_map.plot(column='TRIPS', 
                ax=ax, 
                cmap='viridis', 
                vmax=max_trips_any_zone, # Unified scale
                legend=True,
                legend_kwds={'label': "Trip Origins", 'shrink': 0.5},
                edgecolor='white', linewidth=0.2)
    
    ax.set_title(f"Operator: {op}", fontsize=14, fontweight='bold')
    ax.axis('off')

plt.suptitle(f"Mobility Demand by Operator (Total Trip Origins)", fontsize=16, y=0.95)
plt.tight_layout()
plt.show()