from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ============================================================================
# Coin Schemas
# ============================================================================

# Coin Schemas
class CoinBase(BaseModel):
    inventory_number: Optional[str] = None  # Auto-generated if not provided
    country: Optional[str] = None
    denomination: Optional[str] = None
    year: Optional[int] = None
    mint_mark: Optional[str] = None
    composition: Optional[str] = None
    weight_grams: Optional[float] = None
    diameter_mm: Optional[float] = None
    condition_grade: Optional[str] = None
    condition_notes: Optional[str] = None
    defects: Optional[str] = None
    catalog_number: Optional[str] = None
    variety: Optional[str] = None
    error_type: Optional[str] = None
    notes: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    acquisition_price: Optional[float] = None
    acquisition_source: Optional[str] = None
    is_for_sale: bool = False
    location: Optional[str] = None

class CoinCreate(CoinBase):
    pass

class CoinUpdate(CoinBase):
    pass

class CoinImageSchema(BaseModel):
    id: UUID
    file_path: str
    image_type: Optional[str] = None
    is_primary: bool = False
    width: Optional[int] = None
    height: Optional[int] = None
    
    class Config:
        from_attributes = True

class AIAnalysisSchema(BaseModel):
    id: UUID
    created_at: datetime
    identified_country: Optional[str] = None
    identified_denomination: Optional[str] = None
    identified_year: Optional[int] = None
    ai_grade: Optional[str] = None
    wear_level: Optional[str] = None
    detected_defects: Optional[str] = None
    authenticity_assessment: Optional[str] = None
    authenticity_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True

class ValuationSchema(BaseModel):
    id: UUID
    created_at: datetime
    estimated_value_low: Optional[float] = None
    estimated_value_high: Optional[float] = None
    estimated_value_avg: Optional[float] = None
    currency: str = "USD"
    rarity_score: Optional[int] = None
    market_demand: Optional[str] = None
    confidence_level: Optional[str] = None
    
    class Config:
        from_attributes = True

class CoinSchema(CoinBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    images: List[CoinImageSchema] = []
    analyses: List[AIAnalysisSchema] = []
    valuations: List[ValuationSchema] = []
    
    class Config:
        from_attributes = True

class CoinListSchema(BaseModel):
    id: UUID
    inventory_number: str
    country: Optional[str] = None
    denomination: Optional[str] = None
    year: Optional[int] = None
    condition_grade: Optional[str] = None
    primary_image: Optional[str] = None
    estimated_value: Optional[float] = None
    
    class Config:
        from_attributes = True

# AI Analysis Request
class AnalyzeImageRequest(BaseModel):
    image_path: str
    coin_id: Optional[UUID] = None

# eBay Listing Schemas
class EbayListingCreate(BaseModel):
    coin_id: UUID
    listing_title: str
    listing_description: str
    starting_price: float
    buy_it_now_price: Optional[float] = None

class EbayListingSchema(BaseModel):
    id: UUID
    coin_id: UUID
    ebay_item_id: Optional[str] = None
    listing_title: str
    status: str
    created_at: datetime
    listed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Search and Filter
class CoinSearchParams(BaseModel):
    query: Optional[str] = None
    country: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    denomination: Optional[str] = None
    condition_grade: Optional[str] = None
    is_for_sale: Optional[bool] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    limit: int = 50
    offset: int = 0
