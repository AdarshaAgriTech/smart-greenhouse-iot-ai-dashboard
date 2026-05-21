import paho.mqtt.client as mqtt

broker = "localhost"

# Actuator states
fan_on = False
fogger_on = False
nutrient_on = False
acid_on = False

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Function to publish actuator status
def publish_status(topic, state):
    client.publish(topic, state)

def on_message(client, userdata, msg):

    global fan_on
    global fogger_on
    global nutrient_on
    global acid_on

    topic = msg.topic
    value = msg.payload.decode()

    print(f"{topic} --> {value}")

    # =========================
    # TEMPERATURE CONTROL
    # =========================
    if topic == "greenhouse/temp":

        temp = float(value)

        # Fan ON
        if temp > 30 and not fan_on:
            fan_on = True

            print("🌡️ High Temperature → Fan-Pad ON")

            publish_status("greenhouse/fan_status", "ON")

        # Fan OFF
        elif temp < 28 and fan_on:
            fan_on = False

            print("✅ Temperature Normal → Fan-Pad OFF")

            publish_status("greenhouse/fan_status", "OFF")

    # =========================
    # HUMIDITY CONTROL
    # =========================
    elif topic == "greenhouse/rh":

        rh = float(value)

        # Fogger ON
        if rh < 60 and not fogger_on:
            fogger_on = True

            print("💧 Low Humidity → Fogger ON")

            publish_status("greenhouse/fogger_status", "ON")

        # Fogger OFF
        elif rh > 65 and fogger_on:
            fogger_on = False

            print("✅ Humidity Normal → Fogger OFF")

            publish_status("greenhouse/fogger_status", "OFF")

    # =========================
    # EC CONTROL
    # =========================
    elif topic == "greenhouse/ec":

        ec = float(value)

        # Nutrient ON
        if ec < 1.5 and not nutrient_on:
            nutrient_on = True

            print("🧪 Low EC → Nutrient Dosing ON")

            publish_status("greenhouse/nutrient_status", "ON")

        # Nutrient OFF
        elif ec > 1.8 and nutrient_on:
            nutrient_on = False

            print("✅ EC Normal → Nutrient Dosing OFF")

            publish_status("greenhouse/nutrient_status", "OFF")

    # =========================
    # pH CONTROL
    # =========================
    elif topic == "greenhouse/ph":

        ph = float(value)

        # Acid ON
        if ph > 6.5 and not acid_on:
            acid_on = True

            print("⚗️ High pH → Acid Dosing ON")

            publish_status("greenhouse/acid_status", "ON")

        # Acid OFF
        elif ph < 6.2 and acid_on:
            acid_on = False

            print("✅ pH Normal → Acid Dosing OFF")

            publish_status("greenhouse/acid_status", "OFF")

# Attach callback
client.on_message = on_message

# Connect to broker
client.connect(broker, 1883, 60)

# Subscribe to all greenhouse topics
client.subscribe("greenhouse/#")

print("🟢 Intelligent Greenhouse Controller Running...\n")

# Keep system running
client.loop_forever()