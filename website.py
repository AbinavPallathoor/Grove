import streamlit as st
import pandas as pd
import pydeck as pdk

# Function to choose image based on health
def get_tree_icon_url(health):
    if health < 25:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree25.png"
    elif health <= 70:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree70.png"
    else:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree100.png"

# Sensor Positions: "Name" -> [(lat, lon), health, time_to_water]
sensors = {
    "Bob": [(12.97104135751912, 79.16379375663011), 50, "Sunday, 12:45pm"],
    "Rob": [(12.971529475267, 79.16343174675109), 100, "Sunday, 12:45pm"]
}

# Prepare dataframe with dynamic icon URLs
rows = []
for name, (coords, health, time) in sensors.items():
    rows.append({
        "lat": coords[0],
        "lon": coords[1],
        "info": f"{name}\n{time}",
        "icon_data": {
            "url": get_tree_icon_url(health),
            "width": 128,
            "height": 128,
            "anchorY": 128
        }
    })

df = pd.DataFrame(rows)

# Icon layer
icon_layer = pdk.Layer(
    "IconLayer",
    data=df,
    get_icon="icon_data",
    get_position="[lon, lat]",
    get_size=4,
    size_scale=12,
    pickable=True
)

# View state
view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=18,
    pitch=0
)

# Render
st.pydeck_chart(
    pdk.Deck(
        layers=[icon_layer],
        initial_view_state=view_state,
        tooltip={"text": "{info}"}
    )
)
