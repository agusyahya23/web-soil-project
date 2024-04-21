import paho.mqtt.client as mqtt
import json
import random
import time
import concurrent.futures

# Define MQTT broker host and port
broker_host = "34.123.176.43"
broker_port = 1883

# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")  
    else:
        print(f"Failed to connect, return code {rc}")

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

# Configuration for the 5 specific sensors
specific_sensors = [
    {"latitude": 37.7749, "longitude": -122.4194, "timestamp": time.time()},
    {"latitude": 34.0522, "longitude": -118.2437, "timestamp": time.time()},
    {"latitude": 40.7128, "longitude": -74.0060, "timestamp": time.time()},
    {"latitude": 51.5074, "longitude": -0.1278, "timestamp": time.time()},
    {"latitude": 35.6895, "longitude": 139.6917, "timestamp": time.time()}
]

# Generate fixed random latitude and longitude for the 45 random sensors
random_sensors_config = []
for sensor_id in range(6, 51):
    random_latitude = round(random.uniform(-90, 90), 6)
    random_longitude = round(random.uniform(-180, 180), 6)
    # Initialize timestamp to current time
    timestamp = time.time()
    random_sensors_config.append({
        "sensor_id": sensor_id, 
        "latitude": random_latitude, 
        "longitude": random_longitude, 
        "timestamp": timestamp,
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S", time.time())
        })

# Function to generate data for a sensor
def generate_sensor_data(sensor_config):
    # Increment timestamp
    sensor_config["timestamp"] += 1  # Increase timestamp by 1 second (you can adjust the increment as needed)

    temperature = round(random.uniform(-20, 40), 2)
    humidity = round(random.uniform(0, 100), 2)
    pressure = round(random.uniform(900, 1100), 2)

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sensor_config["timestamp"])),
        "latitude": sensor_config["latitude"],
        "longitude": sensor_config["longitude"],
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S", time.time())
    }

    return data

# Function to continuously publish data from a sensor
def publish_sensor_data(sensor_config):
    while True:
        data = generate_sensor_data(sensor_config)
        json_string = json.dumps(data).encode('ascii')
        client.publish("sensor_mqtt", json_string)
        time.sleep(1)  # Adjust sleep time as needed for the desired publishing rate

# Create a thread pool executor for concurrent publishing
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks for the 5 specific sensors
    for sensor_config in specific_sensors:
        executor.submit(publish_sensor_data, sensor_config)
        
    # Submit tasks for the 45 random sensors
    for sensor_config in random_sensors_config:
        executor.submit(publish_sensor_data, sensor_config)

# The program will keep running until manually stopped.
