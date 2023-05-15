import os
import csv
import asyncio
from dotenv import load_dotenv
from datetime import datetime
from traveltimepy import (Coordinates, Location, PublicTransport, Property,
                          FullRange, TravelTimeSdk, Driving)
import plotly.graph_objects as go

load_dotenv()

def get_coords_from_csv(filename):
    coordinates = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                lat, lng, range_ = map(float, row)
                label = None
            except ValueError:
                lat, lng, range_ = map(float, row[:-1])
                label = row[-1]
            coordinates.append((Coordinates(lat=lat, lng=lng), range_, label))
    return coordinates


def generate_grid(coords, density):
    # Placeholder grid generation
    return [Coordinates(lat=c[0].lat, lng=c[0].lng) for c in coords]

def generate_grid_v2(coords, density):
    # Average the lat and lng of all the coords to get the center
    lat = sum([c[0].lat for c in coords]) / len(coords)
    lng = sum([c[0].lng for c in coords]) / len(coords)
    center = Coordinates(lat=lat, lng=lng)

    grid_edge_points = 10
    # Generate a grid of points around the center
    grid = []
    for i in range(-grid_edge_points, grid_edge_points + 1):
        for j in range(-grid_edge_points, grid_edge_points + 1):
            grid.append(Coordinates(lat=center.lat + i * density, lng=center.lng + j * density))

    return grid


async def calculate_travel_times(sdk, origins, grid):
    travel_times = {}

    for origin in origins:
        origins = [Location(id=origin[2], coords=origin[0])]
        locations_from_grid = [Location(id=str(i), coords=grid[i]) for i in range(len(grid))]
        locations = origins + locations_from_grid
        search_ids = {origin[2]: [str(i) for i in range(len(grid))]}
        results = await sdk.time_filter_async(
            locations=locations,
            search_ids=search_ids,
            departure_time=datetime.now(),
            travel_time=origin[1]*60*2,
            transportation=Driving(),
            properties=[Property.TRAVEL_TIME],
            range=FullRange(enabled=True, max_results=3, width=600),
        )

        travel_times[origin[2]] = {
            loc.id: loc.properties[0].travel_time for loc in results[0].locations
        }
    return travel_times


def weighted_heatmap(travel_times, grid, ranges):
    # TODO: change this so if a point is unreachable it counts it as the maximum travel time for all points.
    # Load the grid into heatmap from grid initialize to 0
    heatmap = {}
    for i in range(len(grid)):
        heatmap[str(i)] = 0

    # For each location, iterate through the grid and add the travel time to the heatmap
    for loc in travel_times:
        for point in heatmap:
            if point not in travel_times[loc]:
                heatmap[point] += ranges[loc] * 60
            else:
                heatmap[point] += travel_times[loc][point] * (1 / ranges[loc])
    return heatmap
    """
    for loc in travel_times:
        for point, value in travel_times[loc].items():
            if point not in heatmap:
                heatmap[point] = 0
            heatmap[point] += value * (1 / ranges[loc])
    return heatmap
    """


def plot(origins, grid, heatmap):
    data = []
    lats, lons, values = [], [], []

    for point, value in heatmap.items():
        idx = int(point)
        lats.append(grid[idx].lat)
        lons.append(grid[idx].lng)
        values.append(value)

    for origin in origins:
        data.append(
            go.Scattergeo(
                lon=[origin[0].lng],
                lat=[origin[0].lat],
                text=[origin[2]],
                mode='markers',
                marker=dict(color='red', size=10),
            )
        )

    data.append(
        go.Densitymapbox(
            lat=lats,
            lon=lons,
            z=values,
            radius=50,
            colorscale='Jet',
        )
    )

    fig = go.Figure(data=data)
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=12,
                      mapbox_center_lat=origins[0][0].lat, mapbox_center_lon=origins[0][0].lng)
    fig.show()


if __name__ == '__main__':
    filename = 'input.csv'
    density = 10

    sdk = TravelTimeSdk(os.getenv("TRAVEL_TIME_APP_ID"), os.getenv("TRAVEL_TIME_APP_KEY"))
    coords = get_coords_from_csv(filename)
    ranges = {c[2]: c[1] for c in coords}

    grid = generate_grid_v2(coords, 0.01)
    travel_times = asyncio.run(calculate_travel_times(sdk, coords, grid))
    heatmap = weighted_heatmap(travel_times, grid, ranges)
    plot(coords, grid, heatmap)