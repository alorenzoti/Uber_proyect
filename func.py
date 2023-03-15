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