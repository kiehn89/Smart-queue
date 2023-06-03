from flask import Flask, request, redirect, render_template, make_response
from sqlite3 import connect
from uuid import uuid4
import os
import requests
from threading import Thread
from smartqueue import Callnext, Clientcount

## TIL TEST MILJØ - FJERNER databaser ved start ##      ##HUSK, linje 94 data sent ##
if os.path.exists('clients.db'):                        ## 
    os.remove('clients.db')
    print("clients.db removed!")
if os.path.exists('old_clients.db'):
    os.remove('old_clients.db')
    print("old_clients.db removed!")

## variable der kalder Flask()##
app = Flask(__name__)

## Målrettet VMqueue ##
kø = '20.67.247.27'

## Estimeret ventetid i "minutter" ##
ventetid = 1

## oprettelse af databaser Overall, using variables for database file names improves code maintainability, readability, and flexibility, making it easier to work with databases and adapt to different scenarios.##
def create_clients_database():
    conn = connect('clients.db')
    conn.execute('CREATE TABLE IF NOT EXISTS clients (id TEXT, position INTEGER)')
    conn.commit()
    return conn

def create_old_clients_database():
    conn = connect('old_clients.db')
    conn.execute('CREATE TABLE IF NOT EXISTS old_clients (id TEXT)')
    conn.commit()
    return conn

## Route til index siden og kø visning ##
@app.route('/')
def index():
## Retriever klientens session ID ##
    session_id = request.cookies.get('session_id')
    print("Session ID retrieved:", session_id)
## Her kigger den på om hvor vidt session ID allerede er i old_clients. ##
    conn_old_clients = create_old_clients_database()
    cursor_old_clients = conn_old_clients.execute('SELECT id FROM old_clients WHERE id = ?', (session_id,))
    result_old_clients = cursor_old_clients.fetchone()
## Hvis den er i old_clients vil den redirecte til /static ##
    if result_old_clients:
        print(result_old_clients, "BLOCKED")
        return redirect('/thanks')
## Såfremt klienten ikke har et session ID endnu ##
    if not session_id:
        session_id = str(uuid4())
        print("Session ID given", session_id)
        response = make_response()
        response.set_cookie('session_id', session_id)
        return response
## Henter 'position' værdien fra clients table i clients.db til en specifik client (session ID). ##
    conn_clients = create_clients_database()
    cursor_clients = conn_clients.execute('SELECT position FROM clients WHERE id = ?', (session_id,))
    result_clients = cursor_clients.fetchone()
    print("The position number", result_clients, "is fetched")
## Laver variablen position og tildeler den det tal som result_clients[0] indeholder. ##
    if result_clients:
        position = result_clients[0]
        print(session_id,"'s", "position in queue:", position)
## Henter den højeste position i clients.db og tildeler den næste klient en position. ##
    else:
        cursor_position = conn_clients.execute('SELECT MAX(position) FROM clients')
        result_position = cursor_position.fetchone()
        if result_position[0]:
            position = result_position[0] + 1
            print("New position =", position)
        else:
            position = 1
            print("Ingen andre i kø")
## Her indsættes klientes session id og position ##
        conn_clients.execute('INSERT INTO clients (id, position) VALUES (?, ?)', (session_id, position))
        conn_clients.commit()
        print(session_id, "og", position, "er indsat i clients databasen")
##  Her indsættes de forskellige variable og sendes til HTML##
    with open('templates/index.html') as f:
        html = f.read().replace('{{counter}}', str(position))
        estimated_time = position * ventetid
        html = html.replace('{{estimated_time}}', str(estimated_time))
        print("Opdateret side")
## Sender client count til vores kø status host ## 
    client_count = Clientcount.get_client_count()
    response = requests.post('http://' + kø + ':80/data3',json={'client_count3': client_count})
    if response.ok:
        print("Estimated time sent to counter.py host")
    return html

## når knappen i bod_knap.html trykkes modtages /call-next GET som i værksætter call_next() funktionen. Den starter funktionen fra modulet smartqueue og classen Callnext
@app.route('/call-next')
def call_next():
    Thread(target=Callnext.call_next_thread).start()
    return 'Success'

## Den her route er svaret fra den ovenstående funktion. og ved get beskeden /callnext initieres hele call_next funktionen som overordnet fjerner og opdaterer positionen
@app.route('/callnext')
def callnext():
    conn_clients = create_clients_database()
    cursor_position = conn_clients.execute('SELECT MIN(position) FROM clients')
    result_position = cursor_position.fetchone()

    if result_position[0] == 1:
        cursor_clients = conn_clients.execute('SELECT id FROM clients WHERE position = 1')
        result_clients = cursor_clients.fetchone()

        if result_clients:
            removed_client = result_clients[0]
            conn_clients.execute('DELETE FROM clients WHERE id = ?', (removed_client,))
            conn_clients.commit()
            print(removed_client, "removed")

            conn_old_clients = create_old_clients_database()
            conn_old_clients.execute('INSERT INTO old_clients (id) VALUES (?)', (removed_client,))
            conn_old_clients.commit()
            print(removed_client, "indsat i old_clients.db")

            conn_clients.execute('UPDATE clients SET position = position - 1 WHERE position > 1')
            conn_clients.commit()
            print("Position opdateret")

            redirect('/thanks')

## Route til /static som viser vores tak.html ##
@app.route('/thanks')
def takker():
    return render_template('tak.html') 

## Route til /bod funktion som anvender JS i bod_knap.html ##
@app.route('/bod')
def nextinline():
    return render_template('bod_knap.html')

print("Smart Queue Initiated!!! We're ONLINE!!!")

## if name=main tilsikrer at app.run() kun vil blive kørt direkte fra scriptet og ikke som et importeret modul ##
if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=80, debug=False)

print("Programmet afbrudt")

##           SSSS    M       M   AAA   RRRRRR   TTTTTT    QQQQ    U     U   EEEEE
##          S        MM     MM  A   A  RR   RR    TT     QQ   QQ  U     U   E
##           SSS     M M   M M  AAAAAA  RRRRRR     TT    QQ   QQ  U     U   EEEE
##              S    M  M M  M  A     A RR  RR     TT    QQ  QQ   U     U   E
##          SSSS     M   M   M  A     A RR   RR    TT     QQQQ      UUUUU    EEEEE
