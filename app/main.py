from fastapi import FastAPI, Request
from datetime import datetime
from app.utils import get_nearest_hour, get_today_info

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Iterator, List

import pickle
import os
import asyncio
import logging
import random
import sys
import json
import csv
from datetime import datetime

LOG_FILE_1 = "log_sensor_1.csv"
LOG_FILE_2 = "log_sensor_2.csv"

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
random.seed()  
app.mount("/static", StaticFiles(directory="app/static"), name="static")

data_store: List[dict] = []
data_store2: List[dict] = []
MAX_DATA_POINTS = 1

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {'request':request})


@app.get("/moisture", response_class=HTMLResponse)
async def moisture_view(request: Request):
    return templates.TemplateResponse("index_moisture.html", {'request': request})


@app.get("/suction", response_class=HTMLResponse)
async def suction_(request: Request):
    return templates.TemplateResponse("index_suction.html", {'request': request})


@app.get("/plot", response_class=HTMLResponse)
async def suction_(request: Request):
    return templates.TemplateResponse("index_plot.html", {'request': request})


@app.post("/predict/moisture/{latitude}/{longitude}")
async def predict_moisture(latitude: str, longitude: str):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    target_hour  = get_nearest_hour(current_time)
    
    api_dict, feature_cols = get_today_info(latitude=latitude, longitude=longitude)
    index = api_dict['timestamp'].index(target_hour)

    features_data = {}
    features_data['longitude'] = longitude
    features_data['latitude']  = latitude

    features = [longitude, latitude]
    for col in feature_cols:
        features_data[col] = api_dict[col][index]
        features.append(features_data[col])

    with open('app/moisture_model.pkl', 'rb') as f:
        model = pickle.load(f)
        features_data['predicted_moisture'] = model.predict([features])[0]
    
    return features_data


@app.post("/predict/suction/{latitude}/{longitude}")
async def predict_suction(latitude: str, longitude: str):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    target_hour  = get_nearest_hour(current_time)
    
    api_dict, feature_cols = get_today_info(latitude=latitude, longitude=longitude)
    index = api_dict['timestamp'].index(target_hour)

    features_data = {}
    features_data['longitude'] = longitude
    features_data['latitude']  = latitude

    features = [longitude, latitude]
    for col in feature_cols:
        features_data[col] = api_dict[col][index]
        features.append(features_data[col])

    with open('app/suction_model.pkl', 'rb') as f:
        model = pickle.load(f)
        features_data['predicted_suction'] = model.predict([features])[0]
    
    return features_data

async def generate_random_data(request: Request) -> Iterator[str]:
    """
    Generates random value between 0 and 100

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    client_ip = request.client.host

    logger.info("Client %s connected", client_ip)

    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%Y%m%d%H%M"),
                "value": random.random() * 100,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(2)


@app.get("/chart-data")
async def chart_data(request: Request) -> StreamingResponse:
    response = StreamingResponse(generate_client_data(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

@app.post("/receive-data")
async def receive_data(data: dict):
    """
    Receive data sent via POST request and store it.
    """
    # Add the new data point to the beginning of the list
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    if latitude == 35.6895 and longitude == 139.6917:
        data_store.insert(0, data)
        logger.info("Received data: %s", data)
        send_time = data.get("current_time")

        received_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate latency
        latency = (datetime.strptime(received_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")).total_seconds()
        sensor = "sensor 1"
        # Log data to CSV file
        with open(LOG_FILE_1, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([sensor, latitude, longitude, send_time, received_time, latency])

    elif latitude == 37.7749 and longitude == -122.4194:
        data_store2.insert(0, data)
        logger.info("Received data: %s", data)
        send_time = data.get("current_time")

        received_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate latency
        latency = (datetime.strptime(received_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")).total_seconds()
        sensor = "sensor 1"
        # Log data to CSV file
        with open(LOG_FILE_2, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([sensor, latitude, longitude, send_time, received_time, latency])
    
    # Ensure that data_store does not exceed the maximum number of data points
    if len(data_store) > MAX_DATA_POINTS:
        data_store.pop()  # Remove the oldest data point from the end of the list
    
    if len(data_store2) > MAX_DATA_POINTS:
        data_store2.pop()  # Re
    
    return {"message": "Data received successfully"}

async def generate_client_data() -> Iterator[str]:
    """
    Generates data stored in the data_store list.
    """
    while True:
        try:
            data = data_store[0]  # Get the oldest data point from the list
            timestamp = data.get("timestamp")
            humidity = data.get("humidity")
            yield f"data:{{\"time\": \"{timestamp}\", \"value\": {humidity}}}\n\n"
            # If no data in data_store, wait for a short time before checking again
            await asyncio.sleep(2)
        except Exception as e:
            logger.error("Error processing data: %s", e)
            break

# async def generate_client_data(request: Request) -> Iterator[str]:
#     """
#     Generates random value between 0 and 100

#     :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
#     """
#     client_ip = request.client.host

#     logger.info("Client %s connected", client_ip)

#     while True:
#         try:
#             data = await request.stream.receive()
#             if not data:
#                 break
#             data = data.decode()
#             json_data = json.loads(data)
#             timestamp = json_data.get("timestamp")
#             humidity = json_data.get("humidity")
#             json_data = json.dumps(
#             {
#                 "time": timestamp,
#                 "value": humidity,
#             }
#             )
#             print(json_data)
          
#             yield f"data:{json_data}\n\n"
#             await asyncio.sleep(2)
#         except:
#             logger.error("Error receiving data from client %s", client_ip)
#             break

