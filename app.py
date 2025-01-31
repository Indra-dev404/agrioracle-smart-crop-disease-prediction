from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

app = Flask(__name__)

# Load the trained model and label encoders
rf_model = joblib.load('rf_model.pkl')
label_encoders = joblib.load('label_encoders.pkl')
target_encoder = joblib.load('target_encoder.pkl')

# Function to get the device's location based on IP address
def get_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = data['loc'].split(',')
        latitude, longitude = float(location[0]), float(location[1])
        return latitude, longitude
    except Exception as e:
        print(f"Error getting location: {e}")
        return None, None

# Function to fetch weather data from OpenMeteo API
def fetch_weather_data(latitude, longitude):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relativehumidity_2m,precipitation&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        response = requests.get(url)
        data = response.json()
        hourly_data = data.get('hourly', {})
        daily_data = data.get('daily', {})
        max_temp = daily_data.get('temperature_2m_max', [None])[0]
        min_temp = daily_data.get('temperature_2m_min', [None])[0]
        rh1 = hourly_data.get('relativehumidity_2m', [None])[0]
        rainfall = hourly_data.get('precipitation', [None])[0]
        return {
            'Maximum Temperature': max_temp,
            'Minimum Temperature': min_temp,
            'RH1': rh1,
            'Rainfall': rainfall
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

# Function to predict pest based on input parameters
def predict_pest(input_data):
    try:
        # Convert categorical columns using label encoders
        for col in ['Crop Name', 'Standard Week']:
            input_data[col] = label_encoders[col].transform([input_data[col]])[0]
        # Prepare the input data for prediction
        input_df = pd.DataFrame([input_data])
        prediction = rf_model.predict(input_df)
        predicted_pest = target_encoder.inverse_transform(prediction)[0]
        return predicted_pest
    except Exception as e:
        print(f"Error predicting pest: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/function')
def function():
    return render_template('function.html')

@app.route('/automated', methods=['POST'])
def automated():
    latitude, longitude = get_location()
    if latitude and longitude:
        weather_data = fetch_weather_data(latitude, longitude)
        if weather_data:
            return jsonify(weather_data)
    return jsonify({'error': 'Failed to fetch weather data'})

@app.route('/semi-automated', methods=['POST'])
def semi_automated():
    data = request.json
    temperature = data.get('temperature')
    rh = data.get('rh')
    latitude, longitude = get_location()
    if latitude and longitude:
        weather_data = fetch_weather_data(latitude, longitude)
        if weather_data:
            weather_data['Temperature'] = temperature
            weather_data['RH'] = rh
            return jsonify(weather_data)
    return jsonify({'error': 'Failed to fetch weather data'})

@app.route('/manual', methods=['POST'])
def manual():
    data = request.json
    crop_name = data.get('crop_name')
    standard_week = data.get('standard_week')
    max_temp = data.get('max_temp')
    min_temp = data.get('min_temp')
    rh1 = data.get('rh1')
    rh2 = data.get('rh2')
    rainfall = data.get('rainfall')
    input_data = {
        'Crop Name': crop_name,
        'Standard Week': standard_week,
        'MaxT(°C)': max_temp,
        'MinT(°C)': min_temp,
        'RH1(%)': rh1,
        'RH2(%)': rh2,
        'RF(mm)': rainfall
    }
    predicted_pest = predict_pest(input_data)
    if predicted_pest:
        return jsonify({'predicted_pest': predicted_pest})
    return jsonify({'error': 'Failed to predict pest'})

if __name__ == "__main__":
    app.run(debug=True)