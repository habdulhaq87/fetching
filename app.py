import rasterio
import numpy as np
import folium
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
from streamlit_folium import st_folium

# Load the GeoTIFF file
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

# Visualize raster data
def visualize_tif(data, bounds, palette, map_center, zoom_start=7):
    data_norm = normalize_data(data)
    colormap = LinearSegmentedColormap.from_list("custom_palette", palette)
    color_values = (colormap(data_norm)[:, :, :3] * 255).astype(np.uint8)

    m = folium.Map(location=map_center, zoom_start=zoom_start)
    folium.raster_layers.ImageOverlay(
        image=color_values,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=0.7,
        name="Raster Data",
    ).add_to(m)
    folium.LayerControl().add_to(m)
    return m

# Main Streamlit app
def main():
    st.title("GeoTIFF Viewer")
    st.write("Visualize a local GeoTIFF file directly on an interactive map.")

    file_path = "data/geo.tif"
    palette = ["black", "blue", "purple", "cyan", "green", "yellow", "red"]
    map_center = [36.25, 44.425]

    data, bounds, profile = load_tif(file_path)
    folium_map = visualize_tif(data, bounds, palette, map_center)

    st_folium(folium_map, width=800, height=600)

if __name__ == "__main__":
    main()
