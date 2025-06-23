from fastapi import FastAPI
from api import layer_router, user_router, digital_twin_router, group_router, tool_router
from db.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router.router)
app.include_router(digital_twin_router.router)
app.include_router(layer_router.router)
app.include_router(group_router.router)
app.include_router(tool_router.router)