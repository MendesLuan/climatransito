import os
import requests
from flask import Flask
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter chaves de API das variáveis de ambiente (Deixei as chaves em um arquivo separado por questão de segurança)
open_weather_map_api_key = os.getenv('OPEN_WEATHER_MAP_API_KEY')
google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Função para obter informações do clima (incluí "lang=pt_br" para trazer respostas em português)
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

# Função para obter informações de trânsito (incluí "lang=pt_br" para trazer respostas em português)
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

# Configuração da aplicação Flask
server = Flask(__name__)

# Configuração da aplicação Dash
app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

app.layout = html.Div([
    html.H1("Painel Interativo de Clima e Trânsito"),
    html.Div([
        html.Label("Cidade:"),
        dcc.Input(id='input-cidade', type='text', value='Araranguá')
    ]),
    html.Button('Obter Clima', id='button-clima', n_clicks=0),
    html.Div(id='output-clima'),

    html.Div([
        html.Label("Origem:"),
        dcc.Input(id='input-origem', type='text', value='Araranguá'),
        html.Label("Destino:"),
        dcc.Input(id='input-destino', type='text', value='Criciúma')
    ]),
    html.Button('Obter Trânsito', id='button-transito', n_clicks=0),
    html.Div(id='output-transito')
])

@app.callback(
    Output('output-clima', 'children'),
    [Input('button-clima', 'n_clicks')],
    [Input('input-cidade', 'value')]
)
def update_clima(n_clicks, cidade):
    if n_clicks > 0:
        weather_info = get_weather_info(cidade, open_weather_map_api_key)
        return html.Div([
            html.H3(f"Clima em {cidade}:"),
            html.P(weather_info)
        ])
    return ""

@app.callback(
    Output('output-transito', 'children'),
    [Input('button-transito', 'n_clicks')],
    [Input('input-origem', 'value'), Input('input-destino', 'value')]
)
def update_transito(n_clicks, origem, destino):
    if n_clicks > 0:
        traffic_info = get_traffic_info(origem, destino, google_maps_api_key)
        return html.Div([
            html.H3(f"Trânsito de {origem} para {destino}:"),
            html.P(traffic_info)
        ])
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
