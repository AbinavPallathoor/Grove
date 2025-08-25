import datetime
import time
import math
import requests
import json
import streamlit as st
import pandas as pd
import bcrypt
import os
import pydeck as pdk
import folium 
import base64





page_bg = """
<style>
.stApp {
    background-image: url("https://raw.githubusercontent.com/AbinavPallathoor/Grove/refs/heads/main/background2.png");
    background-size: cover;
    background-position: center;1
    background-repeat: no-repeat;
    background-attachment: fixed;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

col1, col2, col3, = st.columns([1,4,1])

with col2:
    st.image("C:\\Users\\Antranig\\Desktop\\GROVE\\Picture1.png")

st.markdown(                 #text_input data
    """
    <style>

    div[data-baseweb="input"] > div {
        background-color: #663600; 
        border: 0px solid #1abc9c;   
        border-radius:  0px;
    }

    div[data-baseweb="input"] input {
        color: #ffe7ba;              
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(         #general font
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

st.markdown(                #general Background
    """
    <style>
    .stApp {
        background-color: #ffe7ba;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(               #sidebar background
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

st.markdown(               #sidebar font
    """
    <style>
    [data-testid="stSidebar"] * {
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: 18px;
        color: #3a5a40;
    }

    .st-emotion-cache-ujm5ma {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(             #buton
    """
    <style>
    div.stButton > button {
        background-color: #944f01;  
        color: white;  
        height: 50px;
        width: 120px;
        font-size: 40xpx;
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
Tmin=25
Tmax=35

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

def tt(dr,M):
    t=(M-10)/dr
    a1=t*24
    hrs=math.floor(a1)
    mins=round((a1-hrs)*60)
    tfinal=hrs+"hours, "+mins+"minutes."
    print(tfinal)
    return tfinal

def recalc(M1,dr,t):
    depth=M1*2
    depth2=depth-((t/24)*dr)
    M=depth2/2
    return M




n1=[]
time1=0
water1=0
humidity1=0
temp1=0
dr1=0
Mois1=0

n2=[]
time2=0
water2=0
humidity2=0
temp2=0
dr2=0
Mois2=0

n3=[]
time3=0
water3=0
humidity3=0
temp3=0
dr3=0
Mois3=0

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

        # Loop specifically through fields 1 to 6
        for i in range(1, 7):  
            field_key = f"field{i}"
            if field_key in last_entry and last_entry[field_key] is not None:
                value = last_entry[field_key]
                n1.append(value)
    else:
        n1.append(0)

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")

temp1,humidity1,Mois1,time1,dr1,water1=[n1]


#NODE 1
channel_id = "3045635" 
read_api_key = "E6K7GOO43DZHXP3Y" 

# URL to get the last entry of the channel feed
url = f"https://api.thingspeak.com/channels/{3045635}/feeds.json"

params = {
    'api_key': "E6K7GOO43DZHXP3Y",
    'results': 1
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if data['feeds']:
        last_entry = data['feeds'][0]
        entry_id = last_entry['entry_id']

        # Loop specifically through fields 1 to 6
        for i in range(1, 7):
            field_key = f"field{i}"
            if field_key in last_entry and last_entry[field_key] is not None:
                value = last_entry[field_key]
                n2.append(value)
    else:
        print("The channel feed is empty.")
        n2.append(0)

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")

temp2,humidity2,Mois2,time2,dr2,water2=[n2]


#NODE 2
channel_id = "3045636" 
read_api_key = "LA7J1IB3Z00RF10Z" 

# URL to get the last entry of the channel feed
url = f"https://api.thingspeak.com/channels/{3045636}/feeds.json"

params = {
    'api_key': "LA7J1IB3Z00RF10Z",
    'results': 1
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if data['feeds']:
        last_entry = data['feeds'][0]
        entry_id = last_entry['entry_id']

        # Loop specifically through fields 1 to 6
        for i in range(1, 7):
            field_key = f"field{i}"
            if field_key in last_entry and last_entry[field_key] is not None:
                value = last_entry[field_key]
                n3.append(value)
    else:
        print("The channel feed is empty.")
        n3.append(0)

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")

temp3,humidity3,Mois3,time3,dr3,water3=[n3]

t1=time1-dt
t2=time2-dt
t3=time3-dt

ra1=calculate_ra(J)
et1=calculate_et(Tmin,Tmax,ra1,humidity1)
dr1=dep_rate(et1)
tfinal1=tt(dr1,Mois1)
Mois1=recalc(Mois1,dr1,t1)

ra2=calculate_ra(J)
et2=calculate_et(Tmin,Tmax,ra2,humidity2)
dr2=dep_rate(et2)
tfinal2=tt(dr2,Mois2)
Mois1=recalc(Mois2,dr2,t2)


ra3=calculate_ra(J)
et3=calculate_et(Tmin,Tmax,ra3,humidity3)
dr3=dep_rate(et3)
tfinal3=tt(dr3,Mois3)
Mois3=recalc(Mois3,dr3,t3)


#WRITING INTO ROOT NODE
channel_id = "3045528"
write_api_key = "NWMLJPCEIE93YXBV" # Replace with your Write API Key

# URL for updating a channel. Using POST is recommended for multi-field updates.
url = f"https://api.thingspeak.com/update.json"

# --- Data to be Sent ---
# Create a dictionary to hold the data for the fields you want to update.
# The keys must be 'field3', 'field4', 'field5', etc.
payload = {
    'api_key': "NWMLJPCEIE93YXBV",
    'Moisture': Mois1,
    'Time': time1,
    'Depletion Rate': dr1
}

try:
    # Make the HTTP POST request
    response = requests.post(url, data=payload)
    response.raise_for_status() # Raise an exception for bad status codes

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")


#WRITING INTO NODE 1
channel_id = "3045635"
write_api_key = "JKQBSZ5YJ862N7UH" # Replace with your Write API Key

# URL for updating a channel. Using POST is recommended for multi-field updates.
url = f"https://api.thingspeak.com/update.json"

# --- Data to be Sent ---
# Create a dictionary to hold the data for the fields you want to update.
# The keys must be 'field3', 'field4', 'field5', etc.
payload = {
    'api_key': "JKQBSZ5YJ862N7UH",
    'Moisture': Mois2,
    'Time': time2,
    'Depletion Rate': dr2
}

try:
    # Make the HTTP POST request
    response = requests.post(url, data=payload)
    response.raise_for_status() # Raise an exception for bad status codes

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")


#WRITING INTO NODE 2
channel_id = "3045636"
write_api_key = "JKQBSZ5YJ862N7UH" # Replace with your Write API Key

# URL for updating a channel. Using POST is recommended for multi-field updates.
url = f"https://api.thingspeak.com/update.json"

# --- Data to be Sent ---
# Create a dictionary to hold the data for the fields you want to update.
# The keys must be 'field3', 'field4', 'field5', etc.
payload = {
    'api_key': "JKQBSZ5YJ862N7UH",
    'Mositure': Mois3,
    'Time': time3,
    'Depletion Rate': dr3
}

try:
    # Make the HTTP POST request
    response = requests.post(url, data=payload)
    response.raise_for_status() # Raise an exception for bad status codes

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")

USER_DB = "users.json"


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


        menu = st.sidebar.selectbox("Menu", ["Login", "Register","Dashboard"])
        with col2:

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


        if menu == "Dashboard":
                if st.session_state.get("logged_in", False):
                    st.header(f"Hello, {st.session_state['username']}!")
                    st.subheader("Trees in your neighbourhood")

                    sensors = {
                        "Greeno": [(12.96947962281231, 79.15840797707915), 80, "Tuesday, 12:45pm"],
                        "Tank": [(12.970008248014226, 79.15841899890708), 60, "Sunday, 12:45pm"],
                        "Wood": [(12.96986963409287, 79.1589965417121), 20, "Monday, 12:45pm"]
                    }

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



