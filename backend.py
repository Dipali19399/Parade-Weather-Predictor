import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import requests
from datetime import datetime, timedelta
import warnings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

warnings.filterwarnings('ignore')
raindata="weather_prediction/test/RF_NE_1901-2021.csv"
tempdata="weather_prediction/test/TEMP_ANNUAL_SEASONAL_MEAN.csv"
class WeatherPredictor:
    def __init__(self):
        # Load historical data
        self.rainfall_df = pd.read_csv(raindata)
        self.temperature_df = pd.read_csv(tempdata)
        
        # API endpoints
        self.elevation_api = "https://api.open-elevation.com/api/v1/lookup"
        
        # Current year
        self.current_year = 2025
        
        # Create and prepare data
        self.create_daily_dataset()
        self.prepare_features()
        self.train_models()
        
        # Date validation limits
        self.today = datetime.now().date()
        self.max_future_date = self.today + timedelta(days=180)  # 6 months
    
    def create_daily_dataset(self):
        """Create synthetic daily data from seasonal data"""
        print("Loading and processing historical weather data...")
        
        daily_data = []
        
        for year in range(1901, self.current_year + 1):
            # Get yearly data
            temp_data = self.temperature_df[self.temperature_df['YEAR'] == year]
            rain_data = self.rainfall_df[self.rainfall_df['YEAR'] == year]
            
            if temp_data.empty or rain_data.empty:
                # Use average values if data missing
                recent_temp = self.temperature_df.tail(5).mean()
                recent_rain = self.rainfall_df.tail(5).mean()
                
                jan_feb_temp = recent_temp.get('JAN-FEB', 20)
                mar_may_temp = recent_temp.get('MAR-MAY', 25)
                jun_sep_temp = recent_temp.get('JUN-SEP', 28)
                oct_dec_temp = recent_temp.get('OCT-DEC', 22)
                annual_temp = recent_temp.get('ANNUAL', 25)
                
                jun_rain = recent_rain.get('JUN', 300)
                jul_rain = recent_rain.get('JUL', 300)
                aug_rain = recent_rain.get('AUG', 300)
                sep_rain = recent_rain.get('SEP', 300)
            else:
                # Extract seasonal values from actual data
                jan_feb_temp = temp_data['JAN-FEB'].values[0]
                mar_may_temp = temp_data['MAR-MAY'].values[0]
                jun_sep_temp = temp_data['JUN-SEP'].values[0]
                oct_dec_temp = temp_data['OCT-DEC'].values[0]
                annual_temp = temp_data['ANNUAL'].values[0]
                
                jun_rain = rain_data['JUN'].values[0]
                jul_rain = rain_data['JUL'].values[0]
                aug_rain = rain_data['AUG'].values[0]
                sep_rain = rain_data['SEP'].values[0]
            
            # Create daily data for the year
            for month in range(1, 13):
                # Calculate days in month
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    days_in_month = 31
                elif month == 2:
                    days_in_month = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
                else:
                    days_in_month = 30
                
                # Base temperature for the month
                if month in [1, 2]:
                    base_temp = jan_feb_temp
                elif month in [3, 4, 5]:
                    base_temp = mar_may_temp
                elif month in [6, 7, 8, 9]:
                    base_temp = jun_sep_temp
                else:
                    base_temp = oct_dec_temp
                
                # Base rainfall for the month
                if month == 6:
                    base_rain = jun_rain / 30
                elif month == 7:
                    base_rain = jul_rain / 31
                elif month == 8:
                    base_rain = aug_rain / 31
                elif month == 9:
                    base_rain = sep_rain / 30
                else:
                    base_rain = 0
                
                for day in range(1, days_in_month + 1):
                    # Create daily variations
                    daily_temp = base_temp + np.random.normal(0, 2)
                    
                    # Seasonal adjustment
                    if month in [12, 1, 2]:
                        daily_temp -= 3
                    elif month in [3, 4, 5]:
                        daily_temp += 1
                    elif month in [6, 7, 8, 9]:
                        daily_temp += 2
                    else:
                        daily_temp += 0.5
                    
                    # Rainfall with different intensities
                    if month in [6, 7, 8, 9]:
                        rain_prob = 60 + np.random.normal(0, 15)
                        if np.random.random() < rain_prob / 100:
                            # Vary rainfall intensity
                            rain_intensity = np.random.choice(['light', 'moderate', 'heavy'], 
                                                           p=[0.5, 0.3, 0.2])
                            if rain_intensity == 'light':
                                daily_rain = max(0, base_rain * np.random.lognormal(-1, 0.3))
                            elif rain_intensity == 'moderate':
                                daily_rain = max(0, base_rain * np.random.lognormal(0, 0.3))
                            else:  # heavy
                                daily_rain = max(0, base_rain * np.random.lognormal(1, 0.4))
                        else:
                            daily_rain = 0
                    else:
                        rain_prob = 10 + np.random.normal(0, 5)
                        daily_rain = 0 if np.random.random() > rain_prob / 100 else np.random.exponential(2)
                    
                    # Wind speed with variations for different conditions
                    if daily_rain > 0:
                        if daily_rain > 20:  # Heavy rain likely with storm
                            base_wind = 20 + np.random.normal(0, 5)
                        else:
                            base_wind = 12 + np.random.normal(0, 3)
                    elif month in [6, 7, 8, 9]:  # Monsoon
                        base_wind = 10 + np.random.normal(0, 2)
                    else:
                        base_wind = 8 + np.random.normal(0, 2)
                    
                    daily_wind = max(0, base_wind + np.random.normal(0, 2))
                    
                    # Determine day type for training
                    day_type = self.determine_day_type(daily_rain, daily_temp, daily_wind)
                    
                    daily_data.append({
                        'YEAR': int(year),
                        'MONTH': int(month),
                        'DAY': int(day),
                        'TEMPERATURE': float(daily_temp),
                        'RAINFALL': float(daily_rain),
                        'WIND_SPEED': float(daily_wind),
                        'HAS_RAIN': 1 if daily_rain > 0.1 else 0,
                        'ANNUAL_TEMP': float(annual_temp),
                        'DAY_TYPE': day_type
                    })
        
        self.daily_df = pd.DataFrame(daily_data)
        print(f"✅ Historical data loaded: {len(self.daily_df)} daily records")
    
    def determine_day_type(self, rainfall, temperature, wind_speed):
        """Determine the type of day based on weather parameters"""
        if rainfall > 20 and wind_speed > 25:
            return 'thunderstorm'
        elif rainfall > 10:
            return 'rainy'
        elif rainfall > 2:
            return 'cloudy_rainy'
        elif rainfall > 0.1:
            return 'cloudy'
        elif temperature > 35:
            return 'sunny_hot'
        elif temperature > 25:
            return 'sunny_warm'
        else:
            return 'sunny_cool'
    
    def prepare_features(self):
        """Prepare features for machine learning"""
        # Ensure correct data types
        self.daily_df['YEAR'] = self.daily_df['YEAR'].astype(int)
        self.daily_df['MONTH'] = self.daily_df['MONTH'].astype(int)
        self.daily_df['DAY'] = self.daily_df['DAY'].astype(int)
        
        # Date features
        def calculate_day_of_year(row):
            try:
                date_obj = datetime(int(row['YEAR']), int(row['MONTH']), int(row['DAY']))
                return date_obj.timetuple().tm_yday
            except:
                return (int(row['MONTH']) - 1) * 30 + int(row['DAY'])
        
        self.daily_df['DAY_OF_YEAR'] = self.daily_df.apply(calculate_day_of_year, axis=1)
        
        # Cyclical features
        self.daily_df['DAY_SIN'] = np.sin(2 * np.pi * self.daily_df['DAY_OF_YEAR'] / 365)
        self.daily_df['DAY_COS'] = np.cos(2 * np.pi * self.daily_df['DAY_OF_YEAR'] / 365)
        self.daily_df['MONTH_SIN'] = np.sin(2 * np.pi * self.daily_df['MONTH'] / 12)
        self.daily_df['MONTH_COS'] = np.cos(2 * np.pi * self.daily_df['MONTH'] / 12)
        
        # Lag features and rolling averages
        self.daily_df['TEMP_LAG1'] = self.daily_df['TEMPERATURE'].shift(1)
        self.daily_df['RAIN_LAG1'] = self.daily_df['RAINFALL'].shift(1)
        self.daily_df['WIND_LAG1'] = self.daily_df['WIND_SPEED'].shift(1)
        self.daily_df['TEMP_ROLL7'] = self.daily_df['TEMPERATURE'].rolling(7, min_periods=1).mean()
        self.daily_df['RAIN_ROLL7'] = self.daily_df['RAINFALL'].rolling(7, min_periods=1).mean()
        
        # Fill NaN values
        self.daily_df = self.daily_df.fillna(method='bfill').fillna(method='ffill')
        
        # Climate trend
        self.daily_df['YEAR_TREND'] = self.daily_df['YEAR'] - 1900
        
        print("✅ Feature engineering completed")
    
    def train_models(self):
        """Train machine learning models including day type classification"""
        feature_columns = [
            'YEAR', 'MONTH', 'DAY', 'DAY_OF_YEAR', 'YEAR_TREND',
            'DAY_SIN', 'DAY_COS', 'MONTH_SIN', 'MONTH_COS',
            'TEMP_LAG1', 'RAIN_LAG1', 'WIND_LAG1', 'TEMP_ROLL7', 'RAIN_ROLL7',
            'ANNUAL_TEMP'
        ]
        
        X = self.daily_df[feature_columns]
        y_temp = self.daily_df['TEMPERATURE']
        y_rain = self.daily_df['RAINFALL']
        y_rain_binary = self.daily_df['HAS_RAIN']
        y_wind = self.daily_df['WIND_SPEED']
        y_day_type = self.daily_df['DAY_TYPE']
        
        # Split data
        X_train, X_test, y_temp_train, y_temp_test = train_test_split(X, y_temp, test_size=0.2, random_state=42)
        _, _, y_rain_train, y_rain_test = train_test_split(X, y_rain, test_size=0.2, random_state=42)
        _, _, y_rain_binary_train, y_rain_binary_test = train_test_split(X, y_rain_binary, test_size=0.2, random_state=42)
        _, _, y_wind_train, y_wind_test = train_test_split(X, y_wind, test_size=0.2, random_state=42)
        _, _, y_day_type_train, y_day_type_test = train_test_split(X, y_day_type, test_size=0.2, random_state=42)
        
        # Train models
        self.temp_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
        self.temp_model.fit(X_train, y_temp_train)
        
        self.rain_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
        self.rain_model.fit(X_train, y_rain_train)
        
        self.rain_class_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
        self.rain_class_model.fit(X_train, y_rain_binary_train)
        
        self.wind_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
        self.wind_model.fit(X_train, y_wind_train)
        
        # Day type classification model
        self.day_type_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
        self.day_type_model.fit(X_train, y_day_type_train)
        
        # Evaluate day type model
        day_type_pred = self.day_type_model.predict(X_test)
        day_type_accuracy = accuracy_score(y_day_type_test, day_type_pred)
        
        print("✅ Machine learning models trained successfully")
        print(f"📊 Day Type Classification Accuracy: {day_type_accuracy:.2%}")
    
    def classify_day_type(self, rainfall, temperature, wind_speed, rain_probability):
        """Classify the day type based on predicted weather parameters"""
        # Enhanced classification logic
        if rainfall > 25 and wind_speed > 30 and rain_probability > 80:
            return 'thunderstorm', '⛈️ Thunderstorm Day'
        elif rainfall > 15 and wind_speed > 25:
            return 'thunderstorm', '⛈️ Thunderstorm Day'
        elif rainfall > 20:
            return 'heavy_rain', '🌧️ Heavy Rain Day'
        elif rainfall > 10:
            return 'rainy', '🌧️ Rainy Day'
        elif rainfall > 5:
            return 'moderate_rain', '🌦️ Moderate Rain Day'
        elif rainfall > 2:
            return 'light_rain', '🌦️ Light Rain Day'
        elif rainfall > 0.1 or rain_probability > 60:
            return 'cloudy_rainy', '🌧️☁️ Cloudy with Rain'
        elif rain_probability > 40:
            return 'cloudy', '☁️ Cloudy Day'
        elif temperature > 35:
            return 'sunny_hot', '☀️🔥 Sunny Hot Day'
        elif temperature > 30:
            return 'sunny_warm', '☀️🌡️ Sunny Warm Day'
        elif temperature > 25:
            return 'sunny_pleasant', '☀️😊 Sunny Pleasant Day'
        elif temperature > 20:
            return 'sunny_cool', '☀️❄️ Sunny Cool Day'
        else:
            return 'sunny_cold', '☀️🧊 Sunny Cold Day'
    
    def validate_date(self, date_str):
        """Validate if date is within allowed range (today to 6 months future)"""
        try:
            input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if input_date < self.today:
                return False, "Date cannot be in the past. Please select today or a future date."
            elif input_date > self.max_future_date:
                return False, f"Date cannot be more than 6 months in the future. Maximum allowed: {self.max_future_date}"
            else:
                return True, input_date
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD format."
    
    def get_coordinates(self, city, state, country):
        """Get coordinates for the location"""
        city_coords = {
            'delhi': (28.6139, 77.2090), 'mumbai': (19.0760, 72.8777),
            'chennai': (13.0827, 80.2707), 'bangalore': (12.9716, 77.5946),
            'kolkata': (22.5726, 88.3639), 'hyderabad': (17.3850, 78.4867),
            'pune': (18.5204, 73.8567), 'ahmedabad': (23.0225, 72.5714),
            'jaipur': (26.9124, 75.7873), 'lucknow': (26.8467, 80.9462),
            'kochi': (9.9312, 76.2673), 'goa': (15.2993, 74.1240),
            'shimla': (31.1048, 77.1734), 'darjeeling': (27.0412, 88.2663)
        }
        
        city_key = city.lower()
        return city_coords.get(city_key, (20.5937, 78.9629))
    
    def get_elevation(self, lat, lng):
        """Get elevation data"""
        try:
            params = {'locations': f'{lat},{lng}'}
            response = requests.get(self.elevation_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['results'][0]['elevation'] if data['results'] else 0
        except:
            pass
        return 0
    
    def predict_single_day(self, city, state, country, target_date):
        """Predict weather for a single specific day with day type classification"""
        # Validate date
        is_valid, result = self.validate_date(target_date)
        if not is_valid:
            return result
        
        target_date_obj = result
        
        # Get location data
        lat, lng = self.get_coordinates(city, state, country)
        elevation = self.get_elevation(lat, lng)
        
        # Extract date components
        year = target_date_obj.year
        month = target_date_obj.month
        day = target_date_obj.day
        day_of_year = target_date_obj.timetuple().tm_yday
        
        # Get historical data for features
        recent_data = self.daily_df[
            (self.daily_df['YEAR'] == year - 1) & 
            (self.daily_df['MONTH'] == month) & 
            (self.daily_df['DAY'] == day)
        ]
        
        if recent_data.empty:
            # Use average of similar dates
            similar_data = self.daily_df[
                (self.daily_df['MONTH'] == month) & 
                (self.daily_df['DAY'] == day) &
                (self.daily_df['YEAR'] >= year - 5)
            ]
            
            if not similar_data.empty:
                temp_lag = similar_data['TEMPERATURE'].mean()
                rain_lag = similar_data['RAINFALL'].mean()
                wind_lag = similar_data['WIND_SPEED'].mean()
                temp_roll = similar_data['TEMPERATURE'].mean()
                rain_roll = similar_data['RAINFALL'].mean()
            else:
                temp_lag, rain_lag, wind_lag, temp_roll, rain_roll = 25, 0, 10, 25, 0
        else:
            temp_lag = recent_data['TEMPERATURE'].values[0]
            rain_lag = recent_data['RAINFALL'].values[0]
            wind_lag = recent_data['WIND_SPEED'].values[0]
            temp_roll = recent_data['TEMPERATURE'].values[0]
            rain_roll = recent_data['RAINFALL'].values[0]
        
        # Prepare features
        features = np.array([[
            year, month, day, day_of_year, year - 1900,
            np.sin(2 * np.pi * day_of_year / 365),
            np.cos(2 * np.pi * day_of_year / 365),
            np.sin(2 * np.pi * month / 12),
            np.cos(2 * np.pi * month / 12),
            temp_lag, rain_lag, wind_lag, temp_roll, rain_roll,
            25 + 0.02 * (year - 2000)
        ]])
        
        # Make predictions
        temp_pred = float(self.temp_model.predict(features)[0])
        rain_amount_pred = max(0, float(self.rain_model.predict(features)[0]))
        rain_prob = float(self.rain_class_model.predict_proba(features)[0][1] * 100)
        wind_pred = max(0, float(self.wind_model.predict(features)[0]))
        
        # Predict day type using ML model
        ml_day_type = self.day_type_model.predict(features)[0]
        ml_day_type_proba = np.max(self.day_type_model.predict_proba(features))
        
        # Adjust for elevation and climate
        temp_pred += (-0.0065 * elevation) + (0.02 * (year - 2000))
        
        # Enhanced day type classification
        day_type, day_type_description = self.classify_day_type(
            rain_amount_pred, temp_pred, wind_pred, rain_prob
        )
        
        # Determine weather condition
        condition = self.get_weather_condition(temp_pred, rain_prob, wind_pred)
        
        return {
            'city': city,
            'state': state,
            'country': country,
            'date': target_date,
            'day_name': target_date_obj.strftime("%A"),
            'temperature': round(temp_pred, 1),
            'rain_probability': round(rain_prob, 1),
            'expected_rainfall': round(rain_amount_pred, 1),
            'wind_speed': round(wind_pred, 1),
            'condition': condition,
            'day_type': day_type,
            'day_type_description': day_type_description,
            'ml_day_type': ml_day_type,
            'ml_confidence': round(ml_day_type_proba * 100, 1),
            'elevation': round(elevation, 1),
            'coordinates': f"({lat:.4f}, {lng:.4f})"
        }
    
    def get_weather_condition(self, temp, rain_prob, wind_speed):
        """Determine weather condition"""
        if rain_prob > 70:
            return "Stormy" if wind_speed > 25 else "Rainy with strong winds" if wind_speed > 15 else "Rainy"
        elif rain_prob > 40:
            return "Cloudy with strong winds" if wind_speed > 20 else "Cloudy with chance of rain"
        else:
            if temp > 35:
                return "Hot and windy" if wind_speed > 20 else "Hot and sunny"
            elif temp > 25:
                return "Warm and breezy" if wind_speed > 15 else "Warm and pleasant"
            elif temp > 15:
                return "Cool and windy" if wind_speed > 15 else "Cool and clear"
            else:
                return "Cold"

def display_prediction(prediction):
    """Display the weather prediction with day type classification"""
    print("\n" + "="*70)
    print("🌤️  WEATHER PREDICTION RESULTS")
    print("="*70)
    
    print(f"📍 Location: {prediction['city']}, {prediction['state']}, {prediction['country']}")
    print(f"📅 Date: {prediction['date']} ({prediction['day_name']})")
    print(f"🌍 Coordinates: {prediction['coordinates']}")
    print(f"⛰️  Elevation: {prediction['elevation']} meters")
    
    # Display DAY TYPE prominently
    print(f"\n🎯 DAY TYPE: {prediction['day_type_description']}")
    print(f"   📊 ML Model Confidence: {prediction['ml_confidence']}%")
    print(f"   🤖 ML Predicted Type: {prediction['ml_day_type'].replace('_', ' ').title()}")
    
    print("\n📊 Detailed Weather Forecast:")
    print(f"   🌡️  Temperature: {prediction['temperature']}°C")
    print(f"   🌧️  Rain Probability: {prediction['rain_probability']}%")
    print(f"   💧 Expected Rainfall: {prediction['expected_rainfall']} mm")
    print(f"   💨 Wind Speed: {prediction['wind_speed']} km/h")
    print(f"   ☁️  General Condition: {prediction['condition']}")
    
    # Specialized recommendations based on day type
    print(f"\n💡 {prediction['day_type_description'].split(' ')[-1]} DAY RECOMMENDATIONS:")
    
    day_type = prediction['day_type']   
    if 'thunderstorm' in day_type:
        print("   ⚡ Avoid outdoor activities")
        print("   🌩️ Stay away from tall objects and water")
        print("   🏠 Consider indoor alternatives")
    elif 'rainy' in day_type or 'heavy_rain' in day_type:
        print("   ☔ Carry waterproof gear")
        print("   🚗 Allow extra travel time")
        print("   📱 Check for flood alerts")
    elif 'cloudy' in day_type:
        print("   🌂 Carry an umbrella just in case")
        print("   📷 Good day for photography")
        print("   🚶 Pleasant for walking")
    elif 'sunny' in day_type:
        if 'hot' in day_type:
            print("   🥤 Stay hydrated")
            print("   ☂️ Use sun protection")
            print("   ⏰ Avoid peak sun hours (12-3 PM)")
        elif 'warm' in day_type:
            print("   😊 Perfect outdoor day")
            print("   🌳 Great for picnics and activities")
            print("   💧 Keep water handy")
        else:
            print("   👕 Dress in layers")
            print("   🚶 Excellent for outdoor activities")
            print("   🌅 Enjoy the pleasant weather")
    
    print("="*70)

def main():
    print("="*70)
    print("🌤️  ADVANCED WEATHER PREDICTION SYSTEM")
    print("="*70)
    print("Predict weather and day type for any specific date")
    print("Day Types: ☀️ Sunny, 🌧️ Rainy, ☁️ Cloudy, ⛈️ Thunderstorm")
    print("="*70)
    
    # Initialize predictor
    try:
        predictor = WeatherPredictor()
        print("✅ System initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Display date limits
    print(f"\n📅 Date Range Available:")
    print(f"   Today: {predictor.today}")
    print(f"   Maximum Future Date: {predictor.max_future_date}")
    print(f"   (6 months from today)")
    
    # Get user input
    print("\n📍 Enter Location Details:")
    city = input("City: ").strip() or "Mumbai"
    state = input("State: ").strip() or "Maharashtra"
    country = input("Country: ").strip() or "India"
    
    print(f"\n📅 Enter Prediction Date:")
    print("   Format: YYYY-MM-DD (e.g., 2025-06-15)")
    
    while True:
        target_date = input("Date: ").strip()
        if not target_date:
            # Default to 30 days from today
            default_date = predictor.today + timedelta(days=30)
            target_date = default_date.strftime("%Y-%m-%d")
            print(f"   Using default date: {target_date}")
            break
        
        is_valid, message = predictor.validate_date(target_date)
        if is_valid:
            break
        else:
            print(f"   ❌ {message}")
            print("   Please enter a valid date:")
    
    # Make prediction
    print("\n" + "="*70)
    print("🔮 Generating advanced weather prediction...")
    print("="*70)
    
    prediction = predictor.predict_single_day(city, state, country, target_date)
    
    if isinstance(prediction, str):
        # Error message
        print(f"❌ Prediction Error: {prediction}")
    else:
        # Success - display prediction
        display_prediction(prediction)
        
        # Option to predict another date
        while True:
            another = input("\n🔍 Predict another date? (y/n): ").strip().lower()
            if another in ['y', 'yes']:
                print("\n📅 Enter New Prediction Date:")
                target_date = input("Date: ").strip()
                prediction = predictor.predict_single_day(city, state, country, target_date)
                if isinstance(prediction, str):
                    print(f"❌ Error: {prediction}")
                else:
                    display_prediction(prediction)
            elif another in ['n', 'no', '']:
                print("\n🙏 Thank you for using the Advanced Weather Prediction System!")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no")

if __name__ == "__main__":
    main()