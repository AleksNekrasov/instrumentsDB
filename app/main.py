from fastapi import FastAPI

app = FastAPI(title="FastAPI база учета инструмента",
              version="0.1.0",)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API по учету инструмента"}