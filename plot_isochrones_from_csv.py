
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import plotly.graph_objects as go
from plotly import express as px
import csv
from shapely.geometry import Polygon

load_dotenv()

from traveltimepy import Driving, Coordinates, TravelTimeSdk

async def regular_isochrones(coordinates_list, travel_time):
    sdk = TravelTimeSdk(os.getenv("TRAVEL_TIME_APP_ID"), os.getenv("TRAVEL_TIME_APP_KEY"))

    results = await sdk.time_map_async(
        coordinates=coordinates_list,
        arrival_time=datetime.now(),
        travel_time=travel_time*60, #convert from minutes to seconds
        transportation=Driving()
    )
    return results

def plot_isochrone(fig, result, coordinates_list, travel_time):
    max_points = len(result.shapes)

    for idx, shape in enumerate(result.shapes):
        latitudes = [coord.lat for coord in shape.shell]
        longitudes = [coord.lng for coord in shape.shell]

        fig.add_trace(go.Scattermapbox(
            lat=latitudes,
            lon=longitudes,
            mode='lines',
            line=dict(width=4),
            fill='toself',
            text=f"Isochrone {idx+1}, {travel_time} minutes",
            hoverinfo='text',
            name=f"Isochrone {idx+1}, {travel_time} minutes",
            showlegend=True
        ))

    for coord in coordinates_list:
        fig.add_trace(go.Scattermapbox(
            lat=[coord.lat],
            lon=[coord.lng],
            mode='markers',
            marker=dict(size=8),
            text="Coordinate",
            hoverinfo='text',
            name="Coordinate",
            showlegend=True
        ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=12,
            center=dict(lat=coordinates_list[0].lat, lon=coordinates_list[0].lng)
        ),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    #fig.show()


def get_coords_from_csv(filename):
    coordinates = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            lat, lng, range_ = map(float, row)
            coordinates.append((Coordinates(lat=lat, lng=lng), range_))
    return coordinates


if __name__ == '__main__':
    csv_file = 'input.csv'  # Change 'input.csv' to the name of your CSV file
    coords_ranges = get_coords_from_csv(csv_file)
    fig = go.Figure()

    individual_results = []
    intersection_coords = [coords for coords, _ in coords_ranges]

    for coords, travel_time in coords_ranges:
        single_result = asyncio.run(regular_isochrones([coords], travel_time))[0]
        if len(single_result.shapes) > 1:
            # Only keep the shape with the most points
            print(f"Found {len(single_result.shapes)} shapes for {coords.lat}, {coords.lng}. Keeping the one with the most points.")
            single_result.shapes = [max(single_result.shapes, key=lambda shape: len(shape.shell))]
        individual_results.append(single_result)
        plot_isochrone(fig, single_result, [coords], travel_time)

    fig.show()

    """
    # build a list of polygons from the individual results
    polygons = []
    for time_map_result in individual_results:
        shell = time_map_result.shapes[0].shell
        raw_cords = [(coord.lat, coord.lng) for coord in shell]
        polygons.append(Polygon(raw_cords))

    #polygons = [Polygon(time_map_result.shapes[0].shell) for time_map_result in individual_results]

    # Find the intersection of all polygons
    intersection = polygons[0]
    for polygon in polygons[1:]:
        intersection = intersection.intersection(polygon)
        
    # Convert the intersection to a time map result
    for shape in intersection:
        Coords = [Coordinates(lat=coord[0], lng=coord[1]) for coord in shape.exterior.coords]
        intersection = Driving.Shape(shell=Coords)
    # Plot the intersection
    plot_isochrone(fig, intersection, [], 0)

    fig.show()
    """

