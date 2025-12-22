import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely import LineString, wkt
from shapely.geometry import Point

# ---------------------------------------------------------
# 1. LOAD AND PREPARE THE MAP (ZONES)
# ---------------------------------------------------------
print("Loading Zoning Data...")


ZONES_FILE= "zone_statistiche_csv/zone_statistiche.csv" 
try:
    zones_df = pd.read_csv(ZONES_FILE, sep=';', encoding='latin1')
except:
    zones_df = pd.read_csv(ZONES_FILE, sep=';', encoding='cp1252')

if 'WKT_GEOM' not in zones_df.columns:
    zones_df = pd.read_csv("zone_statistiche_csv/zone_statistiche.csv", sep=',')

# CONVERT TEXT TO GEOMETRY

zones_df['geometry'] = zones_df['WKT_GEOM'].apply(wkt.loads)

# Create GeoDataFrame
zones_gdf = gpd.GeoDataFrame(zones_df, geometry='geometry')

# SET COORDINATE REFERENCE SYSTEM (CRS)
zones_gdf.set_crs(epsg=3003, inplace=True)

# CONVERT TO GPS COORDINATES (EPSG:4326) to match the scooters
zones_gdf = zones_gdf.to_crs(epsg=4326)

print(f"Loaded {len(zones_gdf)} zones.")

# ---------------------------------------------------------
# 2. LOAD SCOOTER DATA & SPATIAL JOIN
# ---------------------------------------------------------
print("Loading Scooter Data...")
df = pd.read_csv("Corse_Torino_TUTTI.csv")
df['DATAORA_INIZIO'] = pd.to_datetime(df['DATAORA_INIZIO'])

# Convert Start/End to Geometry Points
geometry_start = [Point(xy) for xy in zip(df.LONGITUTIDE_INIZIO_CORSA, df.LATITUDINE_INIZIO_CORSA)]
geometry_end = [Point(xy) for xy in zip(df.LONGITUTIDE_FINE_CORSA, df.LATITUDINE_FINE_CORSA)]

gdf_start = gpd.GeoDataFrame(df, geometry=geometry_start, crs="EPSG:4326")
gdf_end = gpd.GeoDataFrame(df, geometry=geometry_end, crs="EPSG:4326")

print("Performing Spatial Join (Mapping GPS to Zones)...")

# 1. Perform Spatial Joins
target_column = 'DENOM' 


gdf_start = gpd.sjoin(gdf_start, zones_gdf[[target_column, 'geometry']], how="inner", predicate="within")
gdf_end = gpd.sjoin(gdf_end, zones_gdf[[target_column, 'geometry']], how="inner", predicate="within")

# 2. Rename columns to avoid confusion
gdf_start = gdf_start.rename(columns={target_column: 'ORIGIN_ZONE'})
gdf_end = gdf_end.rename(columns={target_column: 'DEST_ZONE'})

# 3. CRITICAL FIX: Find common indices (Trips with BOTH valid Start AND End)
valid_trips_index = gdf_start.index.intersection(gdf_end.index)

print(f"Trips starting in zone: {len(gdf_start)}")
print(f"Trips ending in zone: {len(gdf_end)}")
print(f"Valid Trips (Both inside): {len(valid_trips_index)}")

# 4. Create the final dataframe using only the valid intersection
df_zoned = df.loc[valid_trips_index].copy()
df_zoned['ORIGIN_ZONE'] = gdf_start.loc[valid_trips_index, 'ORIGIN_ZONE']
df_zoned['DEST_ZONE'] = gdf_end.loc[valid_trips_index, 'DEST_ZONE']

# ---------------------------------------------------------
# 3. O-D MATRICES (Total, Peak, Off-Peak)
# ---------------------------------------------------------
print("Calculating Matrices...")

# 3a. Total Matrix
od_matrix_total = pd.crosstab(df_zoned['ORIGIN_ZONE'], df_zoned['DEST_ZONE'])

# 3b. Temporal Split
df_zoned['Hour'] = df_zoned['DATAORA_INIZIO'].dt.hour
peak_hours = [7, 8, 9, 16, 17, 18, 19]

df_peak = df_zoned[df_zoned['Hour'].isin(peak_hours)]
df_offpeak = df_zoned[~df_zoned['Hour'].isin(peak_hours)]

od_matrix_peak = pd.crosstab(df_peak['ORIGIN_ZONE'], df_peak['DEST_ZONE'])
od_matrix_offpeak = pd.crosstab(df_offpeak['ORIGIN_ZONE'], df_offpeak['DEST_ZONE'])

#create a map with origin destination lines, bidding the lines based on number of trips, consider only top 100 origin-destination pairs
top_od_pairs = df_zoned.groupby(['ORIGIN_ZONE', 'DEST_ZONE']).size().nlargest(100)
print("Creating Map Visualization for Top 100 O-D Pairs...")
lines = []
for (origin, dest), count in top_od_pairs.items():
    origin_geom = zones_gdf[zones_gdf['DENOM'] == origin].geometry.centroid.values[0]
    dest_geom = zones_gdf[zones_gdf['DENOM'] == dest].geometry.centroid.values[0]
    line = LineString([origin_geom, dest_geom])
    lines.append({'geometry': line, 'count': count})
