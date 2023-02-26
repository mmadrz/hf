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

st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")



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