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

# Fetch S5P dataset
def fetch_s5p_data():
    collection = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_CO')
                  .select('CO_column_number_density')
                  .filterDate('2024-11-01', '2024-12-05'))
    return collection.mean()

# Visualize dataset on a folium map
def visualize_data(dataset):
    vis_params = {
        'min': 0,
        'max': 0.05,
        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
    }
    map_center = [-4.28, -25.01]
    zoom_level = 4

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
    folium.LayerControl().add_to(m)
    return m

# Streamlit app
def main():
    st.title("S5P CO Column Density Visualization")
    st.write("This app visualizes the CO column density using Sentinel-5P data.")

    # Initialize Earth Engine
    initialize_earth_engine()

    # Fetch and visualize dataset
    dataset = fetch_s5p_data()
    folium_map = visualize_data(dataset)

    # Display map in Streamlit
    st_folium(folium_map, width=700, height=500)

if __name__ == "__main__":
    main()
