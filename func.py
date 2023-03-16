import numpy as np
from math import radians, sin, cos, sqrt, asin

def distance(longitude1, latitude1, longitude2, latitude2):
    R = 6371  # Radio de la Tierra en kilómetros
    lat1, lon1, lat2, lon2 = map(np.radians, [latitude1, longitude1, latitude2, longitude2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c
    return distance


import pandas as pd
from func import distance

def clean_data(input_file_path, output_file_path):
    # Read the input CSV file
    df = pd.read_csv(input_file_path)

    # Drop unnecessary columns
    df = df.drop(['key', 'Unnamed: 0'], axis=1)

    # Remove rows with missing values
    df.dropna(axis=0, inplace=True)

    # Convert pickup_datetime to datetime object and adjust time zone to Eastern Standard Time (EST)
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], format='%Y-%m-%d %H:%M:%S %Z')
    df['pickup_datetime'] = df['pickup_datetime'].dt.tz_convert('America/New_York').dt.tz_localize(None)

    # Extract month, weekday, day, hour, and minute from pickup_datetime
    df['month'] = df['pickup_datetime'].dt.month
    df['weekday'] = df['pickup_datetime'].dt.day_name()
    df['day'] = df['pickup_datetime'].dt.day
    df['hour'] = df['pickup_datetime'].dt.hour
    df['minute'] = df['pickup_datetime'].dt.minute
    
    #Order the dataframe
    df.sort_values(by='pickup_datetime', ascending=True, inplace=True, ignore_index=True)

    # Compute distance using haversine formula
    df['distance'] =  distance(df['pickup_longitude'].to_numpy(),df['pickup_latitude'].to_numpy(),
                            df['dropoff_longitude'].to_numpy(), df['dropoff_latitude'].to_numpy())

    # Remove rows with invalid values
    df.drop(df[df['passenger_count'] > 6].index, axis=0, inplace=True)
    df.drop(df[df['fare_amount'] < 2.5].index, axis=0, inplace=True)
    df.drop(df[df['distance'] > 400].index, axis=0, inplace=True)
    df.drop(df[df['distance'] == 0].index, axis=0, inplace=True)
    df.dropna(axis=0, inplace=True)

    # Save the cleaned data to a new CSV file
    df.to_csv(output_file_path, index=False)
    
    return df


import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from sklearn.cluster import DBSCAN


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
    display(ride_data)
    
    # maximum distance between two cluster members in kilometers
    max_distance = 0.005

    # minimum number of cluster members
    min_pickups = pickups

    # call the get_hot_spots function
    
    hot_spots = get_hot_spots(max_distance, min_pickups, ride_data)
    print(hot_spots)
    df_hot = pd.DataFrame({'Lat': hot_spots[0][1], 'Lon': hot_spots[0][0], 'Numero': hot_spots[0][2]})

    m = folium.Map(location=[40.750584, -73.873010], zoom_start=10)

    # Crea un mapa de calor utilizando las coordenadas de hot_spots
    heat_map = HeatMap(df_hot)

    # Agrega el mapa de calor al mapa
    heat_map.add_to(m)

    # Muestra el mapa
    return m