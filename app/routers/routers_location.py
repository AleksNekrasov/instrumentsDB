from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database_depends import get_db
from app.table_models.table_location import Location
from app.schemas_pydantic.location_pydantic import LocationUpdate, LocationResponse, LocationCreate, LocationDelete

from app.helpers import correct_name

router = APIRouter(prefix='/locations', tags=["Locations"])

@router.post("/", response_model=LocationResponse, status_code=201)
async def post_new_location(new_location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """ создание новой локации"""
    # сначала ищем локацию в базе:
    old_stmt = select(Location).where(Location.name == correct_name(new_location.name))
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
    location = Location(**new_location.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)

    return location


