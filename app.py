import rasterio
import numpy as np
import folium
from rasterio.plot import reshape_as_image
import streamlit as st
from streamlit_folium import st_folium
from matplotlib.colors import LinearSegmentedColormap


# Load the GeoTIFF file
@st.cache_data
def load_tif(file_path):
    """
    Load GeoTIFF data from a local file.

    Args:
        file_path (str): Path to the GeoTIFF file.

    Returns:
        tuple: (data, bounds, profile) where `data` is the raster array,
               `bounds` are the geographic boundaries, and `profile` is the metadata.
    """
    with rasterio.open(file_path) as src:
        data = src.read(1)  # Read the first band
        bounds = src.bounds
        profile = src.profile
    return data, bounds, profile


# Normalize data
def normalize_data(data, min_val=None, max_val=None):
    """
    Normalize data to the range [0, 1].

    Args:
        data (numpy.ndarray): Input array.
        min_val (float, optional): Minimum value for normalization. Defaults to data.min().
        max_val (float, optional): Maximum value for normalization. Defaults to data.max().

    Returns:
        numpy.ndarray: Normalized array.
    """
    min_val = min_val if min_val is not None else np.nanmin(data)
    max_val = max_val if max_val is not None else np.nanmax(data)
    return (data - min_val) / (max_val - min_val)


# Visualize the raster data
def visualize_tif(data, bounds, palette, map_center, zoom_start=7):
    """
    Visualize raster data on a Folium map.

    Args:
        data (numpy.ndarray): Normalized raster data.
        bounds (tuple): Geographic bounds of the raster (left, bottom, right, top).
        palette (list): Color palette for visualization.
        map_center (list): [latitude, longitude] to center the map.
        zoom_start (int, optional): Initial zoom level. Defaults to 7.

    Returns:
        folium.Map: Interactive map object.
    """
    # Create a custom color map
    colormap = LinearSegmentedColormap.from_list("custom_palette", palette)
    colormap = np.array([colormap(i) for i in range(256)])[:, :3] * 255
    colormap = colormap.astype(np.uint8)

    # Convert data to image
    img = np.round(normalize_data(data) * 255).astype(np.uint8)
    img = reshape_as_image(img)

    # Create Folium map
    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # Add raster layer
    folium.raster_layers.ImageOverlay(
        image=img,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=0.7,
        name="Raster Data",
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)
    return m


# Streamlit app
def main():
    # App title
    st.title("GeoTIFF Viewer")
    st.write("Visualize a local GeoTIFF file directly on an interactive map.")

    # File path and parameters
    file_path = "data/geo.tif"
    palette = ["black", "blue", "purple", "cyan", "green", "yellow", "red"]  # Custom palette
    map_center = [36.25, 44.425]  # Approximate center of Kurdistan

    # Load and visualize the GeoTIFF
    data, bounds, profile = load_tif(file_path)
    folium_map = visualize_tif(data, bounds, palette, map_center)

    # Display the map in Streamlit
    st_folium(folium_map, width=800, height=600)


if __name__ == "__main__":
    main()
