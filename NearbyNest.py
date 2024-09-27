import requests
import pandas as pd
import json
from geopy.distance import geodesic

# Load Google Maps API key
with open('config.json') as f:
    config = json.load(f)
    api_key = config['google_maps_api_key']
    ipinfo_key = config['ipinfo_io_api_key']

# Function to get the current province using Google Geocoding API
def get_current_province(api_key):
    # Use IP Geolocation to determine your location (Google Maps does not provide this directly)
    ip_location_url = f'https://ipinfo.io?token='+ipinfo_key
    ip_location = requests.get(ip_location_url).json()
    if 'loc' in ip_location:
        lat, lng = ip_location['loc'].split(',')
        # Reverse geocode to get the province using Google API
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
        response = requests.get(geocode_url).json()
        if response['status'] == 'OK':
            for component in response['results'][0]['address_components']:
                if 'administrative_area_level_1' in component['types']:  # 'administrative_area_level_1' is the province/state
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

# Function to find nearest Costco and return its address and distance
def find_nearest_costco(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=50000&type=store&keyword=Costco&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        costco = response['results'][0]
        costco_address = costco.get('vicinity', 'Address not available')  # Get Costco address
        costco_location = costco['geometry']['location']
        costco_lat = costco_location['lat']
        costco_lng = costco_location['lng']
        distance = geodesic((lat, lng), (costco_lat, costco_lng)).km
        return costco_address, round(distance, 2)  # Round distance to 2 significant figures
    return None, None

# Function to find nearest Walmart and return its address and distance
def find_nearest_walmart(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=50000&type=store&keyword=Walmart&key={api_key}"
    response = requests.get(url).json()
    if response['results']:
        walmart = response['results'][0]
        walmart_address = walmart.get('vicinity', 'Address not available')  # Get Walmart address
        walmart_location = walmart['geometry']['location']
        walmart_lat = walmart_location['lat']
        walmart_lng = walmart_location['lng']
        distance = geodesic((lat, lng), (walmart_lat, walmart_lng)).km
        return walmart_address, round(distance, 2)  # Round distance to 2 significant figures
    return None, None

# Main script
def main():
    # Set the current province
    province = get_current_province(api_key)

    if province is None:
        print("Could not determine the current province.")
        return

    print(f"Current province detected: {province}")

    # Load addresses
    df = pd.read_csv('addresses.csv')

    # Initialize a list to store results
    results = []

    # Process each address
    for index, row in df.iterrows():
        address = row['Address']
        
        # Debug: print current address and province
        print(f"Processing address: {address} for province: {province}")
        
        # Check if the address contains a city in the current province (we'll assume province filtering for now)
        lat, lng = get_coordinates(address, api_key)
        if lat is None or lng is None:
            print(f"Skipping address: {address} - Could not get coordinates")
            continue

        # Find nearest Costco
        costco_address, distance_to_costco = find_nearest_costco(lat, lng, api_key)
        # Find nearest Walmart
        walmart_address, distance_to_walmart = find_nearest_walmart(lat, lng, api_key)

        if costco_address and distance_to_costco and walmart_address and distance_to_walmart:
            results.append({
                'MLS': row['MLS'],
                'Address': address,
                'Costco Address': costco_address,
                'Distance to Costco (km)': distance_to_costco,
                'Walmart Address': walmart_address,
                'Distance to Walmart (km)': distance_to_walmart
            })
        else:
            print(f"No Costco or Walmart found for address: {address}")

    if not results:
        print("No results were generated. Ensure addresses are in the current province or check for errors.")

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)

    # Save results to CSV
    result_df.to_csv('results.csv', index=False)
    print("CSV with Costco and Walmart distances generated successfully.")

if __name__ == "__main__":
    main()
