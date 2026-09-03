from fastapi import FastAPI

app = FastAPI(title="Capstone API")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend funcionando correctamente"}
