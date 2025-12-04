from fastapi import FastAPI
from cllm.src.api.routes import router

app = FastAPI()
app.include_router(router)
