import random
import requests
import json
from datetime import datetime, timedelta
import time

# URL of your backend endpoint
url = "http://localhost:8000/receive-data"

# Starting timestamp
timestamp = datetime.now()

# Continuously send data
while True:
    try:
        # Construct data payload
        data = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "longitude": 6.0002,
            "latitude": 7.0002,
            "temperature": 0,
            "humidity": random.randint(0, 100),
            "pressure": 0
        }

        # Send data as a POST request
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Data sent successfully:", data)
        else:
            print("Failed to send data:", data)

        # Increment timestamp by 2 seconds for the next data point
        timestamp += timedelta(seconds=2)

        # Wait for 2 seconds before sending the next data point
        time.sleep(2)
    except Exception as e:
        print("Error occurred while sending data:", e)
