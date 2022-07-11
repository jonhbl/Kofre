import os
import sanitizer
import database
from dotenv import load_dotenv
load_dotenv()

SERVER = os.getenv('SERVER')
DATABASE = os.getenv('DATABASE')
DRIVER = os.getenv('DRIVER')
TABLE = os.getenv('TABLE')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
print('-' * 100)
print(f'Adicionando dados a tabela {TABLE} do BD {DATABASE}.')

sqlClient = database.SQLConnect(
    server=SERVER,
    database=DATABASE,
    driver=DRIVER,
    table=TABLE,
    user=USER,
    password=PASSWORD
)

sqlClient.connect()

DIR = 'galeao_1m'
files = [arq for arq in os.listdir(DIR) if '.txt' in arq]
sqlClient.clear()
for file in files:
    try:
        events = sanitizer.getEvents(DIR, file)
        for id_, event in events.items():
            try:
                sqlClient.create(event['Data'], event['ID'], event['Grupo'], event['Canal'], event['Evento'], event['CodEvento'], event['Duracao'], event['site'])
            except KeyError:
                print(f"Evento {event['ID']} não foi adicionado por estar incompleto!")
    except Exception as e:
        print(e)
        print(f'Não foi possível adicionar o arquivo {file}!')
    print()
