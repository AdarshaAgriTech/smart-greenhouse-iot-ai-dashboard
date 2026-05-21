import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import time
import base64
import plotly.express as px
import itertools
import sqlite3
import joblib

from collections import deque
from datetime import datetime

# =====================================
# DATABASE CONNECTION
# =====================================

conn = sqlite3.connect(
    "greenhouse_data.db",
    check_same_thread=False
)

# =====================================
# LOAD ML MODEL
# =====================================

rh_model = joblib.load(
    "humidity_prediction_model.pkl"
)

# =====================================
# LOAD LOCAL BACKGROUND IMAGE
# =====================================

def get_base64(bin_file):

    with open(bin_file, "rb") as f:

        data = f.read()

    return base64.b64encode(data).decode()

bg_image = get_base64("greenhouse_bg.jpg")

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Smart Greenhouse Dashboard",
    page_icon="🌱",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown(f"""
<style>

.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

header {{
    background-color: rgba(0,0,0,0) !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

html, body, [class*="css"] {{
    color: white !important;
}}

.block-container {{

    padding-top: 0.2rem;
    padding-bottom: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;

    background-color: rgba(0,0,0,0.55);

    border-radius: 12px;
}}

.stMetric {{

    background-color: rgba(30,30,30,0.88);

    padding: 0px;
    
    min-height: 60px;

    border-radius: 12px;

    border: 1px solid #333333;

    box-shadow: 0px 0px 8px rgba(0,255,100,0.2);
}}

[data-testid="stMetricLabel"] {{

    color: white !important;

    font-size: 18px;

    font-weight: bold;
}}

[data-testid="stMetricValue"] {{

    color: white !important;

    font-size: 34px;

    font-weight: bold;
}}

h1, h2, h3 {{

    color: #7CFC00 !important;
}}

section[data-testid="stSidebar"] {{

    background-color: rgba(22,27,34,0.96);
}}

.alert-box {{

    background-color: rgba(42,42,42,0.92);

    padding: 10px;

    border-radius: 10px;

    margin-bottom: 2px;

    font-size: 18px;

    font-weight: bold;

    color: white;

    border-left: 5px solid #7CFC00;
}}

.chart-card {{

    background-color: rgba(30,30,30,0.88);

    padding: 12px;

    border-radius: 14px;

    border: 1px solid #333333;

    box-shadow: 0px 0px 8px rgba(0,255,100,0.2);

    margin-bottom: 10px;
}}
div[data-testid="stHorizontalBlock"] {{

    gap: 0.5rem !important;

}}

div[data-testid="stVerticalBlock"] {{

    gap: 0.6rem !important;

}}

div[data-testid="column"] {{

    padding: 0rem !important;

}}

</style>
""", unsafe_allow_html=True)

# =====================================
# DATA STORAGE
# =====================================

data = {

    "temp": 0,
    "rh": 0,
    "ec": 0,
    "ph": 0,
    "fan": "OFF",
    "fogger": "OFF"
}

# =====================================
# ALERT STORAGE
# =====================================

alerts = deque(maxlen=10)

chart_counter = itertools.count()

# =====================================
# ALERT FUNCTION
# =====================================

def add_alert(message):

    current_time = datetime.now().strftime("%H:%M:%S")

    alerts.appendleft(
        f"{current_time} → {message}"
    )

# =====================================
# MQTT CALLBACK
# =====================================

def on_message(client, userdata, msg):

    topic = msg.topic

    value = msg.payload.decode()

    if topic == "greenhouse/temp":

        temp = float(value)

        data["temp"] = temp

        if temp > 35:
            add_alert("🔥 Critical Temperature")

        elif temp > 30:
            add_alert("🌡️ High Temperature")

    elif topic == "greenhouse/rh":

        rh = float(value)

        data["rh"] = rh

        if rh < 55:
            add_alert("💧 Low Humidity")

    elif topic == "greenhouse/ec":

        data["ec"] = float(value)

    elif topic == "greenhouse/ph":

        ph = float(value)

        data["ph"] = ph

        if ph > 6.5:
            add_alert("⚗️ High pH")

    elif topic == "greenhouse/fan_status":

        data["fan"] = value

    elif topic == "greenhouse/fogger_status":

        data["fogger"] = value

# =====================================
# MQTT SETUP
# =====================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_message = on_message

client.connect("localhost", 1883, 60)

client.subscribe("greenhouse/#")

client.loop_start()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("⚙️ System Status")

st.sidebar.success("MQTT Broker Connected")

st.sidebar.info("Intelligent Controller Active")

st.sidebar.write("---")

st.sidebar.subheader("🚨 Alerts")

alert_placeholder = st.sidebar.empty()

# =====================================
# TITLE
# =====================================

