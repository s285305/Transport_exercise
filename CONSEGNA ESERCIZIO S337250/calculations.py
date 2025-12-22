

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt

# ----------------------------
# 0) Paths and parameters
# ----------------------------
try:
    zones_df = pd.read_csv("zone_statistiche_csv/zone_statistiche.csv", sep=';', encoding='latin1')
except:
    zones_df = pd.read_csv("zone_statistiche_csv/zone_statistiche.csv", sep=',', encoding='latin1')

zones_df['geometry'] = zones_df['WKT_GEOM'].apply(wkt.loads)
zones_gdf = gpd.GeoDataFrame(zones_df, geometry='geometry')
zones_gdf.set_crs(epsg=3003, inplace=True)
zones_gdf = zones_gdf.to_crs(epsg=4326)

BUFFER_M = 300

CRS_TRIPS = "EPSG:4326"
CRS_STOPS = "EPSG:4326"
CRS_ZONES = "EPSG:3003"
target_crs = "EPSG:32632"

zones = zones_gdf.copy()

# Dissolve all 94 zones to a single city polygon
torino_poly = zones.unary_union
torino_gdf = gpd.GeoDataFrame(geometry=[torino_poly], crs=CRS_ZONES)
zones = zones.to_crs(target_crs)
torino_poly_utm = zones.unary_union

csv_path = "Corse_Torino_TUTTI.csv"
stops_path = "gtt_gtfs/stops.geojson"

df = pd.read_csv(csv_path)

df = df.dropna(
    subset=[
        "LATITUDINE_INIZIO_CORSA",
        "LONGITUTIDE_INIZIO_CORSA",
        "LATITUDINE_FINE_CORSA",
        "LONGITUTIDE_FINE_CORSA",
    ]
)

df["trip_id"] = df.index.astype(int)

gdf_orig = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["LONGITUTIDE_INIZIO_CORSA"], df["LATITUDINE_INIZIO_CORSA"]
    ),
    crs="EPSG:4326",
)
gdf_dest = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["LONGITUTIDE_FINE_CORSA"], df["LATITUDINE_FINE_CORSA"]
    ),
    crs="EPSG:4326",
)

stops = gpd.read_file(stops_path)

# -----------------------------------------------------------
# 3. Reproject to metric CRS and clip to Torino 94 zones
# -----------------------------------------------------------
gdf_orig = gdf_orig.to_crs(target_crs)
gdf_dest = gdf_dest.to_crs(target_crs)
stops = stops.to_crs(target_crs)

# Identify which trips have endpoints within Torino
print(f"Before clipping: {len(gdf_orig)} origins, {len(gdf_dest)} destinations, {len(stops)} stops")

gdf_orig["orig_within"] = gdf_orig.within(torino_poly_utm)
gdf_dest["dest_within"] = gdf_dest.within(torino_poly_utm)

# Keep only trips where BOTH endpoints are in Torino
trips_both_in_torino = set(gdf_orig[gdf_orig["orig_within"]]["trip_id"]) & \
                       set(gdf_dest[gdf_dest["dest_within"]]["trip_id"])

gdf_orig = gdf_orig[gdf_orig["trip_id"].isin(trips_both_in_torino)].copy()
gdf_dest = gdf_dest[gdf_dest["trip_id"].isin(trips_both_in_torino)].copy()
stops = stops[stops.within(torino_poly_utm)]

print(f"After clipping to trips with both endpoints in Torino: {len(gdf_orig)} origins, {len(gdf_dest)} destinations, {len(stops)} stops")

# -----------------------------------------------------------
# 4. Create buffers around stops
# -----------------------------------------------------------
buffer_m = 300
stops["buffer"] = stops.geometry.buffer(buffer_m)


try:
    buffer_union = stops["buffer"].union_all()
except AttributeError:
    buffer_union = stops["buffer"].unary_union  

# GeoDataFrame of buffer polygons for mapping
buf_gdf = gpd.GeoDataFrame(geometry=stops["buffer"], crs=target_crs)

# -----------------------------------------------------------
# 5. Classify trips by transit-zone relationship
# -----------------------------------------------------------
gdf_orig["orig_in_zone"] = gdf_orig.within(buffer_union)
gdf_dest["dest_in_zone"] = gdf_dest.within(buffer_union)

trips = pd.DataFrame(
    {
        "trip_id": gdf_orig["trip_id"].values,
        "orig_in_zone": gdf_orig["orig_in_zone"].values,
        "dest_in_zone": gdf_dest["dest_in_zone"].values,
    }
)

