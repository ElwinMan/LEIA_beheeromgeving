from fastapi import FastAPI
from api import layer_router, user_router, digital_twin_router, group_router, tool_router, project_router, cesium_router, story_router, bookmark_router,export_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|frontend):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(digital_twin_router.router)
app.include_router(layer_router.router)
app.include_router(group_router.router)
app.include_router(tool_router.router)
app.include_router(export_router.router)
app.include_router(project_router.router)
app.include_router(cesium_router.router)
app.include_router(story_router.router)
app.include_router(bookmark_router.router)