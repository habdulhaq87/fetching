import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes
import folium
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
from streamlit_folium import st_folium


# Load GeoTIFF file
@st.cache_data
def load_tif(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)  # Read the first band
        bounds = src.bounds
        profile = src.profile
    return data, bounds, profile


# Normalize data
def normalize_data(data, min_val=None, max_val=None):
    min_val = min_val if min_val is not None else np.nanmin(data)
    max_val = max_val if max_val is not None else np.nanmax(data)
    return (data - min_val) / (max_val - min_val)


# Create equal-area polygons
@st.cache_data
def raster_to_polygons(data, transform, bins):
    """
    Convert raster data to polygons grouped by bins.

    Args:
        data (numpy.ndarray): Input raster data.
        transform (Affine): Affine transform for raster data.
        bins (list): List of bin edges for grouping data.

    Returns:
        geopandas.GeoDataFrame: Polygons with raster value bins.
    """
    # Classify data into bins
    binned_data = np.digitize(data, bins, right=True)

    # Mask invalid values
    mask = ~np.isnan(data)

    # Generate polygons
    shapes_generator = shapes(binned_data, mask=mask, transform=transform)
    polygons = []
    for geom, value in shapes_generator:
        polygons.append({"geometry": shape(geom), "value": int(value)})

    return gpd.GeoDataFrame(polygons, crs="EPSG:4326")


# Visualize polygons
def visualize_polygons(gdf, map_center, zoom_start=7):
    """
    Visualize polygons on a Folium map.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame containing polygons.
        map_center (list): [latitude, longitude] to center the map.
        zoom_start (int, optional): Initial zoom level. Defaults to 7.

    Returns:
        folium.Map: Interactive map object.
    """
    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # Add polygons to map
    for _, row in gdf.iterrows():
        folium.GeoJson(
            data=row["geometry"].__geo_interface__,
            style_function=lambda x, value=row["value"]: {
                "fillColor": f"#{hex(255 - value * 25)[2:]:>02}0000",
                "color": "blue",
                "weight": 1,
                "fillOpacity": 0.5,
            },
        ).add_to(m)

    return m


# Main Streamlit app
def main():
    st.title("GeoTIFF to Equal-Area Polygons")
    st.write("Visualize raster data as equal-area polygons.")

    # File path and parameters
    file_path = "data/geo.tif"
    palette = ["black", "blue", "purple", "cyan", "green", "yellow", "red"]
    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]  # Value bins
    map_center = [36.25, 44.425]  # Approximate center of Kurdistan

    # Load data
    data, bounds, profile = load_tif(file_path)
    normalized_data = normalize_data(data)

    # Create polygons
    st.write("Generating polygons...")
    polygons_gdf = raster_to_polygons(normalized_data, profile["transform"], bins)

    # Visualize polygons
    st.write("Visualizing polygons...")
    folium_map = visualize_polygons(polygons_gdf, map_center)
    st_folium(folium_map, width=800, height=600)

    # Export to GeoJSON
    output_file = "data/polygons.geojson"
    polygons_gdf.to_file(output_file, driver="GeoJSON")
    st.write(f"Polygons saved to {output_file}")


if __name__ == "__main__":
    main()
