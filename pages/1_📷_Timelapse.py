import ee
import os
import warnings
import datetime
import fiona
import geopandas as gpd
import folium
import streamlit as st
import geemap.colormaps as cm
import geemap.foliumap as geemap
from datetime import date
from shapely.geometry import Polygon
import json
import leafmap

st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")


collection = st.selectbox(
            "Select a satellite image collection: ",
            [
                "Landsat TM-ETM-OLI Surface Reflectance",
                "Sentinel-2 MSI Surface Reflectance",
                "Geostationary Operational Environmental Satellites (GOES)",
                "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km",
                "MODIS Gap filled Land Surface Temperature Daily",
                "MODIS Ocean Color SMI",
                "USDA National Agriculture Imagery Program (NAIP)",
            ],
            index=1,
        )
json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]
# Preparing values
json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)
# Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


start_date = st.date_input("Select the start date:")
end_date = st.date_input("Select the end date:")

row1_col1, row1_col2 = st.columns([2, 1])

if st.session_state.get("zoom_level") is None:
    st.session_state["zoom_level"] = 4

st.session_state["ee_asset_id"] = None
st.session_state["bands"] = None
st.session_state["palette"] = None
st.session_state["vis_params"] = None

m = leafmap.Map(center=[40, -100], zoom=4, tiles="stamentoner")
m.add_heatmap(
            filepath,
            latitude="latitude",
            longitude="longitude",
            value="pop_max",
            name="Heat map",
            radius=20,
        )
m.to_streamlit(height=700)
