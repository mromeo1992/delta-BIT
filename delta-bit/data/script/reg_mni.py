from fastapi import FastAPI

app = FastAPI()

@app.post("/run")
def run_training():
    # qui parte la tua pipeline
    #read config
    # esegui ants

    # esempio simulazione
    import time
    time.sleep(5)

    return {"status": "done"}