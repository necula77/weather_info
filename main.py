

# citim de la tastatura un oras si sa ne dea temperatura curenta, starea curenta, cantul si directia vantului
# notificare windows
# daca ploua bine inchidem geamurile strangem rufele

import openai
import time
import requests
import json
from plyer import notification


def get_weather(url, city, auth):

    try:
        headers = {"key": auth}
        response = requests.get(url + f"?q={city}", headers=headers)

        if response.status_code == 200:
            response_dict = response.json()
            weather_info = response_dict["current"]
            return weather_info
        else:
            return f"Error: {response.text} with code {response.status_code}."

    except requests.exceptions.RequestException as e:
        return "Request exception: {e}"
    except Exception as e:
        return print(f"Exception is {type(e)}: {e}")


def get_forecast(url, city, auth):
    try:
        headers = {"key": auth}
        response = requests.get(url + f"?q={city}&days=2", headers=headers)

        if response.status_code == 200:
            response_dict = response.json()
            forecast_info = response_dict["forecast"]["forecastday"][1]["day"]
            return forecast_info
        else:
            return f"Error: {response.text} with code {response.status_code}."

    except requests.exceptions.RequestException as e:
        return "Request exception: {e}"
    except Exception as e:
        return print(f"Exception is {type(e)}: {e}")


def send_alerts(config, weather: dict, forecast: dict):

    over_thresholds = {}

    for city, v in weather.items():
        notification_alert = []
        if v["temp_c"] > config["max_temp"]:
            over_thresholds["temp_c"] = True
            notification_alert.append(f"Temperatura este f mare: {v['temp_c']}. ")
        if v["wind_kph"] > config["max_wind_velocity"]:
            over_thresholds["wind_kph"] = True
            notification_alert.append(f"Viteza vantului este f mare : {v['wind_kph']}. ")
        if v["pressure_mb"] > config["max_pressure"]:
            over_thresholds["pressure_mb"] = True
            notification_alert.append(f"Presiunea atmosferica este f mare: {v['pressure_mb']}. ")
        if v["humidity"] > config["max_humidity"]:
            over_thresholds["humidity"] = True
            notification_alert.append(f"Umiditatea este f mare: {v['humidity']}. ")

        notification_alert.append(f"The weather outside is " + v['condition']['text'] + ". ")

        print(f"City: {city}\n" + "\n".join(notification_alert))

        if notification_alert:
            notification.notify(
                title=city,
                message=" ".join(notification_alert),
                app_icon=None,
                timeout=10,
            )
        time.sleep(5)

    for city, x in forecast.items():
        notification_alert = []

        if over_thresholds.get("temp_c", False):
            if x["maxtemp_c"] > config["max_temp"]:
                notification_alert.append(f"La noapte")

        if over_thresholds.get("wind_kph", False):
            if x["maxwind_kph"] > config["max_wind_velocity"]:
                notification_alert.append(f"La noapte")

        if over_thresholds.get("pressure_mb", False):
            if x["maxpressure_mb"] > config["max_pressure"]:
                notification_alert.append(f"La noapte")

        if over_thresholds.get("humidity", False):
            if x["maxhumidity"] > config["max_humidity"]:
                notification_alert.append(f"La noapte")

        if notification_alert:
            notification.notify(
                title=city,
                message=" ".join(notification_alert),
                app_icon=None,
                timeout=10,
            )
        time.sleep(5)


def cities_read(file):
    with open(file, "r") as f:
        cities = json.loads(f.read())
    return cities


def init_config():
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
        return config
    except FileNotFoundError as e:
        print(f"Nu avem fisierul de config {e}")
        exit()
    except PermissionError as e:
        print(f"Nu ai permisiunea sa citesti fisierul de config {e}")
        exit()
    except json.decoder.JSONDecodeError as e:
        print(f"Exception raised because json file is not valid: {e}")
        exit()
    except Exception as e:
        print(f"Unknown Exception {e}.")
        exit()


def read_from_txt_file(file, list):

    ip_list = []

    with open(file, "r") as f:
        for line in file:
            ip_list.append(line.strip())

    return ip_list


if __name__ == "__main__":
    print("Started script here.")
    config = init_config()
    weather = {}
    forecast = {}

    cities = cities_read("cities.json")['cities']

    for city in cities:
        weather[city] = get_weather(config["base_url"], city, auth=config["api_key"])
        forecast[city] = get_forecast(config["forecast_url"], city, auth=config["api_key"])

    send_alerts(config, weather, forecast)
