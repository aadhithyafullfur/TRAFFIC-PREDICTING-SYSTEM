import joblib
import pandas as pd

# Load model
model = joblib.load('traffic_classifier.pkl')

# Get locations from model
locations = sorted([col.split('LOCATION_')[-1] for col in model.feature_names_in_ if col.startswith('LOCATION_')])

print('Total locations in model:', len(locations))
print('\nFirst 20 locations:')
for i, loc in enumerate(locations[:20]):
    print(f'{i+1:2d}. {loc}')

print('\nSample of all locations:')
for i in range(0, len(locations), len(locations)//10):
    print(f'{i+1:3d}. {locations[i]}')
