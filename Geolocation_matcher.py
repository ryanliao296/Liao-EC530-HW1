import math

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
    Find the closest point in the second array for each point in the first array.
    Inputs:
        array1: List of tuples containing (latitude, longitude) of points.
        array2: List of tuples containing (latitude, longitude) of points.
    Outputs:
        A list of tuples where each entry contains the closest points from array 2 and the distance
"""
def match_closest_points(array1, array2):

    closest = []

    # Calculate and update min_distance to find the closest point in Array 2
    for lat1, lon1 in array1:
        closest_point = None
        min_distance = float('inf')
        for lat2, lon2 in array2:
            distance = haversine(lat1, lon1, lat2, lon2)
            if distance < min_distance:
                min_distance = distance
                closest_point = (lat2, lon2)
        closest.append(((lat1, lon1), closest_point, min_distance))

    return closest

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
            # Receive user input
            lat_input = input("Enter latitude (or type 'd' to finish): ")
            if lat_input.lower() == 'd':
                break
            lat = float(lat_input)
            lon = float(input("Enter longitude: "))
            
            # Check latitude and longitude ranges
            if not (-90 <= lat <= 90):
                print("Error: Latitude must be between -90 and 90. Please try again.")
                continue
            if not (-180 <= lon <= 180):
                print("Error: Longitude must be between -180 and 180. Please try again.")
                continue
            
            array.append((lat, lon))

        # Check for numerical coordinates
        except ValueError:
            print("Invalid input. Please enter numeric values for latitude and longitude.")

    return array


# Ask for first and second array from user
print("Input coordinates for the first array:")
array1 = user_input_array()

print("Input coordinates for the second array:")
array2 = user_input_array()

# Run calculations and output for each point in array 1's closest point in array 2
results = match_closest_points(array1, array2)
for point1, closest_point, distance in results:
    print(f"Point {point1} is closest to {closest_point} with a distance of {distance:.2f} km")

