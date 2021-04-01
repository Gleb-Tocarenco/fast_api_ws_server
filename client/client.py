import json
import requests
from websocket import create_connection
channels = requests.get('http://127.0.0.1:8000/channels/').json()['channels']
ws = create_connection('ws://127.0.0.1:8000/ws/')
ws.send(json.dumps({"action": "connect", "channel": channels[0]}))
ws.send(json.dumps({"action": "update", "channel": [channels[1], channels[2]]}))
ws.send(json.dumps({"action": "disconnect", "channel": channels[2]}))
ws.recv()