st.markdown("""
<div style="
background-color: rgba(0,0,0,0.65);
padding:12px;
border-radius:14px;
text-align:center;
margin-bottom:12px;
border:1px solid #333333;
box-shadow:0px 0px 10px rgba(0,255,100,0.25);
">

<h1 style="
color:#7CFC00;
margin:0;
font-size:48px;
font-weight:800;
">
🌱 Smart Greenhouse IoT Dashboard
</h1>

</div>
""", unsafe_allow_html=True)
main_placeholder = st.empty()

# =====================================
# DASHBOARD LOOP
# =====================================

while True:

    with main_placeholder.container():
        # =====================================
        # LIVE SENSOR DATA
        # =====================================

        col1, col2, col3, col4 = st.columns(4)

        cards = [

            ("🌡️ Temperature", f"{data['temp']} °C"),

            ("💧 Humidity", f"{data['rh']} %"),

            ("🧪 EC", f"{data['ec']}"),

            ("⚗️ pH", f"{data['ph']}")
        ]

        for col, (title, value) in zip(
            [col1, col2, col3, col4],
            cards
        ):

            col.markdown(f"""
            <div style="
            background-color: rgba(30,30,30,0.88);
            padding:8px;
            border-radius:12px;
            border:1px solid #333333;
            height:58px;
            margin-bottom:8px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            ">

            <div style="
            font-size:15px;
            color:white;
            font-weight:bold;
            ">
            {title}
            </div>

            <div style="
            font-size:28px;
            color:white;
            font-weight:bold;
            ">
            {value}
            </div>

            </div>
            """, unsafe_allow_html=True)

                        # =====================================
        # ACTUATOR STATUS
        # =====================================

        act1, act2 = st.columns(2)

        fan_color = (
            "#00FF7F"
            if data["fan"] == "ON"
            else "#FF3B30"
        )

        fogger_color = (
            "#00FF7F"
            if data["fogger"] == "ON"
            else "#FF3B30"
        )

        fan_status = data["fan"]

        fogger_status = data["fogger"]

        # FAN CARD

        act1.markdown(f"""
<div style="
background-color: rgba(30,30,30,0.88);
padding:10px;
border-radius:12px;
display:flex;
justify-content:space-between;
align-items:center;
height:55px;
border:1px solid #333333;
margin-bottom:8px;
">

<div style="
font-size:18px;
font-weight:bold;
color:white;
">
🌀 Fan-Pad
</div>

<div style="
display:flex;
align-items:center;
gap:10px;
">

<div style="
width:18px;
height:18px;
border-radius:50%;
background:{fan_color};
">
</div>

<div style="
font-size:22px;
font-weight:bold;
color:white;
">
{fan_status}
</div>

</div>

</div>
""", unsafe_allow_html=True)

        # FOGGER CARD

        act2.markdown(f"""
<div style="
background-color: rgba(30,30,30,0.88);
padding:10px;
border-radius:12px;
display:flex;
justify-content:space-between;
align-items:center;
height:55px;
border:1px solid #333333;
margin-bottom:8px;
">

<div style="
font-size:18px;
font-weight:bold;
color:white;
">
🌫️ Fogger
</div>

<div style="
display:flex;
align-items:center;
gap:10px;
">

<div style="
width:18px;
height:18px;
border-radius:50%;
background:{fogger_color};
">
</div>

<div style="
font-size:22px;
font-weight:bold;
color:white;
">
{fogger_status}
</div>

</div>

</div>
""", unsafe_allow_html=True)
        # =====================================
        # ALERTS
        # =====================================

        with alert_placeholder.container():

            for alert in list(alerts):

                st.markdown(
                    f'<div class="alert-box">{alert}</div>',
                    unsafe_allow_html=True
                )

        # =====================================
        # DATABASE QUERIES
        # =====================================

        recent_query = """
        SELECT * FROM greenhouse_data
        ORDER BY timestamp DESC
        LIMIT 100
        """

        recent_df = pd.read_sql_query(
            recent_query,
            conn
        )

        full_query = """
        SELECT * FROM greenhouse_data
        """

        full_df = pd.read_sql_query(
            full_query,
            conn
        )

                       # =====================================
        # ANALYTICS
        # =====================================

        if not full_df.empty:

            avg_temp = round(
                full_df["temperature"].mean(),
                2
            )

            avg_rh = round(
                full_df["humidity"].mean(),
                2
            )

            fan_on_count = (
                (
                    full_df["fan_status"] == "ON"
                ) &
                (
                    full_df["fan_status"].shift(1)
                    != "ON"
                )
            ).sum()

            fogger_on_count = (
                (
                    full_df["fogger_status"] == "ON"
                ) &
                (
                    full_df["fogger_status"].shift(1)
                    != "ON"
                )
            ).sum()

            # =====================================
            # AVG CARDS
            # =====================================

            row1_col1, row1_col2 = st.columns(2)

            analytics_row1 = [

                ("📊 Avg Temperature", f"{avg_temp} °C"),

                ("📊 Avg Humidity", f"{avg_rh} %")
            ]

            for col, (title, value) in zip(
                [row1_col1, row1_col2],
                analytics_row1
            ):

                col.markdown(f"""
                <div style="
                background-color: rgba(30,30,30,0.88);
                padding:6px 10px;
                border-radius:10px;
                border:1px solid #333333;
                margin-bottom:8px;
                height:58px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                ">

                <div style="
                font-size:15px;
                font-weight:bold;
                color:white;
                ">
                {title}
                </div>

                <div style="
                font-size:24px;
                font-weight:bold;
                color:white;
                ">
                {value}
                </div>

                </div>
                """, unsafe_allow_html=True)

            # =====================================
            # ACTUATOR COUNT CARDS
            # =====================================

            row2_col1, row2_col2 = st.columns(2)

            analytics_row2 = [

                ("🌀 Fan ON Count", fan_on_count),

                ("🌫️ Fogger ON Count", fogger_on_count)
            ]

            for col, (title, value) in zip(
                [row2_col1, row2_col2],
                analytics_row2
            ):

                col.markdown(f"""
                <div style="
                background-color: rgba(30,30,30,0.88);
                padding:6px 10px;
                border-radius:10px;
                border:1px solid #333333;
                margin-bottom:8px;
                height:58px;
                margin-bottom:8px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                ">

                <div style="
                font-size:15px;
                font-weight:bold;
                color:white;
                ">
                {title}
                </div>

                <div style="
                font-size:24px;
                font-weight:bold;
                color:white;
                ">
                {value}
                </div>

                </div>
                """, unsafe_allow_html=True)

                        # =====================================
            # RH PREDICTION CARD
            # =====================================

            if len(full_df) >= 3:

                latest_row = full_df.iloc[-1]

                prediction_input = pd.DataFrame([{

                    "hour":
                        pd.to_datetime(
                            latest_row["timestamp"]
                        ).hour,

                    "temp_lag_1":
                        latest_row["temperature"],

                    "rh_lag_1":
                        latest_row["humidity"],

                    "temp_rolling_mean":
                        full_df["temperature"]
                        .tail(3)
                        .mean(),

                    "rh_rolling_mean":
                        full_df["humidity"]
                        .tail(3)
                        .mean()
                }])

                predicted_rh = rh_model.predict(
                    prediction_input
                )[0]

                st.markdown(f"""
                <div style="
                background-color: rgba(30,30,30,0.88);
                padding:6px 10px;
                border-radius:10px;
                border:1px solid #333333;
                margin-bottom:8px;
                height:58px;
                display:flex;
                justify-content:space-between;
                align-items:center;
                ">

                <div style="
                font-size:15px;
                font-weight:bold;
                color:white;
                ">
                🔮 Predicted Next Hour RH
                </div>

                <div style="
                font-size:24px;
                font-weight:bold;
                color:white;
                ">
                {round(predicted_rh,2)} %
                </div>

                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    "<div style='margin-top:12px'></div>",
                    unsafe_allow_html=True
                )
        # =====================================
        # CHARTS
        # =====================================

        chart_col1, chart_col2 = st.columns(2)

        # TEMPERATURE CHART

        with chart_col1:


            if not recent_df.empty:

                temp_df = recent_df.copy()

                temp_df = temp_df.sort_values(
                    "timestamp"
                )

                temp_df["Time"] = pd.to_datetime(
                    temp_df["timestamp"]
                )

                fig_temp = px.line(

                    temp_df,

                    x="Time",

                   y="temperature",
                   labels={
                   "temperature": "Temperature (°C)"
                   },

                    title="Temperature Trend"
                )

                fig_temp.update_layout(
               
                    template="plotly_dark",
                    height=220,
                    margin=dict(l=55, r=20, t=40, b=40)
                )

                st.plotly_chart(
                    fig_temp,
                    use_container_width=True,
                    key=f"temp_{next(chart_counter)}"
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        # HUMIDITY CHART

        with chart_col2:

            if not recent_df.empty:

                rh_df = recent_df.copy()

                rh_df = rh_df.sort_values(
                    "timestamp"
                )

                rh_df["Time"] = pd.to_datetime(
                    rh_df["timestamp"]
                )

                fig_rh = px.line(

                    rh_df,

                    x="Time",

                   y="humidity",
                   labels={
                   "humidity": "Humidity (%)"
                   },

                    title="Humidity Trend"
                )

                fig_rh.update_layout(
                    template="plotly_dark",
                    height=220,
                    margin=dict(l=55, r=20, t=40, b=40)
                )

                st.plotly_chart(
                    fig_rh,
                    use_container_width=True,
                    key=f"rh_{next(chart_counter)}"
                )


        st.caption(
            "MQTT + SQLite + AI Prediction + Streamlit"
        )

    time.sleep(1)