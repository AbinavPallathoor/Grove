import streamlit as st
import datetime
import math
import requests
import json
import pandas as pd
import bcrypt
import folium
from streamlit_folium import st_folium
import base64
import os

# Styling for Streamlit app
page_bg = """
<style>
.stApp {
    background-image: url("https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/background2.png");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    div[data-baseweb="input"] > div {
        background-color: #663600;
        border: 0px solid #1abc9c;
        border-radius: 0px;
    }
    div[data-baseweb="input"] input {
        color: #ffe7ba;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    * {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #3a5a40;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffe7ba;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #52361e;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] * {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: 18px;
        color: #ffffff;
    }
    .st-emotion-cache-ujm5ma {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #944f01;
        color: white;
        height: 50px;
        width: 120px;
        font-size: 40px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #ffe7ba;
        color: #FDFEFE;
        border: 2px solid #52361e;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Backend logic from grove.1.py
channel_id = "3045528"
read_api_key = "8Q9268X6ISZE84W9"
url = f"https://api.thingspeak.com/channels/{3045528}/feeds.json"
params = {
    'api_key': "8Q9268X6ISZE84W9",
    'results': 1
}


phi = 0.2257  # latitude of Vellore in Radians
M = 80  # assumed soil moisture after each time the plant is watered

#ROOT NODE DETAILS
channel_id = "3045528"
read_api_key = "8Q9268X6ISZE84W9"

# URL to get the last entry of the channel feed
url = f"https://api.thingspeak.com/channels/{3045528}/feeds.json"

params = {
    'api_key': '8Q9268X6ISZE84W9',
    'results': 1
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if data['feeds']:
        last_entry = data['feeds'][0]
        entry_id = last_entry['entry_id']
        created_at = last_entry['created_at']
        
        print(f"Retrieved data for Entry ID: {entry_id} at {created_at}")

        # Loop specifically through fields 1 to 5
        for i in range(1, 7):  
            field_key = f"field{i}"
            if field_key in last_entry and last_entry[field_key] is not None:
                value = last_entry[field_key]
                print(f"  - Field {i}: {value}")
    else:
        print("The channel feed is empty.")

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")


dt=datetime.datetime.now()
J1=0
print(type(dt.month))
if dt.month==2:
    J1=31
elif dt.month==3:
    J1=59
elif dt.month==4:
    J1=90
elif dt.month==5:
    J1=120
elif dt.month==6:
    J1=151
elif dt.month==7:
    J1=181
elif dt.month==8:
    J1=212
elif dt.month==9:
    J1=243
elif dt.month==10:
    J1=273
elif dt.month==11:
    J1=304
elif dt.month==12:
    J1=334
print(type(dt.day))
J=J1+(dt.day) #calculated day of the year
phi=0.2257 #latitude of Vellore in Radians
M=80 #assumed soil moisture after each time the plant is watered when soil


def calculate_ra(J): #calculation of extraterrestrial radiation
    dr = 1 + 0.033 * math.cos(2 * math.pi * J / 365)
    delta = 0.409 * math.sin(2 * math.pi * J / 365 - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta))
    ra = (24 * 60 / math.pi) * 0.0820 * dr * (ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)) # formula used
    return ra


def calculate_et(Tmin,Tmax,ra,humidity):
    Tmean=(Tmax+Tmin)/2
    et=0.0023*ra*(Tmean+17.8)*math.sqrt(Tmax-Tmin)*((1-(humidity/100))**0.5)
    return et

def dep_rate(et):
    dr=(et/200)*100 # depth of soil water assumed to be 200mm
    return dr

def tt(dr):
    t=(M-10)/dr
    a1=t*24
    hrs=math.floor(a1)
    mins=round((a1-hrs)*60)
    tfinal=str(hrs)+"hours, "+str(mins)+"minutes."
    print(tfinal)
    return tfinal

def recalc(M1,dr,t):
    depth=M1*2
    depth2=depth-((t/24)*dr)
    M=depth2/2


def calculate_julian_day():
    dt = datetime.datetime.now()
    J1 = 0
    if dt.month == 2:
        J1 = 31
    elif dt.month == 3:
        J1 = 59
    elif dt.month == 4:
        J1 = 90
    elif dt.month == 5:
        J1 = 120
    elif dt.month == 6:
        J1 = 151
    elif dt.month == 7:
        J1 = 181
    elif dt.month == 8:
        J1 = 212
    elif dt.month == 9:
        J1 = 243
    elif dt.month == 10:
        J1 = 273
    elif dt.month == 11:
        J1 = 304
    elif dt.month == 12:
        J1 = 334
    J = J1 + dt.day
    return J

USER_DB = "C:\\Users\\Antranig\\Desktop\\GROVE\\users.json"

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)


def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_tree_icon_url(health):
    if health < 25:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree25.png"
    elif health <= 70:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree70.png"
    else:
        return "https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/tree100.png"

def main():
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Placeholder for logo image (update path or use URL if needed)
        st.image("C:\\Users\\Antranig\\Desktop\\GROVE\\Picture1.png")

        menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Dashboard"])

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ""

        if menu == "Register":
                st.subheader("Create New Account")
                new_user = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                if st.button("Register"):
                    users = load_users()

                    if new_user in users:
                        st.error("Username already exists.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif new_user == "" or new_password == "":
                        st.warning("Fields cannot be empty.")
                    else:
                        users[new_user] = hash_password(new_password)
                        save_users(users)
                        st.success("Account created successfully! Please login.")

        elif menu == "Login":
            st.subheader("LOGIN HERE!")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
        
            if st.button("Login"):
                users = load_users()

            if username in users and verify_password(password, users[username]):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")

        elif menu == "Dashboard":
            if st.session_state.get("logged_in", False):
                st.header(f"Hello, {st.session_state['username']}!")
                st.subheader("Trees in your neighbourhood")

                # Fetch sensor data
                last_entry =last_entry = data['feeds'][0]
                sensor_data = {}
                if last_entry:
                    for i in range(1, 7):
                        field_key = f"field{i}"
                        if last_entry[field_key] and last_entry[field_key].strip():  # Check if not empty
                            try:
                                sensor_data[field_key] = float(last_entry[field_key])
                            except ValueError:
                                sensor_data[field_key] = 0.0  # Default value if conversion fails
                        else:
                            sensor_data[field_key] = 0.0  # Default value for empty fields

                # Calculate Julian day and evapotranspiration
                J = calculate_julian_day()
                ra = calculate_ra(J)
                Tmin = sensor_data.get("field1", 25.0)  # Default Tmin if not available
                Tmax = sensor_data.get("field2", 35.0)  # Default Tmax if not available
                humidity = sensor_data.get("field3", 50.0)  # Default humidity
                et = calculate_et(Tmin, Tmax, ra, humidity)
                dr = dep_rate(et)
                irrigation_time = tt(dr)

                # Define sensors with updated data
                sensors = {
                    "Greeno": [(12.96947962281231, 79.15840797707915), 80, f"Tuesday, 12:45pm, Irrigation: {irrigation_time}"],
                    "Tank": [(12.970008248014226, 79.15841899890708), 60, f"Sunday, 12:45pm, Irrigation: {irrigation_time}"],
                    "Wood": [(12.96986963409287, 79.1589965417121), 20, f"Monday, 12:45pm, Irrigation: {irrigation_time}"]
                }

                # Create Folium map
                avg_lat = sum([coords[0] for coords, _, _ in sensors.values()]) / len(sensors)
                avg_lon = sum([coords[1] for coords, _, _ in sensors.values()]) / len(sensors)
                m = folium.Map(
                    location=[avg_lat, avg_lon],
                    zoom_start=18,
                    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                    attr="Google Satellite"
                )

                for name, (coords, health, time) in sensors.items():
                    folium.Marker(
                        location=coords,
                        popup=f"<b>{name}</b><br>{time}<br>Health: {health}",
                        icon=folium.CustomIcon(get_tree_icon_url(health), icon_size=(60, 60))
                    ).add_to(m)

                st_folium(m, width=800, height=500)

                # Display sensor data and calculations
                st.subheader("Sensor Data and Irrigation Details")
                if last_entry:
                    st.write(f"Retrieved data for Entry ID: {last_entry['entry_id']} at {last_entry['created_at']}")
                    for i in range(1, 7):
                        field_key = f"field{i}"
                        if field_key in sensor_data:
                            st.write(f"Field {i}: {sensor_data[field_key]}")
                    st.write(f"Evapotranspiration (ET): {et:.2f} mm/day")
                    st.write(f"Irrigation Timing: {irrigation_time}")
                else:
                    st.warning("No sensor data available.")

            else:
                st.warning("⚠️ Please login first to access the dashboard.")

    with col3:
        if st.session_state.logged_in:
            st.sidebar.success(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.rerun()

if __name__ == '__main__':
    main()