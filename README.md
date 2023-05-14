# Isochrone Map Plotter

This script reads a list of coordinates and travel times from an input CSV file, and plots isochrone maps based on these values using Plotly. An isochrone map represents areas that can be reached within a given travel time from a specific location. The script uses the TravelTime API to fetch the isochrone data and draws the corresponding polygons on a map.

## Prerequisites

Please ensure you have Python 3.6+ and have installed the necessary dependencies listed in the `requirements.txt` file. You can install these dependencies using the following command:

```bash
pip install -r requirements.txt
```

You must also have a valid TravelTime API key. Set your API credentials in a `.env` file with the following format:

```
TRAVEL_TIME_APP_ID=your_app_id
TRAVEL_TIME_APP_KEY=your_app_key
```

Replace `your_app_id` and `your_app_key` with your actual credentials.

## Input

The script requires a CSV file containing latitude, longitude, and travel time (in minutes) for each coordinate. The file should be formatted as follows:

```
latitude,longitude,travel_time
```

For example:

```
51.5074,-0.1278,15
48.8566,2.3522,10
```

Save this CSV file in the same directory as the script and update the `csv_file` variable in the script to the CSV file's name:

```python
csv_file = 'input.csv'  # Change 'input.csv' to the name of your CSV file
```

## Running the Script

Run the script using the following command:

```bash
python isochrone_map_plotter.py
```

The script will read the input CSV file, fetch the isochrone data from the TravelTime API, and plot the isochrone map in your browser using Plotly. You can interact with the map, zooming and panning to explore the isochrones.

## Output

The generated isochrone map will be displayed in your browser, where you can interact with it. Each isochrone polygon will be labeled according to its corresponding coordinate and travel time. The points from the input CSV file are also plotted and labeled as "Coordinate".