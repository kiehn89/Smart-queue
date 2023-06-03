import sqlite3
import requests

class Callnext:  
    ## starter thread til "/call-next"
    def call_next_thread():
        response = requests.get('http://0.0.0.0:80/callnext')
        if response.ok:
            print('Næste i køen!')

class Clientcount:
    ## Connecter til database og anvender SELECT COUNT (ALL) som henter antallet af rækker i databasen, fetchone() henter så den ene værdi. ##
    def get_client_count():
        client_count = 0
        conn = sqlite3.connect('clients.db')  
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        result = cursor.fetchone()
        client_count = result[0]
        conn.close()

        return client_count
