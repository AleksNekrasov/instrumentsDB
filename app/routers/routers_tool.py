from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database_depends import get_db
from app.table_models.table_tool import Tool
from app.schemas_pydantic.tool_pydantic import (ToolResponse,
                                                ToolCreate,
                                                ToolUpdate,
                                                ToolShortResponse)

from app.helpers import (correct_name,
                         select_response,
                         select_location_with_list_tools,
                         update_model,
                         create_model)

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/", status_code=201, response_model=ToolResponse)
async def post_new_tool(new_tool: ToolCreate, db: AsyncSession = Depends(get_db)):
