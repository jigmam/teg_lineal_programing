
def send_ws_message(ws, msg):
    ws.send(msg)
    ws.receive()
        
