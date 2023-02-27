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
from geemap import geojson_to_ee, ee_to_geojson



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




def save_uploaded_file(file_content, file_name):
    """
    Save the uploaded file to a temporary directory
    """
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(file_name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(file_content.getbuffer())

    return file_path

st.title("Upload Vector Data")


width = 950
height = 600
url = st.text_input(
            "Enter a URL to a vector dataset",
            "https://github.com/giswqs/streamlit-geospatial/raw/master/data/us_states.geojson",
        )

data = st.file_uploader(
            "Upload a vector dataset", type=["geojson", "kml", "zip", "tab"]
        )
container = st.container()

if data or url:
    if data:
        file_path = save_uploaded_file(data, data.name)
        layer_name = os.path.splitext(data.name)[0]
    elif url:
        file_path = url
        layer_name = url.split("/")[-1].split(".")[0]

if file_path.lower().endswith(".kml"):
    fiona.drvsupport.supported_drivers["KML"] = "rw"
    gdf = gpd.read_file(file_path, driver="KML")
else:
    gdf = gpd.read_file(file_path)

lon, lat = leafmap.gdf_centroid(gdf)
m = leafmap.Map(center=(lat, lon), draw_export=True)
m.add_gdf(gdf, layer_name=layer_name)


# m.add_vector(file_path, layer_name=layer_name)
m.to_streamlit(width=width, height=height)






m= geemap.Map.addLayer(ee_data, {}, "US States EE")

collection = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(roi) \
    .filterDate(start_date, end_date) \
    .filterMetadata ('CLOUDY_PIXEL_PERCENTAGE', 'Less_Than', 15) \
    .filterMetadata ('NODATA_PIXEL_PERCENTAGE', 'Less_Than', 70) \
    .map(Cloudmask)\
        .mean()