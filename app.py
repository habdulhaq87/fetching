import ee
import streamlit as st
import folium
from streamlit_folium import st_folium

# Initialize Earth Engine
def initialize_earth_engine():
    """Initialize Earth Engine with authentication if required."""
    try:
        ee.Initialize()
    except ee.EEException:
        ee.Authenticate()
        ee.Initialize()

# Fetch data
@st.cache_data
def fetch_s5p_data(start_date, end_date, region_bounds):
    """
    Fetch the S5P dataset for the specified date range and region.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        region_bounds (list): [west, south, east, north] bounds of the region.

    Returns:
        tuple: Mean image of the dataset and the region geometry.
    """
    region = ee.Geometry.Rectangle(region_bounds)
    collection = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO')
                  .select('CO_column_number_density')
                  .filterDate(start_date, end_date)
                  .filterBounds(region))
    return collection.mean(), region

# Create map visualization
def visualize_data(dataset, region, center_coords, zoom_level=7):
    """
    Create a Folium map to visualize the dataset.

    Args:
        dataset (ee.Image): Processed Earth Engine image.
        region (ee.Geometry): Region geometry for bounding box.
        center_coords (list): [latitude, longitude] for map center.
        zoom_level (int): Initial zoom level of the map.

    Returns:
        folium.Map: Interactive map object.
    """
    vis_params = {
        'min': 0,
        'max': 0.05,
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }

    # Convert dataset to URL for visualization
    map_id = ee.Image(dataset).getMapId(vis_params)
    tile_url = map_id['tile_fetcher'].url_format

    # Create and configure the Folium map
    m = folium.Map(location=center_coords, zoom_start=zoom_level)
    folium.TileLayer(
        tiles=tile_url,
        attr='Google Earth Engine',
        overlay=True,
        name='S5P CO'
    ).add_to(m)

    # Add region bounding box
    folium.GeoJson(
        data=region.getInfo(),
        style_function=lambda x: {'color': 'blue', 'fill': False}
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

# Main Streamlit app
def main():
    # App title and description
    st.title("S5P CO Column Density - Kurdistan Region")
    st.write("Visualizing CO column density over Kurdistan using Sentinel-5P data.")

    # Initialize Earth Engine
    initialize_earth_engine()

    # Define parameters
    start_date = '2024-11-01'
    end_date = '2024-12-05'
    region_bounds = [42.35, 35.0, 46.5, 37.5]  # [west, south, east, north]
    center_coords = [36.25, 44.425]  # Map center (latitude, longitude)

    # Fetch dataset
    dataset, region = fetch_s5p_data(start_date, end_date, region_bounds)

    # Create and display the map
    folium_map = visualize_data(dataset, region, center_coords)
    st_folium(folium_map, width=700, height=500)

# Run the app
if __name__ == "__main__":
    main()
