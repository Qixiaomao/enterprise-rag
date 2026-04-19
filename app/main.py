from fastapi import FastAPI

app = FastAPI(title = "Enterprise RAG")

@app.get("/")
def root():
    return {"status":"ok"}