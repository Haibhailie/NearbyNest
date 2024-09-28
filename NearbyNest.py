import requests
import pandas as pd
import json
from geopy.distance import geodesic

# Load configuration data from the JSON file
def load_config_data():
    with open('config.json') as f:
        config_data = json.load(f)
    return config_data

# Load addresses from CSV
def load_addresses():
    df = pd.read_csv('addresses.csv')
    return df

# Function to get the current province using Google Geocoding API
def get_current_province(api_key, ipinfo_key):
    ip_location_url = f'https://ipinfo.io?token=' + ipinfo_key
    ip_location = requests.get(ip_location_url).json()
    if 'loc' in ip_location:
        lat, lng = ip_location['loc'].split(',')
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
        response = requests.get(geocode_url).json()
        if response['status'] == 'OK':
            for component in response['results'][0]['address_components']:
                if 'administrative_area_level_1' in component['types']:
                    return component['long_name']
    return None

# Function to get the coordinates of an address
def get_coordinates(address, api_key):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    response = requests.get(url).json()
    if response['status'] == 'OK':
        location = response['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

# Function to find the nearest place (e.g., Costco, Walmart, etc.) dynamically based on the amenity
def find_nearest_place(lat, lng, keyword, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=50000&type=store&keyword={keyword}&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        place = response['results'][0]
        place_name = place.get('name', f'{keyword} Store')
        place_address = place.get('vicinity', 'Address not available')
        place_location = place['geometry']['location']
        place_lat = place_location['lat']
        place_lng = place_location['lng']
        distance = geodesic((lat, lng), (place_lat, place_lng)).km
        return place_name, place_address, place_lat, place_lng, round(distance, 2)
    return None, None, None, None, None

# Function to get travel time for a given mode of transportation
def get_travel_time(lat, lng, dest_lat, dest_lng, mode, api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={lat},{lng}&destinations={dest_lat},{dest_lng}&mode={mode}&key={api_key}"
    response = requests.get(url).json()
    if response['rows']:
        element = response['rows'][0]['elements'][0]
        if element['status'] == 'OK':
            duration = element['duration']['text']
            return duration
    return None

# Main script
def main():
    # Load configuration data
    config_data = load_config_data()
    
    # Extract input values from config.json
    google_api_key = config_data['google_maps_api_key']
    ipinfo_key = config_data['ipinfo_io_api_key']
    amenities = config_data['amenities'].split(', ')  # Split the amenities from config.json

    # Set the current province
    province = get_current_province(google_api_key, ipinfo_key)
    if province is None:
        print("Could not determine the current province.")
        return

    print(f"Current province detected: {province}")

    # Load addresses from addresses.csv
    addresses_df = load_addresses()

    # Initialize results
    main_results = []
    travel_time_results = {amenity: [] for amenity in amenities}

    # Process each address from the CSV
    for idx, row in addresses_df.iterrows():
        mls_number = row['MLS']
        address = row['Address']
        
        # Log processing of the current address
        print(f"\nProcessing address: {address}")

        # Get coordinates for the input address
        lat, lng = get_coordinates(address, google_api_key)
        if lat is None or lng is None:
            print(f"Skipping address: {address} - Could not get coordinates")
            continue

        # Store all the dynamic results
        row_result = {
            'MLS': mls_number,
            'Address': address,
        }

        # For each amenity, find the nearest place and get travel times
        for amenity in amenities:
            amenity_name, amenity_address, amenity_lat, amenity_lng, distance_to_amenity = find_nearest_place(lat, lng, amenity, google_api_key)

            if amenity_address:
                row_result[f'{amenity} Name'] = amenity_name
                row_result[f'{amenity} Address'] = amenity_address
                row_result[f'Distance to {amenity} (km)'] = distance_to_amenity

                # Log found amenity
                print(f"- Found {amenity}: {amenity_name}, Distance: {distance_to_amenity} km")

                # Calculate travel times
                walking_time = get_travel_time(lat, lng, amenity_lat, amenity_lng, 'walking', google_api_key)
                biking_time = get_travel_time(lat, lng, amenity_lat, amenity_lng, 'bicycling', google_api_key)
                driving_time = get_travel_time(lat, lng, amenity_lat, amenity_lng, 'driving', google_api_key)

                travel_time_results[amenity].append({
                    'MLS': mls_number,
                    'Address': address,
                    f'{amenity} Name': amenity_name,
                    f'{amenity} Address': amenity_address,
                    f'Distance to {amenity} (km)': distance_to_amenity,
                    f'Walking Time to {amenity}': walking_time,
                    f'Biking Time to {amenity}': biking_time,
                    f'Driving Time to {amenity}': driving_time
                })

        main_results.append(row_result)

    # Save results to Excel with multiple sheets
    main_df = pd.DataFrame(main_results)
    with pd.ExcelWriter('NearbyNestResults.xlsx', engine='openpyxl') as writer:
        main_df.to_excel(writer, sheet_name='Main Sheet', index=False)

        for amenity, result in travel_time_results.items():
            amenity_df = pd.DataFrame(result)
            amenity_df.to_excel(writer, sheet_name=f'{amenity}', index=False)

    print("\nExcel file with multiple sheets created successfully.")

if __name__ == "__main__":
    main()
