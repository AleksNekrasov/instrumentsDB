from fastapi import FastAPI


from app.routers.routers_employee import router as employee_router
from app.routers.routers_location import router as location_router
from app.routers.routers_tool_model import router as tool_model_router
from app.routers.routers_tool import router as tool_router
from app.routers.routers_tool_issues import router as tool_issue_router
from app.routers.routers_tool_movement import router as tool_movement_router
from app.routers.router_users import router as user_router
from app.routers.routers_repair import router as repair_router

app = FastAPI(title="FastAPI база учета инструмента",
              version="0.1.0",
              )

app.include_router(repair_router)
app.include_router(employee_router)
app.include_router(location_router)
app.include_router(tool_model_router)
app.include_router(tool_router)
app.include_router(tool_issue_router)
app.include_router(tool_movement_router)
app.include_router(user_router)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API по учету инструмента"}

