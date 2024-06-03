Instruções


1 - Clonar o Repositório:

git clone https://github.com/seu_usuario/seu_repositorio.git

2 - Navegar até o Diretório do Projeto:

cd seu_repositorio

3 - Criar e Ativar um Ambiente Virtual:

python -m venv venv
 3.1 Windows:

venv\Scripts\activate

 3.2 macOS/Linux:

source venv/bin/activate

4 - Instalar as Dependências:

pip install -r requirements.txt

5 - Configurar as Variáveis de Ambiente:
 5.1 Criar um arquivo .env com o conteúdo (Incluir susas chaves):

  OPEN_WEATHER_MAP_API_KEY=sua_chave_open_weather
  GOOGLE_MAPS_API_KEY=sua_chave_google_maps

6 - Rodar a Aplicação:

python app.py


7 - Acessar a Aplicação:
http://127.0.0.1:8050/dashboard/

Dicas Adicionais
Certifique-se de que o usuário tenha Python instalado em sua máquina.