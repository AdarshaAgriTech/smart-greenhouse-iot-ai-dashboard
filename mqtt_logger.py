import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect("greenhouse_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS greenhouse_data (

    timestamp TEXT,
    temperature REAL,
    humidity REAL,
    ec REAL,
    ph REAL,
    fan_status TEXT,
    fogger_status TEXT,
    nutrient_status TEXT,
    acid_status TEXT
)
""")

conn.commit()

# =========================
# DATA STORAGE
# =========================

data = {
    "temperature": None,
    "humidity": None,
    "ec": None,
    "ph": None,
    "fan_status": "OFF",
    "fogger_status": "OFF",
    "nutrient_status": "OFF",
    "acid_status": "OFF"
}

# =========================
# MQTT CALLBACK
# =========================

def on_message(client, userdata, msg):

    topic = msg.topic
    value = msg.payload.decode()

    # =========================
    # SENSOR DATA
    # =========================

    if topic == "greenhouse/temp":
        data["temperature"] = float(value)

    elif topic == "greenhouse/rh":
        data["humidity"] = float(value)

    elif topic == "greenhouse/ec":
        data["ec"] = float(value)

    elif topic == "greenhouse/ph":
        data["ph"] = float(value)

    # =========================
    # ACTUATOR DATA
    # =========================

    elif topic == "greenhouse/fan_status":
        data["fan_status"] = value

    elif topic == "greenhouse/fogger_status":
        data["fogger_status"] = value

    elif topic == "greenhouse/nutrient_status":
        data["nutrient_status"] = value

    elif topic == "greenhouse/acid_status":
        data["acid_status"] = value

    # =========================
    # INSERT ONLY AFTER FULL SENSOR CYCLE
    # =========================

    if topic == "greenhouse/ph":

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO greenhouse_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            data["temperature"],
            data["humidity"],
            data["ec"],
            data["ph"],
            data["fan_status"],
            data["fogger_status"],
            data["nutrient_status"],
            data["acid_status"]
        ))

        conn.commit()

        print(f"Logged at {timestamp}")

# =========================
# MQTT SETUP
# =========================

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_message = on_message

client.connect("localhost", 1883, 60)

client.subscribe("greenhouse/#")

print("MQTT Logger Running...")

client.loop_forever()