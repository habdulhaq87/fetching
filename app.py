import ee
import streamlit as st
import folium
from streamlit_folium import st_folium

# Authenticate and initialize Earth Engine
def initialize_earth_engine():
    try:
        ee.Initialize()
    except ee.EEException:
        ee.Authenticate()
        ee.Initialize()

# Fetch S5P dataset for a specific region
def fetch_s5p_data():
    # Define the bounding box for Iraq's Kurdistan region
    region = ee.Geometry.Rectangle([42.35, 35.0, 46.5, 37.5])  # Longitude/Latitude bounds
    collection = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO')
                  .select('CO_column_number_density')
                  .filterDate('2024-11-01', '2024-12-05')
                  .filterBounds(region))
    return collection.mean(), region

# Visualize dataset on a folium map
def visualize_data(dataset, region):
    vis_params = {
        'min': 0,
        'max': 0.05,
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }

    # Center the map on the Kurdistan region
    map_center = [36.25, 44.425]  # Approximate center of Kurdistan
    zoom_level = 7

    # Convert dataset to URL for visualization
    map_id = ee.Image(dataset).getMapId(vis_params)
    tile_url = map_id['tile_fetcher'].url_format

    # Create Folium map
    m = folium.Map(location=map_center, zoom_start=zoom_level)
    folium.TileLayer(
        tiles=tile_url,
        attr='Google Earth Engine',
        overlay=True,
        name='S5P CO'
    ).add_to(m)
    
    # Add bounding box to the map
    folium.GeoJson(
        data=region.getInfo(),
        style_function=lambda x: {'color': 'blue', 'fill': False}
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

# Streamlit app
def main():
    st.title("S5P CO Column Density - Kurdistan Region")
    st.write("This app visualizes the CO column density over the Kurdistan region using Sentinel-5P data.")

    # Initialize Earth Engine
    initialize_earth_engine()

    # Fetch and visualize dataset
    dataset, region = fetch_s5p_data()
    folium_map = visualize_data(dataset, region)

    # Display map in Streamlit
    st_folium(folium_map, width=700, height=500)

if __name__ == "__main__":
    main()