od_lines_gdf = gpd.GeoDataFrame(lines, geometry='geometry', crs="EPSG:4326")
# Plotting the lines
# Rebuild line width with a stronger scaling
max_lw = 8
min_lw = 0.5
norm_counts = (od_lines_gdf["count"] - od_lines_gdf["count"].min()) / (
    od_lines_gdf["count"].max() - od_lines_gdf["count"].min()
)
line_widths = min_lw + norm_counts * (max_lw - min_lw)

fig, ax = plt.subplots(figsize=(14, 12))

# 1) Tone down background polygons
zones_gdf.plot(
    ax=ax,
    color="black",
    edgecolor="white",
    linewidth=1,
    alpha=0.6,
)

# 2) Plot lines on top with zorder and transparency
od_lines_gdf.plot(
    ax=ax,
    column="count",
    linewidth=line_widths,
    cmap="Reds",
    legend=True,
    alpha=0.8,
    zorder=3,
)

# 3) Optionally add centroids as points
zones_gdf.centroid.plot(
    ax=ax,
    color="black",
    markersize=5,
    alpha=0.7,
    zorder=4,
)

ax.set_title("Top 100 Origin–Destination Pairs", fontsize=16)
ax.set_axis_off()
plt.tight_layout()
plt.show()


# ---------------------------------------------------------
# 4. VISUALIZATION 
# ---------------------------------------------------------
print("Generating Plots...")

# 1. Define Top Zones based on TOTAL volume
top_zones = df_zoned['ORIGIN_ZONE'].value_counts().head(30).index.tolist()

#2. Create the Heatmap Data safely
s_m= od_matrix_total.reindex(index=top_zones, columns=top_zones, fill_value=0)
plt.figure(figsize=(12, 10))
sns.heatmap(s_m, cmap="OrRd", linewidths=.5)
plt.title("O-D Matrix: TOTAL Trips (Top 30 Zones)")
plt.xlabel("Destination Zone")
plt.ylabel("Origin Zone")
plt.tight_layout()
plt.show()

subset_matrix = od_matrix_peak.reindex(index=top_zones, columns=top_zones, fill_value=0)
subset_matrix_offpeak = od_matrix_offpeak.reindex(index=top_zones, columns=top_zones, fill_value=0)
plt.figure(figsize=(12, 10))
sns.heatmap(subset_matrix, cmap="OrRd", linewidths=.5)
plt.title("O-D Matrix: PEAK HOURS (Top 30 Zones)")
plt.xlabel("Destination Zone")
plt.ylabel("Origin Zone")
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 10))
sns.heatmap(subset_matrix_offpeak, cmap="OrRd", linewidths=.5)
plt.title("O-D Matrix: OFF PEAK HOURS (Top 30 Zones)")
plt.xlabel("Destination Zone")
plt.ylabel("Origin Zone")
plt.tight_layout()
plt.show()


# # 3. Map Visualization (Trip Generation)
trip_counts = df_zoned['ORIGIN_ZONE'].value_counts().reset_index()
trip_counts.columns = [target_column, 'TRIPS']

# Merge counts back into the map
zones_gdf[target_column] = zones_gdf[target_column].astype(str)
trip_counts[target_column] = trip_counts[target_column].astype(str)

zones_map_plot = zones_gdf.merge(trip_counts, on=target_column, how='left').fillna(0)

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
zones_map_plot.plot(column='TRIPS', ax=ax, legend=True, 
                    legend_kwds={'label': "Number of Trips Starting Here"},
                    cmap='viridis')
zones_map_plot.boundary.plot(ax=ax, linewidth=1, color='white', alpha=0.5)
plt.title("Intensity of Trip Origins by Zone")
plt.axis('off')
plt.show()

# # 3. Map Visualization (Trip Destination)
trip_counts_dest = df_zoned['DEST_ZONE'].value_counts().reset_index()
trip_counts_dest.columns = [target_column, 'TRIPS']
# Merge counts back into the map
trip_counts_dest[target_column] = trip_counts_dest[target_column].astype(str)
zones_map_plot_dest = zones_gdf.merge(trip_counts_dest, on=target_column, how='left').fillna(0)
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
zones_map_plot_dest.plot(column='TRIPS', ax=ax, legend=True,
                    legend_kwds={'label': "Number of Trips Ending Here"},
                    cmap='plasma')
zones_map_plot_dest.boundary.plot(ax=ax, linewidth=1, color='white', alpha=0.5)
plt.title("Intensity of Trip Destinations by Zone")
plt.axis('off')
plt.show()


print("Analysis Complete.")