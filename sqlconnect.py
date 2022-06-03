class SQLConnect():
    def __init__(self, server=None, database=None, driver=None, table=None)->None:
        self.server = server
        self.database = database
        self.data = (
                     f"Driver={driver};"
                     f"Server={server};"
                     f"Database={database};"
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
        sql = f"INSERT INTO {self.table}({data},{id_},{grupo},{canal},{evento},{codEvento},{duracao},{site})"
        self.cursor.execute(sql) #git add
        self.cursor.commit() #git commit