import time

# citim de la tastatura un oras si sa ne dea temperatura curenta, starea curenta, cantul si directia vantului
# notificare windows
# daca ploua bine inchidem geamurile strangem rufele

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


def send_alerts(config, weather):

    for oras, value in weather.items():

        notification_alert = []

        if int(value["temp_c"]) > int(config["max_temp"]):
            notification_alert.append(f"Temperatura este foarte mare in: {value['temp_c']}.")
        if int(value["wind_kph"]) > int(config["max_wind_velocity"]):
            notification_alert.append(f"Viteza vantului este foarte mare: {value['wind_kph']}.")
        if int(value["pressure_mb"]) > int(config["max_pressure"]):
            notification_alert.append(f"Presiunea atmosferica este foarte mare: {value['pressure_mb']}.")

        print(notification_alert)

        if notification_alert:
            notification.notify(
                title=city,
                message="".join(notification_alert),
                app_icon=None,
                timeout=10,
            )

        time.sleep(5)



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


if __name__ == "__main__":
    print("Started script here.")
    config = init_config()
    weather = {}

    while True:

        city = input("Introdu orasul despre care vrei sa aflii informatii. Scrie N pentru exit: \n >> ")
        if city.lower() == "n":
            break
        weather[city] = get_weather(config["base_url"],city, auth=config["api_key"])

    send_alerts(config, weather)
