import math
import csv
import pandas as pd
import logging
from scipy.spatial import KDTree
import re

# Set up logging for skipped rows
logging.basicConfig(
    filename='skipped_rows.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)
radius_earth = 6371

"""
    Calculate the great-circle distance between two points on the Earth's surface using the Haversine formula.
    Inputs:
        lat1, lon1: Latitude and Longitude of the first point in degrees.
        lat2, lon2: Latitude and Longitude of the second point in degrees.
    Outputs:
        The distance between the two points in kilometers.
"""
def haversine(lat1, lon1, lat2, lon2):
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    delta_lat = lat1 - lat2
    delta_lon = lon1 - lon2

    a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth * c

"""
    Find the closest point in the second array for each point in the first array using a KDTree.
    Inputs:
        array1: List of tuples containing (latitude, longitude) of points.
        array2: List of tuples containing (latitude, longitude) of points.
    Outputs:
        A list of tuples where each entry contains the closest points from array 2 and the distance
"""
def match_closest_points(array1, array2):
    if not array1 or not array2:
        print("One or both input arrays are empty. Exiting.")
        return []

    # Build the KDTree for array2
    tree = KDTree([(math.radians(lat), math.radians(lon)) for lat, lon in array2])

    # Find closest points for each point in array1
    results = []
    for lat1, lon1 in array1:
        # Query the KDTree for the closest neighbor
        dist, idx = tree.query((math.radians(lat1), math.radians(lon1)))

        # Convert the great-circle distance back to kilometers
        lat2, lon2 = array2[idx]
        distance_km = haversine(lat1, lon1, lat2, lon2)

        results.append(((lat1, lon1), (lat2, lon2), distance_km))
    return results

"""
Load coordinates from csv file
"""
def load_coordinates_from_csv(file_path, lat_col, lon_col):
    array = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Parse latitude and longitude using the universal parser
                    lat = parse_coordinate(row[lat_col])
                    lon = parse_coordinate(row[lon_col])
                   
                    # Validate latitude and longitude ranges
                    if not (-90 <= lat <= 90):
                        raise ValueError(f"Latitude out of range: {lat}")
                    if not (-180 <= lon <= 180):
                        raise ValueError(f"Longitude out of range: {lon}")
                   
                    array.append((lat, lon))
                except ValueError as e:
                    print(f"Invalid coordinate in row {row_num}. Skipping. Error: {e}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except KeyError:
        print(f"Specified columns '{lat_col}' or '{lon_col}' not found in the file.")
    return array

"""
Convert DMS to decimal degrees
"""
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

"""
Parse a coordinate string in multiple formats:
    - Decimal degrees: '40.7128', '-74.0060'
    - Degrees, minutes, seconds: '40°42'51"N', '74°0'22"W'
    - Decimal degrees with direction: '40.7128° N', '74.0060° W'
"""
def parse_coordinate(coord_str):
    try:
        # Remove spaces for easier parsing
        coord_str = coord_str.strip()
       
        # Check for degrees, minutes, seconds (DMS) format
        dms_match = re.match(r"(\d+)°\s*(\d+)'?\s*(\d+(?:\.\d+)?)?\"?\s*([NSEW])?", coord_str, re.IGNORECASE)
        if dms_match:
            degrees = int(dms_match.group(1))
            minutes = int(dms_match.group(2))
            seconds = float(dms_match.group(3)) if dms_match.group(3) else 0
            direction = dms_match.group(4).upper() if dms_match.group(4) else None
           
            # Convert to decimal degrees
            decimal = degrees + (minutes / 60) + (seconds / 3600)
            if direction in ['S', 'W']:
                decimal = -decimal
            return decimal

        # Check for decimal degrees with direction
        dd_match = re.match(r"([+-]?\d+(?:\.\d+)?)°?\s*([NSEW])?", coord_str, re.IGNORECASE)
        if dd_match:
            decimal = float(dd_match.group(1))
            direction = dd_match.group(2).upper() if dd_match.group(2) else None
            if direction in ['S', 'W']:
                decimal = -decimal
            return decimal

        # Fallback to basic decimal degrees
        return float(coord_str)
    except ValueError as e:
        raise ValueError(f"Error parsing coordinate '{coord_str}': {e}")

"""
    Prompt the user to input an array of GPS points (latitude and longitude).
    Input:
        None
    Output:
        A list of tuples containing the entered (latitude, longitude) values.
"""
def user_input_array():
    array = []
    while True:
        try:
            lat_input = input("Enter latitude (e.g., '40.7128', '40°42'51\"N', or '40.7128° N'; type 'd' to finish): ")
            if lat_input.lower() == 'd':
                break
            lon_input = input("Enter longitude (e.g., '-74.0060', '74°0'22\"W', or '74.0060° W'): ")
           
            lat = parse_coordinate(lat_input)
            lon = parse_coordinate(lon_input)
           
            if not (-90 <= lat <= 90):
                print("Error: Latitude must be between -90 and 90. Please try again.")
                continue
            if not (-180 <= lon <= 180):
                print("Error: Longitude must be between -180 and 180. Please try again.")
                continue
           
            array.append((lat, lon))
        except ValueError as e:
            print(f"Invalid input: {e}")
    return array

"""
    Get GPS points for an array based on user choice (manual or CSV).
"""
def get_coordinates(array_name):
    print(f"How would you like to input coordinates for {array_name}?")
    choice = input("Type 'manual' for manual input or 'csv' for CSV file: ").strip().lower()
    
    if choice == 'csv':
        file_path = input(f"Enter the path to the CSV file for {array_name}: ")
        lat_col = input(f"Enter the column name for latitude in {array_name}: ")
        lon_col = input(f"Enter the column name for longitude in {array_name}: ")
        return load_coordinates_from_csv(file_path, lat_col, lon_col)
    elif choice == 'manual':
        print(f"Input coordinates for {array_name}:")
        return user_input_array()
    else:
        print("Invalid choice. Please type 'manual' or 'csv'.")
        return get_coordinates(array_name)


array1 = get_coordinates("Array 1")
array2 = get_coordinates("Array 2")

# Run calculations and output results
if array1 and array2:
    results = match_closest_points(array1, array2)
    for point1, closest_point, distance in results:
        print(f"Point {point1} is closest to {closest_point} with a distance of {distance:.2f} km")
else:
    print("One or both arrays are empty. Please check your input.")

