import random
import json
import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

# Define MQTT broker host and port
broker_host = "34.123.176.43"
broker_port = 1883

# Define MQTT topic
mqtt_topic = "sensor_mqtt"

# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_publish(client, userdata, mid):
    print("Message published")

# Create MQTT client instance
client = mqtt.Client()

# Set up callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to MQTT broker
client.connect(broker_host, broker_port)

# Start background thread for MQTT client
client.loop_start()

# Starting timestamp
timestamp = datetime.now()

# Continuously send data
try:
    while True:
        # Construct data payload
        data = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "longitude": 139.6917,
            "latitude": 35.6895,
            "temperature": 0,
            "humidity": random.randint(0, 100),
            "pressure": 0,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Convert the data payload to JSON string
        json_data = json.dumps(data).encode('ascii')

        # Publish the data to the specified MQTT topic
        client.publish(mqtt_topic, json_data)

        print(f"Data sent to MQTT topic {mqtt_topic}:", data)

        # Increment timestamp by 2 seconds for the next data point
        timestamp += timedelta(seconds=2)

        # Wait for 2 seconds before sending the next data point
        time.sleep(2)
except KeyboardInterrupt:
    print("Disconnecting from MQTT broker")
    client.disconnect()
    client.loop_stop()
