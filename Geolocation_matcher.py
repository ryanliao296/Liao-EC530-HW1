import math
import csv
import pandas as pd
import logging
from scipy.spatial import KDTree

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
                    lat = parse_coordinate(row[lat_col])
                    lon = parse_coordinate(row[lon_col])
                    
                    # Validate latitude and longitude ranges
                    if lat is None or lon is None:
                        print(f"Invalid coordinate in row {row_num}. Skipping.")
                        continue
                    if not (-90 <= lat <= 90):
                        print(f"Invalid latitude {lat} in row {row_num}. Skipping this row.")
                        continue
                    if not (-180 <= lon <= 180):
                        print(f"Invalid longitude {lon} in row {row_num}. Skipping this row.")
                        continue
                    
                    array.append((lat, lon))
                except ValueError:
                    print(f"Invalid data in row {row_num}: {row}. Skipping.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except KeyError:
        print(f"Specified columns '{lat_col}' or '{lon_col}' not found in the file.")
    except UnicodeDecodeError as e:
        print(f"Error decoding file {file_path}: {e}")
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
Parse DMS or decimal degrees input
"""
def parse_coordinate(input_str):
    try:
        # Split the input string by spaces
        parts = input_str.split()
        if len(parts) == 2:
            # Format: "40 42.8" (degrees and minutes only, without seconds or direction)
            degrees, minutes = map(float, parts)
            return degrees + (minutes / 60)
        elif len(parts) == 3:
            # Format: "40 42.8 0" or "40 42.8 N"
            degrees, minutes, last_part = parts
            if last_part.isdigit():  # If last part is a numeric second
                seconds = float(last_part)
                return float(degrees) + (float(minutes) / 60) + (seconds / 3600)
            else:  # If last part is a direction like 'N' or 'W'
                return dms_to_decimal(float(degrees), float(minutes), 0, last_part.upper())
        elif len(parts) == 4:
            # Format: "40 42.8 0 N"
            degrees, minutes, seconds, direction = parts
            return dms_to_decimal(float(degrees), float(minutes), float(seconds), direction.upper())
        else:
            # Assume decimal degrees format
            return float(input_str)
    except ValueError as e:
        print(f"Error parsing coordinate: {e}")
        return None

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
            lat_input = input("Enter latitude (or type 'd' to finish): ")
            if lat_input.lower() == 'd':
                break
            lat = parse_coordinate(lat_input)
            if lat is None:
                print("Invalid latitude format. Please try again.")
                continue
            
            lon_input = input("Enter longitude: ")
            lon = parse_coordinate(lon_input)
            if lon is None:
                print("Invalid longitude format. Please try again.")
                continue
            
            if not (-90 <= lat <= 90):
                print("Error: Latitude must be between -90 and 90. Please try again.")
                continue
            if not (-180 <= lon <= 180):
                print("Error: Longitude must be between -180 and 180. Please try again.")
                continue
            
            array.append((lat, lon))
        except ValueError:
            print("Invalid input. Please enter numeric values for latitude and longitude.")
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

