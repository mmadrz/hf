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


m = geemap.Map(
    basemap="HYBRID",
    plugin_Draw=True,
    Draw_export=True,
    locate_control=True,
    plugin_LatLngPopup=False,
)
m.add_basemap("ROADMAP")
m.to_streamlit(height=700)

# Create a cloud mask function
def Cloudmask(image):
# Exclude the pixels that represent clouds and cirrus on the image (with the QA60 Band)
    qa = image.select('QA60')
    cloud_type = 1 << 10
    cirrus_type = 1 << 11
    mask = qa.bitwiseAnd(cloud_type).eq(0) \
    .And(qa.bitwiseAnd(cirrus_type).eq(0))
    return image.updateMask(mask)



roi_pass = st.file_uploader("Choose the json file of your ROI")
if roi_pass is not None:
    roi = json.loads(roi_pass)

feature = ee.Feature(roi, {})
roi = feature.geometry()


collection = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(roi) \
    .filterDate(start_date, end_date) \
    .filterMetadata ('CLOUDY_PIXEL_PERCENTAGE', 'Less_Than', 15) \
    .filterMetadata ('NODATA_PIXEL_PERCENTAGE', 'Less_Than', 70) \
    .map(Cloudmask)\
    .mean()

