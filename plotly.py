import streamlit as st
from func import *

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
from func import distance
import folium 
from folium.plugins import HeatMap
import plotly.express as px
from folium.plugins import HeatMapWithTime
import pytz
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import mplleaflet as mpl
from streamlit_folium import folium_static

df=pd.read_csv('Data/uber_limpios.csv')

def get_hot_spots(max_distance, min_pickups, ride_data):
    ## get coordinates from ride data
    coords = df[['pickup_latitude', 'pickup_longitude']]

    ## calculate epsilon parameter using
    ## the user defined distance
    kms_per_radian = 6371.0088
    epsilon = max_distance / kms_per_radian

    ## perform clustering
    db = DBSCAN(eps=epsilon, min_samples=min_pickups,
                algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

    ## group the clusters
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

    ## report
    print('Number of clusters: {}'.format(num_clusters))

    ## initialize lists for hot spots
    lat = []
    lon = []
    num_members = []

    ## loop through clusters and get centroids, number of members
    for i in range(len(set(cluster_labels))):
        if not clusters[i].empty:
            ## get centroid and magnitude of cluster
            lat.append(clusters[i]['pickup_latitude'].mean())
            lon.append(clusters[i]['pickup_longitude'].mean())
            num_members.append(len(clusters[i]))

    hot_spots = [lon, lat, num_members]
    return hot_spots, print(hot_spots)

def create_heat_map(month,day,hour,pickups):
    # get ride data
    
    ride_data = df.loc[((df['month']== month) & (df['day']== day) & (df['hour'] > hour))]
    
    
    # maximum distance between two cluster members in kilometers
    max_distance = 0.005

    # minimum number of cluster members
    min_pickups = pickups

    # call the get_hot_spots function
    
    hot_spots = get_hot_spots(max_distance, min_pickups, ride_data)
    
    df_hot = pd.DataFrame({'Lat': hot_spots[0][1], 'Lon': hot_spots[0][0], 'Numero': hot_spots[0][2]})

    m = folium.Map(location=[40.750584, -73.873010], zoom_start=10)

    # Crea un mapa de calor utilizando las coordenadas de hot_spots
    heat_map = HeatMap(df_hot)

    # Agrega el mapa de calor al mapa
    heat_map.add_to(m)

    # Muestra el mapa
    return m


def main():
    # Agregar contenido principal aquí
    st.title('Clustuber')
    st.write('App para saber a donde ir!')
    
    # Agregar campos para que el usuario ingrese los argumentos
    mes = st.number_input('Ingrese el mes:', value=1,min_value=1, max_value=12)
    dia = st.number_input('Ingrese el dia', value=1,min_value=1, max_value=31)
    hora = st.number_input('Ingrese la hora', value=1,min_value=1, max_value=24) 
    pickups = st.number_input('Nº min de recogidas', value=1,min_value=1)
    # Agregar un botón para llamar a la función
    if st.button('Ejecutar'):
        # Llamar a la función y mostrar el resultado
        resultado = create_heat_map(mes, dia, hora, pickups)
        folium_static(resultado)

if __name__ == '__main__':
    # Crear una barra lateral con el enlace "Acerca de"
    st.sidebar.title('Acerca de')
    st.sidebar.info('Versión Beta de la app, esta app esta pensada para conductores de Uber que no sepan donde ir')
    st.sidebar.info('Parametros de entrada: Mes: nº del mes, Dia: nº del dia del mes, Hora: nº hora (1-24), Nº min de recogidas: número de recogidas necesarias para formar un cluster')
    # Llamar a la función principal
    main()


    # correr en consola en la dirección del proyecto: streamlit run plotly.py