def classify(row):
    if row["orig_in_zone"] and row["dest_in_zone"]:
        return "Both endpoints in transit zones"
    elif row["orig_in_zone"] and not row["dest_in_zone"]:
        return "Origin only in transit zone"
    elif not row["orig_in_zone"] and row["dest_in_zone"]:
        return "Destination only in transit zone"
    else:
        return "No endpoint in transit zone"

trips["class"] = trips.apply(classify, axis=1)

# Attach class back to GeoDataFrames for mapping
gdf_orig = gdf_orig.merge(trips[["trip_id", "class"]], on="trip_id")
gdf_dest = gdf_dest.merge(trips[["trip_id", "class"]], on="trip_id")

# -----------------------------------------------------------
# 6. Numeric summary and metrics
# -----------------------------------------------------------
total_trips = len(trips)
orig_in = int(trips["orig_in_zone"].sum())
dest_in = int(trips["dest_in_zone"].sum())
both_in = int(((trips["orig_in_zone"]) & (trips["dest_in_zone"])).sum())
one_endpoint = int((trips["orig_in_zone"] ^ trips["dest_in_zone"]).sum())

print("\n=== METRICS ===")
print(f"Total e-scooter trips analyzed: {total_trips:,}")
print(f"Trips with origins in transit zones: {orig_in:,} ({100*orig_in/total_trips:.1f}%)")
print(f"Trips with destinations in transit zones: {dest_in:,} ({100*dest_in/total_trips:.1f}%)")
print(f"Trips with both endpoints in transit zones: {both_in:,} ({100*both_in/total_trips:.1f}%)")
print(f"Complementary trips (one endpoint transit): {one_endpoint:,} ({100*one_endpoint/total_trips:.1f}%)")

summary = trips["class"].value_counts().to_frame("count")
summary["share"] = summary["count"] / len(trips)
print("\n=== BREAKDOWN BY CLASS ===")
print(summary)

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
import numpy as np


# -----------------------------------------------------------
# 7. IMPROVED Map: Single map with better readability
# -----------------------------------------------------------

# Sample trips for visualization (plot 10% for clarity)
sample_size = min(50000, len(gdf_orig))  # max 50k points
sample_idx = np.random.choice(gdf_orig.index, size=sample_size, replace=False)
gdf_orig_sample = gdf_orig.loc[sample_idx]

fig, ax = plt.subplots(1, 1, figsize=(14, 14))

# 1. Background: zone boundaries (subtle)
zones.boundary.plot(ax=ax, color="gray", linewidth=0.3, alpha=0.3)

# 2. Transit buffers (light, transparent)
buf_gdf.plot(ax=ax, color="lightblue", alpha=0.15, edgecolor="none")

# 3. PT stops (small, visible)
stops.plot(ax=ax, color="navy", markersize=4, alpha=0.8, zorder=3, label="PT stops")

# 4. Trip origins by class (larger, better colors)
color_map = {
    "Both endpoints in transit zones": "#2E7D32",      # dark green
    "Origin only in transit zone": "#1976D2",          # blue
    "Destination only in transit zone": "#F57C00",     # orange
    "No endpoint in transit zone": "#D32F2F"           # red
}

for trip_class, color in color_map.items():
    subset = gdf_orig_sample[gdf_orig_sample["class"] == trip_class]
    if len(subset) > 0:
        subset.plot(
            ax=ax,
            color=color,
            markersize=3,
            alpha=0.4,
            label=f"{trip_class} ({len(gdf_orig[gdf_orig['class']==trip_class]):,})",
            zorder=2
        )

ax.set_title("E-scooter trips and PT proximity analysis - Torino", fontsize=16, pad=20)
ax.legend(loc="upper left", frameon=True, fancybox=True, shadow=True, fontsize=10)
ax.set_axis_off()

plt.tight_layout()
plt.savefig("torino_escooter_pt_clean.png", dpi=300, bbox_inches="tight")
plt.show()

# -----------------------------------------------------------
# 8. ALTERNATIVE: Hexbin density map (even cleaner)
# -----------------------------------------------------------
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

zones.boundary.plot(ax=ax, color="black", linewidth=0.5, alpha=0.5)
stops.plot(ax=ax, color="red", markersize=3, alpha=0.6, zorder=3, label="PT stops")

# Hexbin for origins
x = gdf_orig.geometry.x
y = gdf_orig.geometry.y
hexbin = ax.hexbin(x, y, gridsize=50, cmap='YlOrRd', alpha=0.7, edgecolors='none', mincnt=1)

cb = plt.colorbar(hexbin, ax=ax, label="Trip count per hexagon")
ax.set_title("E-scooter trip origin density - Torino", fontsize=16, pad=20)
ax.legend(loc="upper left")
ax.set_axis_off()

plt.tight_layout()
plt.savefig("torino_escooter_density.png", dpi=300, bbox_inches="tight")
plt.show()

