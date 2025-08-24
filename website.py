import streamlit as st
import pandas as pd
import pydeck as pdk

# Sensor Positions
# Format: "Name" [(lat, lon), health, time_to_water]
sensors = {
    "Bob": [(12.97104135751912, 79.16379375663011), 50, "Sunday, 12:45pm"],
    "Rob": [(12.971529475267, 79.16343174675109), 100, "Sunday, 12:45pm"]
}

names = list(sensors.keys())
lats = [sensors[n][0][0] for n in names]
lons = [sensors[n][0][1] for n in names]
infos = [f"{name}\n{sensors[name][2]}" for name in sensors]

# Sensor Plots
df = pd.DataFrame({
    'lat': lats,
    'lon': lons,
    'info': infos
})

# Add an icon definition per row (replace the URL with your own PNG if you like)
df["icon_data"] = [{
    "url": "tree.png",  # <-- your icon PNG here
    "width": 128,
    "height": 128,
    "anchorY": 128   # anchors the bottom of the icon at the coordinate
} for _ in range(len(df))]

# Icon layer (image marker instead of circle)
icon_layer = pdk.Layer(
    "IconLayer",
    data=df,
    get_icon="icon_data",
    get_position="[lon, lat]",
    get_size=4,        # base size in pixels
    size_scale=10,     # scales the size up (tweak as needed)
    pickable=True
)

# View state
view_state = pdk.ViewState(
    latitude=lats[0],
    longitude=lons[0],
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
