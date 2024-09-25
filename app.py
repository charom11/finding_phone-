from flask import Flask, request, jsonify, render_template
import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

Key = "ac093794d4d047ee915b90c52fc9bba3"

# In-memory store for location data
location_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track-number', methods=['POST'])
def track_number():
    number = request.json.get('number')
    
    try:
        check_number = phonenumbers.parse(number)
        number_location = geocoder.description_for_number(check_number, "en")
        service_provider = carrier.name_for_number(check_number, "en")

        geocoder_instance = OpenCageGeocode(Key)
        results = geocoder_instance.geocode(number_location)

        if results:
            lat = results[0]['geometry']['lat']
            lng = results[0]['geometry']['lng']
            location_data[number] = {'location': number_location, 'service_provider': service_provider, 'latitude': lat, 'longitude': lng}
            return jsonify({
                'location': number_location,
                'service_provider': service_provider,
                'latitude': lat,
                'longitude': lng
            })
        else:
            return jsonify({'error': 'Location not found'}), 404
            
    except phonenumbers.NumberParseException:
        return jsonify({'error': 'Invalid phone number format'}), 400
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.get_json()
    number = data.get('number')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if number and latitude is not None and longitude is not None:
        location_data[number] = {'latitude': latitude, 'longitude': longitude}
        print(f"Updated Location for {number}: Latitude: {latitude}, Longitude: {longitude}")
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Number or location not provided."), 400


@app.route('/get-location/<number>', methods=['GET'])
def get_location(number):
    data = location_data.get(number)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'No location found for this number.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
