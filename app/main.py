from fastapi import FastAPI

from app.routers.routers_employee import router as employee_router

app = FastAPI(title="FastAPI база учета инструмента",
              version="0.1.0",
              )

app.include_router(employee_router)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API по учету инструмента"}
