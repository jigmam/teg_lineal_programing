from tkinter import W
from fastapi import FastAPI, WebSocket
import json

import uvicorn
from optimizador_2 import  main
app = FastAPI()



      

# @app.post("/optimizer")
# async def init_optimizer(data : Request):
#     req_data = await data.json()
#     print(req_data)
#     optimizer.set_optimizer(req_data)
#     return {
#         "status" : "SUCCESS",
#         "data" : req_data
#     }



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            data = json.loads(data)
            breed_id = data.get("breed_id",0)
            date_init = data.get("date_init",0)
            date_end = data.get("date_end",0)
            diference = data.get("diference",0)
            algoritm = data.get("sAloj",0)
            optimizer = data.get("algoritmo",1)
            scenario_id = data.get("idScenario",0)
            result = main(
                date_init,
                date_end,
                diference,
                algoritm, 
                optimizer, 
                breed_id,
                scenario_id)
            await websocket.send_text(str(result))
            await websocket.close()
            break
        except Exception as e:
           print(e)
           await websocket.close()
           break


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)