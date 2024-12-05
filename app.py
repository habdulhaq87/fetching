import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes
import folium
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
from streamlit_folium import st_folium
import tempfile
import os


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
    binned_data = np.digitize(data, bins, right=True).astype(np.uint8)
    mask = ~np.isnan(data)
    shapes_generator = shapes(binned_data, mask=mask, transform=transform)
    polygons = []
    for geom, value in shapes_generator:
        polygons.append({"geometry": shape(geom), "value": int(value)})
    return gpd.GeoDataFrame(polygons, crs="EPSG:4326")


# Visualize polygons
def visualize_polygons(gdf, map_center, zoom_start=7):
    m = folium.Map(location=map_center, zoom_start=zoom_start)
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
    st.title("Interactive GeoTIFF to Equal-Area Polygons")
    st.write("Visualize raster data as equal-area polygons with adjustable parameters.")

    # File upload
    uploaded_file = st.file_uploader("Upload a GeoTIFF file", type=["tif"])
    if not uploaded_file:
        st.warning("Please upload a GeoTIFF file to proceed.")
        return

    # Temporary file handling
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    temp_file.write(uploaded_file.read())
    temp_file.close()

    # Parameters for processing
    bins_input = st.text_input(
        "Enter value bins (comma-separated)", "0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0"
    )
    bins = list(map(float, bins_input.split(",")))
    map_center_lat = st.number_input("Map Center Latitude", value=36.25)
    map_center_lon = st.number_input("Map Center Longitude", value=44.425)
    zoom_start = st.slider("Map Zoom Level", min_value=1, max_value=18, value=7)

    # Load and process data
    data, bounds, profile = load_tif(temp_file.name)
    normalized_data = normalize_data(data)

    # Create polygons
    st.write("Generating polygons...")
    polygons_gdf = raster_to_polygons(normalized_data, profile["transform"], bins)

    # Visualize polygons
    st.write("Visualizing polygons...")
    folium_map = visualize_polygons(polygons_gdf, [map_center_lat, map_center_lon], zoom_start)
    st_folium(folium_map, width=800, height=600)

    # Export and download GeoJSON
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".geojson")
    polygons_gdf.to_file(output_file.name, driver="GeoJSON")
    with open(output_file.name, "rb") as f:
        st.download_button("Download GeoJSON", f, file_name="polygons.geojson", mime="application/json")

    # Cleanup temporary files
    os.unlink(temp_file.name)
    os.unlink(output_file.name)


if __name__ == "__main__":
    main()
