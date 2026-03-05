import requests
import json
import datetime as dt

start_date = dt.datetime.fromisoformat("2026-10-15")
sample_dates = [(start_date + dt.timedelta(days=30 * i)).isoformat()[:10] for i in range(12)]

url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"

for date in sample_dates:
    print(f"Durchforste Flüge für {date}...")

    querystring = {"departure_id":"BER","arrival_id":"NRT","outbound_date": date, "travel_class":"ECONOMY","adults":"2","show_hidden":"1","currency":"EUR","language_code":"en-US","country_code":"DE","search_type":"best"}

    headers = {
	"x-rapidapi-key": "7b885e71d2msh354774867106b55p1bc55djsnba797b36a354",
	"x-rapidapi-host": "google-flights2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        wunschpreis: int = 1300

        top_flights = data['data']['itineraries']['topFlights']
        other_flights = data['data']['itineraries']['otherFlights']
        all_flights = {'all_itineraries': top_flights + other_flights}

        filtered = [f for f in all_flights["all_itineraries"] if str(f["price"]).isdigit() and int(f["price"]) <= wunschpreis]

        if filtered:
            cheapest = min(filtered, key=lambda f: int(f["price"]))
            print(f"{len(filtered)} Flüge gefunden. Günstigster: {cheapest["price"]}€")
            dateiname = f"Mathe/p{wunschpreis}_d{date}.json"
            with open(dateiname, "w") as f:
                try:
                    json.dump(filtered, f, indent=4)
                except:
                    print("ups.")
        else: print(f"Nix unter {wunschpreis}. :(")
    else: print("Keine Daten bekommen.")