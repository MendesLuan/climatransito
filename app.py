import os
import requests
from flask import Flask
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dotenv import load_dotenv
import datetime
import dash_leaflet as dl

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter chaves de API das variáveis de ambiente
open_weather_map_api_key = os.getenv('OPEN_WEATHER_MAP_API_KEY')
google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Função para obter informações do clima
def get_weather_info(cidade, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_description = data["weather"][0]["description"].title()
        temperature = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        hourly_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br"
        hourly_response = requests.get(hourly_url)
        hourly_data = hourly_response.json()

        hourly_forecast = []
        if hourly_response.status_code == 200:
            for forecast in hourly_data['list'][:5]:
                time = datetime.datetime.fromtimestamp(forecast['dt']).strftime('%H:%M')
                temp = forecast['main']['temp']
                description = forecast['weather'][0]['description'].title()
                hourly_forecast.append(f"{time} - {temp}°C, {description}")

        return {
            "description": weather_description,
            "temperature": temperature,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "hourly_forecast": hourly_forecast
        }
    else:
        return {
            "error": f"Erro ao obter informações do clima: {data}"
        }

# Função para obter informações de trânsito
def get_traffic_info(origem, destino, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origem}&destination={destino}&key={api_key}&language=pt-BR"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        if "routes" in data and len(data["routes"]) > 0:
            duration = data["routes"][0]["legs"][0]["duration"]["text"]
            distance = data["routes"][0]["legs"][0]["distance"]["text"]
            steps = data["routes"][0]["legs"][0]["steps"]
            
            route_coords = [(step["start_location"]["lat"], step["start_location"]["lng"]) for step in steps]
            end_location = steps[-1]["end_location"]
            route_coords.append((end_location["lat"], end_location["lng"]))

            return {
                "info": f"Distância: {distance}, Duração: {duration}",
                "route_coords": route_coords
            }
        else:
            return {"info": "Nenhuma rota encontrada."}
    else:
        return {"info": f"Erro ao obter informações de trânsito: {data}"}

# Configuração da aplicação Flask
server = Flask(__name__)

# Configuração da aplicação Dash
app = Dash(__name__, server=server, url_base_pathname='/dashboard/')
app.css.append_css({'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'})

# Definindo a imagem de fundo
current_dir = os.path.dirname(os.path.abspath(__file__))
background_image = f'url({os.path.join(current_dir, "ceu_azul.jpg")})'
app.layout = html.Div([
    html.H1("Painel Interativo de Clima e Trânsito", style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label("Cidade:"),
            dcc.Input(id='input-cidade', type='text', value='', placeholder='Digite a cidade', style={'marginBottom': '10px'}),
            html.Button('Obter Clima', id='button-clima', n_clicks=0, style={'marginBottom': '10px'}),
            html.Div(id='output-clima', style={'marginTop': '10px'})
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
        html.Div([
            html.Label("Origem:"),
            dcc.Input(id='input-origem', type='text', value='', placeholder='Digite a origem', style={'marginBottom': '10px'}),
            html.Label("Destino:"),
            dcc.Input(id='input-destino', type='text', value='', placeholder='Digite o destino', style={'marginBottom': '10px'}),
            html.Button('Obter Trânsito', id='button-transito', n_clicks=0, style={'marginBottom': '10px'}),
            html.Div(id='output-transito', style={'marginTop': '10px'}),
            dl.Map(id='map', style={'width': '100%', 'height': '500px', 'margin': "auto", "display": "block", "backgroundImage": background_image}, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="layer")
            ])
        ], style={'textAlign': 'center', 'marginBottom': '20px'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
])

@app.callback(
    Output('output-clima', 'children'),
    [Input('button-clima', 'n_clicks')],
    [Input('input-cidade', 'value')]
)
def update_clima(n_clicks, cidade):
    if n_clicks > 0 and cidade:
        weather_info = get_weather_info(cidade, open_weather_map_api_key)
        if "error" in weather_info:
            return html.Div([
                html.H3(f"Erro: {weather_info['error']}")
            ])
        return html.Div([
            html.Div([
                html.H3(f"{cidade}:", style={'textAlign': 'center'}),
                html.Div([
                    html.P(f"{weather_info['temperature']}°C", style={'fontSize': '48px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '5px'}),
                    html.P(f"{weather_info['description']}", style={'textAlign': 'center'})
                ], style={'textAlign': 'center'})
            ], style={'flex': '1'}),
            html.Div([
                html.H4("Previsão Horária:", style={'textAlign': 'center'}),
                html.Ul([html.Li(forecast) for forecast in weather_info['hourly_forecast']])
            ], style={'flex': '1', 'padding': '0 20px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    return ""

@app.callback(
    [Output('output-transito', 'children'), Output('layer', 'children')],
    [Input('button-transito', 'n_clicks')],
    [Input('input-origem', 'value'), Input('input-destino', 'value')]
)
def update_transito(n_clicks, origem, destino):
    if n_clicks > 0 and origem and destino:
        traffic_info = get_traffic_info(origem, destino, google_maps_api_key)
        if "route_coords" in traffic_info:
            markers = [dl.Marker(position=coord) for coord in traffic_info['route_coords']]
            path = dl.Polyline(positions=traffic_info['route_coords'], color="blue")
            return (
                html.Div([
                    html.H3(f"Trânsito de {origem} para {destino}:"),
                    html.P(traffic_info["info"])
                ]),
                markers + [path]
            )
        return html.Div([
            html.H3(f"Trânsito de {origem} para {destino}:"),
            html.P(traffic_info["info"])
        ]), []
    return "", []

if __name__ == '__main__':
    app.run_server(debug=True)
