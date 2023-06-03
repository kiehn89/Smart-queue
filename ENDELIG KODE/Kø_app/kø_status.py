from flask import Flask, request

## ##
app = Flask(__name__)

## Sætter en global værdi til 0 ##
client_count1 = 0
client_count2 = 0
client_count3 = 0

## Ruterne som beskederne med JSON indeholder ##
@app.route('/data1', methods=['POST'])
def receive_estimated_time1():
    data = request.get_json()
    global client_count1
    client_count1 = data.get('client_count1') * 2
    return 'Success'

@app.route('/data2', methods=['POST'])
def receive_estimated_time2():
    data = request.get_json()
    global client_count2
    client_count = data.get('client_count2') * 2
    return 'Success'

@app.route('/data3', methods=['POST'])
def receive_estimated_time3():
    data = request.get_json()
    global client_count3
    client_count3 = data.get('client_count3') * 2
    return 'Success'

## index siden for kø status ##
@app.route('/')
def serve_html():
    with open('index.html') as f:
        html = f.read()
    html = html.replace('{{client_count1}}', str(client_count1))
    html = html.replace('{{client_count2}}', str(client_count2))
    html = html.replace('{{client_count3}}', str(client_count3))
    return html

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=80, debug=False)
