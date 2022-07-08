from datetime import datetime
import pyodbc

class SQLConnect():
    def __init__(self, server=None, database=None, driver=None, table=None, user=None, password=None)->None:
        self.server = server
        self.database = database
        self.data = (
                     f"Driver={driver};"
                     f"Server={server};"
                     f"Database={database};"
                     f"UID={user};"
                     f"PWD={password};"
                    )
        self.table = table
            
    def connect(self):
        try:
            self.connection = pyodbc.connect(self.data)
            self.cursor = self.connection.cursor()
            print('Servidor conectado!')
        except Exception as e:
            print(e)
            print('Servidor não conectado!')
        
    
    def create(self, data:datetime, id_:str, grupo:str, canal:str, evento:str, codEvento:int, duracao:float , site:int):
        sql = f"INSERT INTO {self.table} VALUES ('{data.strftime('%d/%m/%Y %H:%M:%S')}','{id_}','{grupo}','{canal}','{evento}',{codEvento},{duracao},{site})"
        try:
            self.cursor.execute(sql) 
            self.cursor.commit() 
            #print(f'Evento {id_} foi adicionado a tabela!')
        except pyodbc.IntegrityError:
            print('A tabela já possui essa linha!')
        except Exception as e:
            print(e)
            print('Houve um erro!')

    def delete(self, column, info):
        sql = f"DELETE FROM {self.table} where {column}={info}"
        try:
            self.cursor.execute(sql) 
            self.cursor.commit() 
            print(f'O linha contendo {info} na coluna {column} foi removida!')
        except:
            print(f'Não foi possível remover {info}!')
        
    def clear(self):
        sql = f"DELETE FROM {self.table};"
        self.cursor.execute(sql) 
        self.cursor.commit() 
        print('Todos os dados da tabela foram removidos!')