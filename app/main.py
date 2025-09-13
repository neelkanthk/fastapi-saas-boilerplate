from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth
from app.config import api
from app.config.api import api_name

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get('/', status_code=status.HTTP_200_OK)
def read_root():
    return {
        "message": f"Welcome to {api_name} API.",
        "docs": "/docs",
    }
