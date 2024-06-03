import requests

# Chave de API do OpenWeatherMap
open_weather_map_api_key = "d0bc266300a74662704475aab82905f3"

# Chave de API do Google Maps
google_maps_api_key = "AIzaSyCnIRb6l1oCXqLnxphxinW156umG9LsVi8"


# Função para obter informações do clima
def get_weather_info(cidade, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"] 
        return f"Descrição: {weather_description}, Temperatura: {temperature}°C"
    else:
        return f"Erro ao obter informações do clima: {data}"

# Função para obter informações de trânsito
def get_traffic_info(origem, destino, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origem}&destination={destino}&key={api_key}&language=pt-BR"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if "routes" in data and len(data["routes"]) > 0:
            duration = data["routes"][0]["legs"][0]["duration"]["text"]
            distance = data["routes"][0]["legs"][0]["distance"]["text"]
            return f"Distância: {distance}, Duração: {duration}"
        else:
            return "Nenhuma rota encontrada."
    else:
        return f"Erro ao obter informações de trânsito: {data}"

# Obter a cidade do usuário
cidade = input("Digite o nome da cidade: ")

# Obter origem e destino do usuário
origem = input("Digite a origem: ")
destino = input("Digite o destino: ")

# Informações do clima
weather_info = get_weather_info(cidade, open_weather_map_api_key)
print(f"Condição do tempo em {cidade}: {weather_info}")

# Informações de trânsito
traffic_info = get_traffic_info(origem, destino, google_maps_api_key)
print(f"Informações de trânsito de {origem} para {destino}: {traffic_info}")


