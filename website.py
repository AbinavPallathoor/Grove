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

# Sensor Positions
sensors = {
    "Greeno": [(12.96947962281231, 79.15840797707915), 80, "Tuesday, 12:45pm"],
    "Tank": [(12.970008248014226, 79.15841899890708), 60, "Sunday, 12:45pm"],
    "Wood": [(12.96986963409287, 79.1589965417121), 20, "Monday, 12:45pm"]
}

# Build DataFrame
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

# Icon layer with dynamic image
icon_layer = pdk.Layer(
    "IconLayer",
    data=df,
    get_icon="icon_data",  # Now points to single column with all icon details
    get_position='[lon, lat]',
    get_size=4,
    size_scale=16,
    pickable=True
)

# View state
view_state = pdk.ViewState(
    latitude=df["lat"].mean(),
    longitude=df["lon"].mean(),
    zoom=18,
    pitch=0
)

# Render map
st.pydeck_chart(
    pdk.Deck(
        layers=[icon_layer],
        initial_view_state=view_state,
        tooltip={"text": "{info}"}
    )
)
