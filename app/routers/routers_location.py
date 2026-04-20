from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database_depends import get_db
from app.table_models.table_location import Location
from app.schemas_pydantic.location_pydantic import (LocationUpdate,
                                                    LocationResponse,
                                                    LocationCreate,
                                                    LocationDelete,
                                                    LocationWithToolsResponse)

from app.helpers import (correct_name,
                         select_locations,
                         select_location_with_list_tools,
                         update_model)

router = APIRouter(prefix='/locations', tags=["Locations"])

@router.post("/", response_model=LocationResponse, status_code=201)
async def post_new_location(new_location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """ создание новой локации"""
    normalized_name = correct_name(new_location.name) # приводим отправленное нам название локации в корректный вид
    # сначала ищем локацию в базе:
    old_stmt = select(Location).where(Location.name == normalized_name)
    old_location = (await db.scalars(old_stmt)).one_or_none()

    #если нашли такую локацию и она активна:
    if old_location and old_location.is_active:
        return old_location

    # Если нашли такую локацию и она в статусе False
    if old_location and not old_location.is_active:
        old_location.is_active = True
        await db.commit()
        await db.refresh(old_location)
        return old_location

    # Если такая локация не найдена:
    data = new_location.model_dump() # распаковка в словарь
    data["name"] = normalized_name   # меняем name на корректную запись
    location = Location(**data)      # записываем в новый объект Location
    db.add(location)                 # добавляем в базу
    await db.commit()
    await db.refresh(location)

    return location


@router.get("/", response_model=list[LocationResponse])
async def get_all_locations(db: AsyncSession = Depends(get_db)):
    """возвращает список всех активных локаций"""
    stmt = select_locations()
    locations = (await db.scalars(stmt)).all()
    return locations

@router.get("/{location_id}", response_model=LocationWithToolsResponse)
async def location_with_tools(location_id: int,
                              db: AsyncSession = Depends(get_db)):
    """Локация по id со списком инструментов в ней"""
    stmt = select_location_with_list_tools(location_id=location_id)
    location = (await db.scalars(stmt)).one_or_none()

    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return location

@router.put("/{location_id}", response_model=LocationResponse)
async  def put_location_by_id(location_id: int, location_update: LocationUpdate, db: AsyncSession = Depends(get_db)):
    # ищем локацию
    stmt = select_locations().where(Location.id == location_id)
    location = (await db.scalars(stmt)).one_or_none()

    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    data = location_update.model_dump(exclude_unset=True)  # распаковка объекта в словарь

    update_model(obj=Location, data=data) # обновляем наш объект новыми значениями

    await db.commit()
    await db.refresh(location)

    return  location




