from contextlib import asynccontextmanager
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Path, status
from sqlalchemy import func
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Item, ItemCreate, ItemRead, ItemStatus, ItemUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables when the application starts
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Lost & Found System API",
    description="A FastAPI-based REST API for reporting and managing lost and found items on campus.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to the College Lost & Found System API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


# 1. POST /items - Create a new lost/found item
@app.post(
    "/items",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
    summary="Create a new lost or found item report",
)
def create_item(
    item_in: ItemCreate,
    session: Session = Depends(get_session)
):
    db_item = Item.model_validate(item_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# 2. GET /items - Return all reported items
@app.get(
    "/items",
    response_model=List[ItemRead],
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Retrieve all reported items",
)
def read_all_items(
    session: Session = Depends(get_session)
):
    items = session.exec(select(Item)).all()
    return items


# 6. GET /items/status/{status} - Return items based on their status
@app.get(
    "/items/status/{status}",
    response_model=List[ItemRead],
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Filter items by status (Lost, Found, Returned)",
)
def read_items_by_status(
    status: ItemStatus = Path(..., description="Item status: 'Lost', 'Found', or 'Returned'"),
    session: Session = Depends(get_session)
):
    items = session.exec(select(Item).where(Item.status == status)).all()
    return items


# 7. GET /items/category/{category} - Return all items belonging to a particular category
@app.get(
    "/items/category/{category}",
    response_model=List[ItemRead],
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Filter items by category",
)
def read_items_by_category(
    category: str = Path(..., min_length=1, description="Category name (e.g., Electronics, Documents, Accessories)"),
    session: Session = Depends(get_session)
):
    # Case-insensitive category match
    query = select(Item).where(func.lower(Item.category) == category.strip().lower())
    items = session.exec(query).all()
    return items


# 3. GET /items/{item_id} - Return a specific item using its ID
@app.get(
    "/items/{item_id}",
    response_model=ItemRead,
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Retrieve a specific item by its ID",
)
def read_item_by_id(
    item_id: int = Path(..., ge=1, description="The ID of the item to retrieve"),
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist."
        )
    return item


# 4. PUT /items/{item_id} - Update details/status of an existing item
@app.put(
    "/items/{item_id}",
    response_model=ItemRead,
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Update details or status of an existing item",
)
def update_item(
    item_id: int = Path(..., ge=1, description="The ID of the item to update"),
    item_in: ItemUpdate = ...,
    session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist."
        )

    # Extract updated fields
    update_data = item_in.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(db_item, field_name, value)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# 5. DELETE /items/{item_id} - Delete an item report
@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    tags=["Items"],
    summary="Delete an item report by ID",
)
def delete_item(
    item_id: int = Path(..., ge=1, description="The ID of the item to delete"),
    session: Session = Depends(get_session)
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist."
        )

    session.delete(db_item)
    session.commit()
    return {
        "message": f"Item with ID {item_id} was successfully deleted.",
        "id": item_id
    }
