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
