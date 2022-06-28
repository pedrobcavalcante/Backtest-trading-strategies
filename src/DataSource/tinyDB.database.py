import os
from tinydb import TinyDB, where

class DataBase:
    
    def __init__(self, db_name):
        self.db = TinyDB(os.path.join('DB', db_name + ".json"))
        self.db_name = db_name

    def insert(self, data):
        table = self.db.table(self.db_name)
        table.insert(data)
        
    def get(self):
        table = self.db
        return table.all()

    def search(self, field, data):
        results = self.db.search(where(field) == data)
        print(results)

    def update(self, field, data, id):
        #self.db.update(data, doc_id = id)
        results = self.db.search(doc_id=id)
        for res in results:
            res[field] = data
        self.db.write_back(results)

    def insertMultiple(self, data):
        table = self.db
        table.insert_multiple(data)

    def delete(self, id):
        self.db.remove(doc_id = id)


DataBasecompras = DataBase('compras')
#DataBaseEstrategias = DataBase('estrategys')

#DataBasecompras.insert({"name": "teste"})
DataBasecompras.update("name", "davi", 2)