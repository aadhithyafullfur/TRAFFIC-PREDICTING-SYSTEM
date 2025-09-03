import openrouteservice
from openrouteservice import convert

api_key = "5b3ce3597851110001cf624814b4a4ce25c54048af11a14163f28d54"
client = openrouteservice.Client(key=api_key)

start_coords = (77.6045, 12.9754)  # (lon, lat)
end_coords = (77.6392, 12.9784)    # (lon, lat)

route = client.directions(
    coordinates=[start_coords, end_coords],
    profile='driving-car',
    format='geojson'
)

print(route)
