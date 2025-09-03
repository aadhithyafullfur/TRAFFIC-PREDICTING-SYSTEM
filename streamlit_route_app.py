import streamlit as st
import pandas as pd
import joblib
import openrouteservice
from openrouteservice import convert
import folium
from streamlit_folium import folium_static
from config import ORS_API_KEY

model = joblib.load("traffic_classifier.pkl")
traffic_data = pd.read_csv("bangalore_traffic.csv")

st.title("🚦 Smart Traffic Predictor & Route Advisor")

location_list = sorted({col.split("LOCATION_")[-1] for col in model.feature_names_in_ if col.startswith("LOCATION_")})
weather_options = ["Clear", "Rainy", "Cloudy", "Foggy"]

from_location = st.selectbox("📍 From", location_list)
to_location = st.selectbox("📍 To", location_list)
weather = st.selectbox("🌤️ Weather", weather_options)
hour = st.slider("⏰ Hour of Day", 0, 23, 9)

filtered = traffic_data[
    (traffic_data["LOCATION"] == to_location) &
    (pd.to_datetime(traffic_data["TIME"], format="%H:%M").dt.hour == hour)
]
vehicle_count = int(filtered["VEHICLE_COUNT"].mean()) if not filtered.empty else 75
st.number_input("🚗 Estimated Vehicle Count", value=vehicle_count, disabled=True)

input_data = pd.DataFrame(columns=model.feature_names_in_)
input_data.loc[0] = 0
input_data.at[0, "HOUR"] = hour
input_data.at[0, "VEHICLE_COUNT"] = vehicle_count

weather_col = f"WEATHER_{weather}"
to_col = f"LOCATION_{to_location}"
if weather_col in input_data.columns:
    input_data.at[0, weather_col] = 1
if to_col in input_data.columns:
    input_data.at[0, to_col] = 1

prediction = model.predict(input_data)[0]
label = "🟢 Low Traffic" if prediction == 0 else "🔴 High Traffic"
st.markdown(f"### 🚩 Predicted Traffic at Destination: **{label}**")

