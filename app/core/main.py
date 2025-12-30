from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    Base.metadata.create_all(bind=engine)
    
    yield  

    pass


app = FastAPI(lifespan=lifespan)