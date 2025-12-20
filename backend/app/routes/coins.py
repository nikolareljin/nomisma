from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
import os
from datetime import datetime
import shutil

from ..database import get_db
from ..models import Coin, CoinImage, AIAnalysis, Valuation, User
from ..schemas import (
    CoinCreate, CoinUpdate, CoinSchema, CoinListSchema, 
    CoinSearchParams
)
from ..services.vision_ai import vision_ai_service
from ..auth import get_current_user

router = APIRouter()

IMAGES_PATH = os.getenv("IMAGES_PATH", "/app/images")

@router.post("/", response_model=CoinSchema, status_code=201)
async def create_coin(
    coin: CoinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new coin record"""
    coin_data = coin.model_dump()
    coin_data["user_id"] = current_user.id
    db_coin = Coin(**coin_data)
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin

@router.get("/", response_model=List[CoinListSchema])
async def list_coins(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    country: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    denomination: Optional[str] = None,
    condition_grade: Optional[str] = None,
    is_for_sale: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List coins with optional filtering and search"""
    query = db.query(Coin).filter(Coin.user_id == current_user.id)
    
    # Apply filters
    if country:
        query = query.filter(Coin.country.ilike(f"%{country}%"))
    if year_min:
        query = query.filter(Coin.year >= year_min)
    if year_max:
        query = query.filter(Coin.year <= year_max)
    if denomination:
        query = query.filter(Coin.denomination.ilike(f"%{denomination}%"))
    if condition_grade:
        query = query.filter(Coin.condition_grade == condition_grade)
    if is_for_sale is not None:
        query = query.filter(Coin.is_for_sale == is_for_sale)
    
    # Search across multiple fields
    if search:
        search_filter = or_(
            Coin.inventory_number.ilike(f"%{search}%"),
            Coin.country.ilike(f"%{search}%"),
            Coin.denomination.ilike(f"%{search}%"),
            Coin.notes.ilike(f"%{search}%"),
            Coin.catalog_number.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Sorting
    if hasattr(Coin, sort_by):
        order_column = getattr(Coin, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    
    # Pagination
    coins = query.offset(skip).limit(limit).all()
    
    # Transform to list schema with primary image and estimated value
    result = []
    for coin in coins:
        primary_image = next((img.file_path for img in coin.images if img.is_primary), None)
        if not primary_image and coin.images:
            primary_image = coin.images[0].file_path
        
        estimated_value = None
        if coin.valuations:
            latest_valuation = max(coin.valuations, key=lambda v: v.created_at)
            estimated_value = float(latest_valuation.estimated_value_avg) if latest_valuation.estimated_value_avg else None
        
        result.append(CoinListSchema(
            id=coin.id,
            inventory_number=coin.inventory_number,
            country=coin.country,
            denomination=coin.denomination,
            year=coin.year,
            condition_grade=coin.condition_grade,
            primary_image=primary_image,
            estimated_value=estimated_value
        ))
    
    return result

@router.get("/{coin_id}", response_model=CoinSchema)
async def get_coin(
    coin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific coin by ID"""
    coin = db.query(Coin).filter(
        Coin.id == coin_id,
        Coin.user_id == current_user.id
    ).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin

@router.put("/{coin_id}", response_model=CoinSchema)
async def update_coin(
    coin_id: UUID,
    coin_update: CoinUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a coin record"""
    coin = db.query(Coin).filter(
        Coin.id == coin_id,
        Coin.user_id == current_user.id
    ).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    # Update fields
    update_data = coin_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coin, field, value)
    
    db.commit()
    db.refresh(coin)
    return coin

@router.delete("/{coin_id}", status_code=204)
async def delete_coin(
    coin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a coin record"""
    coin = db.query(Coin).filter(
        Coin.id == coin_id,
        Coin.user_id == current_user.id
    ).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    # Delete associated images from filesystem
    for image in coin.images:
        image_path = os.path.join(IMAGES_PATH, image.file_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(coin)
    db.commit()
    return None

@router.post("/{coin_id}/images", status_code=201)
async def upload_coin_image(
    coin_id: UUID,
    file: UploadFile = File(...),
    image_type: str = "obverse",
    is_primary: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an image for a coin"""
    coin = db.query(Coin).filter(
        Coin.id == coin_id,
        Coin.user_id == current_user.id
    ).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    # Create coin-specific directory
    coin_dir = os.path.join(IMAGES_PATH, str(coin_id))
    os.makedirs(coin_dir, exist_ok=True)
    
    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{image_type}_{timestamp}{file_extension}"
    file_path = os.path.join(coin_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get image dimensions
    from PIL import Image
    img = Image.open(file_path)
    width, height = img.size
    file_size = os.path.getsize(file_path)
    
    # Create database record
    relative_path = f"{coin_id}/{filename}"
    coin_image = CoinImage(
        coin_id=coin_id,
        file_path=relative_path,
        file_size=file_size,
        image_type=image_type,
        is_primary=is_primary,
        width=width,
        height=height,
        format=img.format
    )
    
    db.add(coin_image)
    db.commit()
    db.refresh(coin_image)
    
    return {
        "id": coin_image.id,
        "file_path": relative_path,
        "url": f"/images/{relative_path}"
    }

@router.get("/{coin_id}/stats")
async def get_coin_stats(
    coin_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a coin"""
    coin = db.query(Coin).filter(
        Coin.id == coin_id,
        Coin.user_id == current_user.id
    ).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    return {
        "total_images": len(coin.images),
        "total_analyses": len(coin.analyses),
        "total_valuations": len(coin.valuations),
        "ebay_listings": len(coin.ebay_listings),
        "latest_valuation": coin.valuations[-1].estimated_value_avg if coin.valuations else None,
        "latest_analysis_date": coin.analyses[-1].created_at if coin.analyses else None
    }