coords_map = {
    "1st Cross": (12.9716, 77.5946),
    "1st Main Road": (12.9784, 77.5994),
    "2nd Cross": (12.9352, 77.6245),
    "2nd Cross Road": (12.9628, 77.6447),
    "2nd Main Road": (12.9863, 77.6189),
    "3rd Cross": (12.9256, 77.6693),
    "4th Cross": (12.9087, 77.6014),
    "Albert Victor Road": (12.9663, 77.5967),
    "Ali Asker Road": (12.9945, 77.5861),
    "Annaswamy Mudaliar Road": (12.9665, 77.5942),
    "Artillery Road": (12.9759, 77.6158),
    "Assayyee Road - Annaswamy Mudaliar Road": (12.9653, 77.5951),
    "Atturu-Ananthapura Road": (12.9001, 77.5623),
    "Avenue Road": (12.9732, 77.5816),
    "Bangalore University Road": (13.0344, 77.5652),
    "Banasawadi-Ramamurthynagar Road": (13.0139, 77.6612),
    "Bannerghatta Road": (12.8913, 77.5979),
    "Bazaar Street": (12.9675, 77.5783),
    "Bedarahalli-Ullalu Road": (12.8614, 77.5337),
    "Begur Main Road": (12.8581, 77.6412),
    "Bellary Road": (13.0068, 77.5893),
    "Berlie Street": (12.9731, 77.6118),
    "Bhaskaran Road": (12.9497, 77.5843),
    "Bilesivali-LG Layout Road": (12.9542, 77.5347),
    "Bride Street": (12.9765, 77.6091),
    "Brigade Road": (12.9754, 77.6045),
    "Brunton Road": (12.9761, 77.6073),
    "BTM Layout": (12.9162, 77.6101),
    "Buddha Vihar Road": (12.9578, 77.5489),
    "Byappanahalli Main Road": (12.9782, 77.6385),
    "Campbell Road": (12.9892, 77.5819),
    "Castle Street": (12.9738, 77.5967),
    "Central Street": (12.9739, 77.6112),
    "Chamarajpet - Sarjapur Road": (12.9541, 77.5653),
    "Chikkabanavara Road": (13.0637, 77.5243),
    "Chikkabidarakal Main Road": (12.9056, 77.4902),
    "Church Street": (12.9723, 77.6118),
    "City Bus Road": (12.9779, 77.5716),
    "Cleveland Road": (12.9726, 77.6089),
    "Coles Road": (12.9917, 77.5991),
    "Commercial Street": (12.9771, 77.6105),
    "Commissariat Road": (12.9738, 77.6115),
    "Convent Road": (12.9712, 77.6062),
    "Crescent Road": (12.9881, 77.5931),
    "Cubbon Road": (12.9765, 77.5947),
    "Cunningham Crescent": (12.9735, 77.6047),
    "Cunningham Road": (12.9789, 77.6022),
    "Cunningham Road Cross": (12.9794, 77.6015),
    "Curley Street": (12.9748, 77.6137),
    "Devasandra - Kadugodi Road": (12.9932, 77.7321),
    "Devanga Hostel Road": (12.9628, 77.5791),
    "Diagonal Road": (12.9762, 77.5923),
    "Dickenson Road": (12.9715, 77.6221),
    "Dispensary Road": (12.9697, 77.5987),
    "Doddabailakere Road": (12.9378, 77.5113),
    "Double Road": (12.9632, 77.5841),
    "Dr BR Ambedkar Veedhi": (12.9764, 77.5925),
    "Dr.Rajkumar Road": (12.9981, 77.5521),
    "Electronic City Phase 1": (12.8456, 77.6643),
    "Gunjur-Hosahalli Road": (12.9274, 77.7001),
    "HAL Wind Tunnel - Belur Road": (12.9532, 77.6732),
    "Haines Road": (12.9584, 77.6037),
    "Handrahalli Main Road": (12.8765, 77.5732),
    "Hanumanthaiah-KM Kariappa Road": (12.9751, 77.5902),
    "Hegganahalli Main Road": (13.0432, 77.5134),
    "Hennur Main Road": (13.0415, 77.6213),
    "Hesaraghatta Road": (13.1347, 77.4875),
    "Hosakerehalli Main Road": (12.9134, 77.5623),
    "Hospital Road": (12.9667, 77.5873),
    "Hosur Road": (12.9169, 77.6298),
    "Hosur-Bommanahalli-Madivala-Adugodi-Vellara Junction": (12.9356, 77.6145),
    "Indiranagar 100 Feet Road": (12.9784, 77.6392),
    "Infantry Road": (12.9812, 77.5998),
    "Jayachamaraja Wodeyar Road": (12.9738, 77.5876),
    "Jewellers Street": (12.9682, 77.5801),
    "Kachohalli-Gangadanahalli-Dombarahalli Road": (12.9023, 77.4765),
    "Kaikondanahalli Main Road": (12.9314, 77.6765),
    "Kamaraj Road": (12.9761, 77.5921),
    "Kanakapura Road": (12.8994, 77.5621),
    "Kanteerava Studio Road - MEI Road": (12.9892, 77.5943),
    "Kasturba Road": (12.9746, 77.5932),
    "Kenchenahalli Road": (12.9321, 77.6234),
    "KH Road (Double Road)": (12.9632, 77.5841),
    "Koramangala 5th Block": (12.9345, 77.6232),
    "Koramangala - Indiranagar Road": (12.9654, 77.6287),
    "Kothnur-Puttenahalli Road": (12.8723, 77.5432),
    "Laggere Main Road": (13.0213, 77.5213),
    "Lalbagh Road": (12.9507, 77.5841),
    "Langford Road": (12.9574, 77.5978),
    "Lavelle Road": (12.9709, 77.6012),
    "Linden Street": (12.9723, 77.6118),
    "Link Road": (12.9843, 77.6123),
    "M. Chinnaswamy Stadium Road": (12.9784, 77.5994),
    "Magadi Road - Kasturba Road - Varthur Road": (12.9654, 77.5578),
    "Magrath Road": (12.9632, 77.6001),
    "Mahadevapura Road": (12.9912, 77.6987),
    "Mahatma Gandhi Road": (12.9765, 77.6045),
    "Mallathahalli Main Road": (12.9432, 77.5345),
    "Markham Road": (12.9667, 77.6132),
    "MEI Road": (12.9892, 77.5943),
    "Millers Road": (12.9873, 77.5932),
    "Millers Tank Bund Road": (12.9854, 77.5921),
    "Mission Road": (12.9601, 77.5887),
    "Mother Teresa Road": (12.9712, 77.5967),
    "Muddinapalya Road": (12.9154, 77.6432),
    "Mysore Road": (12.9563, 77.5132),
    "Mysore Road Flyover": (12.9584, 77.5143),
    "Mysore-Old Madras Road": (12.9213, 77.6745),
    "Nagavara Main Road": (13.0432, 77.6213),
    "Nagarbhavi Main Road": (12.9432, 77.5123),
    "Netaji Road": (12.9654, 77.5789),
    "Norris Street": (12.9745, 77.6098),
    "Old Madras Road": (12.9987, 77.6789),
    "ORR (Outer Ring Road)": (12.9345, 77.6891),
    "Outer Ring Road": (12.9345, 77.6891),
    "Palm Grove Road": (12.9678, 77.6032),
    "Panathur Road": (12.9312, 77.6789),
    "Palace Road": (12.9987, 77.5921),
    "Pipeline Road": (12.9543, 77.5432),
    "Police Road": (12.9765, 77.5876),
    "Post Office Road": (12.9632, 77.5789),
    "Prime Street": (12.9721, 77.6045),
    "Primrose Road": (12.9745, 77.6078),
    "Promenade Road": (12.9892, 77.5943),
    "Puttalingaiah Road - Subram Chetty Road": (12.9543, 77.5789),
    "Queen's Road": (12.9812, 77.5921),
    "Race Course Road": (12.9843, 77.5987),
    "Raj Bhavan Road": (12.9876, 77.5943),
    "Rajaram Mohan Roy Road": (12.9632, 77.5789),
    "Rajbhavan Road - Chowdaiah Road - Bellary Road": (12.9912, 77.5943),
    "Ramamurthynagar Road": (13.0132, 77.6789),
    "Ramagondanahalli Road": (12.9213, 77.5432),
    "R.V. Road": (12.9432, 77.5678),
    "Residency Road": (12.9712, 77.6012),
    "Rest House Crescent": (12.9789, 77.5987),
    "Richmond Road": (12.9612, 77.6012),
    "Sonnenahalli-Muggalipalya Road": (12.9432, 77.6789),
    "Saint John's Church Road": (12.9765, 77.5987),
    "Saint Mark's Road": (12.9723, 77.6118),
    "Sarjapura Road": (12.9012, 77.6891),
    "Shankar Mutt Road - Vanivilas Road": (12.9432, 77.5789),
    "Sheshadri Road": (12.9632, 77.5789),
    "Shivaji Road": (12.9784, 77.5994),
    "Silver Jubilee Park Road": (12.9543, 77.5432),
    "South End Street": (12.9543, 77.5789),
    "Sri Rama Temple Street": (12.9432, 77.5678),
    "St.Mark's Road": (12.9723, 77.6118),
    "State Bank Road": (12.9789, 77.5987),
    "Subramanyapura-Vasanthapura Main Road": (12.9213, 77.5432),
    "Subratho Mukherjee - Jalahalli Road": (13.0432, 77.5432),
    "Suranjandas Road": (12.9632, 77.5789),
    "T Chowdiah Road": (12.9912, 77.5943),
    "Tank Bund Road": (12.9854, 77.5921),
    "Tavarekere Main Road": (12.8765, 77.5732),
    "Thimmaiah Road": (12.9987, 77.5921),
    "Tindlu Main Road": (13.0432, 77.5432),
    "Trinity Church Road": (12.9723, 77.6118),
    "Uttarahalli Main Road": (12.9012, 77.5432),
    "Vatal Nagaraj Road": (12.9543, 77.5789),
    "Venkataswamy Naidu Road": (12.9432, 77.5789),
    "Victoria Road": (12.9667, 77.5873),
    "Vidyaranyapura Road": (13.0789, 77.5432),
    "Walker Lane": (12.9745, 77.6078),
    "Wellington Street": (12.9765, 77.6045),
    "Whitefield Main Road": (12.9784, 77.7321),
    "Whitefield - Channasandra Road": (12.9912, 77.6987),
    "Whitefield Road - Varthur Road": (12.9654, 77.7321),
    "Wood Street": (12.9712, 77.6012),
    "Yeshwanthpura 1st Main Road": (13.0213, 77.5432),
    "Silk Board": (12.9172, 77.6237),
    "Marathahalli": (12.9592, 77.6974),
    "Whitefield": (12.9698, 77.7499),
    "Hebbal": (13.0358, 77.5970),
    "Electronic City": (12.8452, 77.6604),
    "Majestic": (12.9763, 77.5715)

}
if from_location in coords_map and to_location in coords_map and from_location != to_location:
    client = openrouteservice.Client(key=ORS_API_KEY)
    from_coords = coords_map[from_location][::-1]
    to_coords = coords_map[to_location][::-1]

    try:
        route = client.directions(
            coordinates=[from_coords, to_coords],
            profile='driving-car',
            format='geojson',
            validate=True,
            optimize_waypoints=True,
            alternative_routes={"share_factor": 0.5, "target_count": 3},
        )

        midpoint = [
            (coords_map[from_location][0] + coords_map[to_location][0])/2,
            (coords_map[from_location][1] + coords_map[to_location][1])/2
        ]
        m = folium.Map(location=midpoint, zoom_start=13)

        features = route['features']
        route_details = []
        
        for feature in features:
            summary = feature['properties']['summary']
            route_details.append({
                'distance': summary['distance']/1000,
                'duration': summary['duration']/60,
                'feature': feature
            })

        best_index = min(enumerate(route_details), 
                       key=lambda x: (x[1]['duration'], x[1]['distance']))[0]

        colors = ['blue', 'green', 'purple']
        best_route = None
        
        for i, detail in enumerate(route_details):
            if i == best_index:
                continue  # Skip best route for now
            
            current_color = colors[i % len(colors)]
            folium.GeoJson(
                detail['feature'],
                name=f"Route {i+1}",
                style_function=lambda x, color=current_color: {
                    'color': color,
                    'weight': 4,
                    'opacity': 0.7
                }
            ).add_to(m)

        best_detail = route_details[best_index]
        folium.GeoJson(
            best_detail['feature'],
            name=f"Best Route {best_index+1}",
            style_function=lambda x: {
                'color': 'orange',
                'weight': 6,
                'opacity': 1
            }
        ).add_to(m)

        folium.Marker(coords_map[from_location], popup=f"From: {from_location}", 
                     icon=folium.Icon(color="green", icon="play")).add_to(m)
        folium.Marker(coords_map[to_location], popup=f"To: {to_location}", 
                     icon=folium.Icon(color="red", icon="stop")).add_to(m)


        st.markdown("### 🗺️ Route Map")
        folium_static(m, width=800, height=500)

        st.markdown("### 📊 Route Analysis")
        

        cols = st.columns(len(route_details))
        
        for i, detail in enumerate(route_details):
            with cols[i]:
                is_best = i == best_index
                emoji = "🌟" if is_best else "🔹"
                color = "#ff9900" if is_best else colors[i % len(colors)]
                
                st.markdown(f"""
                <div style='border: 2px solid {color}; border-radius: 5px; padding: 10px; margin: 5px;
                            {"background: #fff7e6" if is_best else ""}'>
                    <h4>{emoji} Route {i+1}</h4>
                    📏 Distance: {detail['distance']:.1f} km<br>
                    ⏱️ Time: {detail['duration']:.1f} mins
                    {"<br>🚗 Best Route Recommendation" if is_best else ""}
                </div>
                """, unsafe_allow_html=True)

        st.success(f"""
        **Recommended Route: Route {best_index+1}**
        - Total Distance: {best_detail['distance']:.1f} km
        - Estimated Time: {best_detail['duration']:.1f} minutes
        - Chosen for optimal balance of travel time and distance
        - Incorporates historical traffic patterns at {hour}:00
        """)

    except Exception as e:
        st.error(f"Failed to fetch routes: {str(e)}")
else:
    st.warning("Please select different start and end locations")