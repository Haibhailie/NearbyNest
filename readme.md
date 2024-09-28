# NearbyNest Configuration Tool

NearbyNest is a tool designed to help you find nearby amenities (such as Costco, Walmart, grocery stores, and more) based on real estate addresses and amenities of interest. It leverages Google Maps APIs and IPinfo.io API to find distances, walking/biking/driving times, and more, and stores this information in a user-friendly format.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup Guide](#setup-guide)
  - [1. Setting Up Google Maps API Key](#1-setting-up-google-maps-api-key)
  - [2. Setting Up IPinfo.io API Key](#2-setting-up-ipinfoio-api-key)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Contributing](#contributing)

---

## Features

- Add MLS and address details through a graphical interface.
- Configure nearby amenities to search for (e.g., Costco, Walmart, Grocery).
- Automatically fetch distances and travel times to amenities using Google Maps.
- Get real-time logs in the console during execution.
- Save and load address and config data in `addresses.csv` and `config.json`.

---

## Requirements

- Python 3.x
- Required Python libraries:

  - `customtkinter`
  - `pandas`
  - `geopy`
  - `requests`
  - `openpyxl`

  You can install all required packages by running:

  ```bash
  pip install -r requirements.txt
  ```

---

## Setup Guide

To use this application, you need to set up two API keys:

### 1. Setting Up Google Maps API Key

The Google Maps API key allows NearbyNest to retrieve geographical information like distances and travel times. Follow these steps to obtain your free Google Maps API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or use an existing one.
3. Enable the following APIs:
   - **Geocoding API**
   - **Places API**
   - **Distance Matrix API**
4. Create an API key:
   - Navigate to **API & Services > Credentials**.
   - Click **Create Credentials** and select **API Key**.
5. Copy the generated API key and save it in your `config.json` file.

#### Google Maps Free Tier:

Google provides $200 of free usage each month, which is enough for most small to medium-sized applications. You can review the pricing details [here](https://cloud.google.com/maps-platform/pricing).

### 2. Setting Up IPinfo.io API Key

IPinfo.io provides IP-based geolocation data, which the app uses to determine the user's location for better address management.

1. Go to [IPinfo.io](https://ipinfo.io/).
2. Sign up for a free account.
3. After logging in, go to the [API Access Token page](https://ipinfo.io/account).
4. Copy your **Access Token** and save it in your `config.json` file.

#### IPinfo.io Free Tier:

IPinfo.io offers a free tier with up to 50,000 API requests per month, which should be more than enough for this application. Check the pricing [here](https://ipinfo.io/pricing).

---

## How It Works

NearbyNest allows you to input MLS numbers and corresponding addresses into the app via a simple graphical interface. Once the addresses are entered, you can specify nearby amenities (like Costco, Walmart, etc.) and the tool will use Google Maps APIs to find the nearest locations of those amenities for each address.

### Application Workflow:

1. **Set Up API Keys**:

   - Add your **Google Maps API key** and **IPinfo.io API key** into the `config.json` file.
   - This file is automatically loaded by the app on startup.

2. **Add Addresses**:

   - You can manually add addresses (with MLS numbers) via the graphical interface.
   - The addresses are saved in `addresses.csv` for future use.

3. **Configure Amenities**:

   - You can list amenities (e.g., Costco, Walmart, Grocery) that the app should search for in your area.

4. **Search**:

   - When you press the **Search** button, the app queries Google Maps for nearby amenities, calculates distances, and displays the data in real-time within the console log.
   - The results are saved to an Excel file (`NearbyNest_results_dynamic_with_names.xlsx`) containing multiple sheets, one for each amenity type.

5. **Log Output**:
   - The console log at the bottom of the interface shows real-time logs of the application's progress, indicating when it finds nearby amenities and completes processing.

---

## Usage

1. **Run the Application**:

   - To run the application, simply execute the following command:

   ```bash
   python NearbyNestUI.py
   ```

2. **Interacting with the Application**:

   - Input your Google Maps API key and IPinfo.io API key in the appropriate fields.
   - Add addresses (with MLS numbers) and configure the amenities of interest.
   - Click **Search** to find nearby amenities and get results saved into an Excel file.

3. **Results**:
   - The results will be saved to an Excel file (`NearbyNestResults.xlsx`) with detailed information about the nearest amenities and distances for each address.

---

## Contributing

Contributions are welcome! Feel free to submit pull requests to improve the functionality, UI, or add new features to the NearbyNest tool.

---

### License

This project is licensed under the MIT License.
