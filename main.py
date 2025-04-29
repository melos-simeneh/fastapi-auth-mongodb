from fastapi import FastAPI
from utils.db import  mongo_connection
from contextlib import asynccontextmanager
from routes import auth_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await mongo_connection.connect()
    yield
    # Shutdown
    await mongo_connection.close()

    
app = FastAPI(lifespan=lifespan, 
                title="FastAPI Auth with MongoDB",
                version="1.0.0", description="API Schema")


app.include_router(auth_routes.router)
