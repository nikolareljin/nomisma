from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    coins = relationship("Coin", back_populates="user", cascade="all, delete-orphan")


class Coin(Base):
    __tablename__ = "coins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Internal inventory tracking
    inventory_number = Column(String(20), unique=True, nullable=False)
    
    # Basic information
    country = Column(String(100))
    denomination = Column(String(100))
    year = Column(Integer)
    mint_mark = Column(String(20))
    composition = Column(String(200))
    weight_grams = Column(Numeric(10, 3))
    diameter_mm = Column(Numeric(10, 2))
    
    # Condition and grading
    condition_grade = Column(String(50))
    condition_notes = Column(Text)
    defects = Column(Text)
    
    # Cataloging
    catalog_number = Column(String(100))
    variety = Column(String(100))
    error_type = Column(String(100))
    
    # User notes
    notes = Column(Text)
    acquisition_date = Column(DateTime)
    acquisition_price = Column(Numeric(10, 2))
    acquisition_source = Column(String(200))
    
    # Status
    is_for_sale = Column(Boolean, default=False)
    location = Column(String(200))
    
    # Relationships
    user = relationship("User", back_populates="coins")
    images = relationship("CoinImage", back_populates="coin", cascade="all, delete-orphan")
    analyses = relationship("AIAnalysis", back_populates="coin", cascade="all, delete-orphan")
    valuations = relationship("Valuation", back_populates="coin", cascade="all, delete-orphan")
    ebay_listings = relationship("EbayListing", back_populates="coin", cascade="all, delete-orphan")


class CoinImage(Base):
    __tablename__ = "coin_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    image_type = Column(String(20))  # 'obverse', 'reverse', 'edge', 'detail'
    is_primary = Column(Boolean, default=False)
    
    # Image metadata
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(10))
    
    # Relationship
    coin = relationship("Coin", back_populates="images")


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI identification
    identified_country = Column(String(100))
    identified_denomination = Column(String(100))
    identified_year = Column(Integer)
    identified_mint_mark = Column(String(20))
    
    # Condition assessment
    ai_grade = Column(String(50))
    wear_level = Column(String(50))
    surface_quality = Column(String(50))
    strike_quality = Column(String(50))
    luster_rating = Column(String(50))
    
    # Defects and errors
    detected_defects = Column(Text)
    detected_errors = Column(Text)
    
    # Authenticity
    authenticity_assessment = Column(String(50))
    authenticity_confidence = Column(Numeric(5, 2))
    
    # Raw AI response
    raw_response = Column(JSON)
    model_version = Column(String(50))
    
    # Relationship
    coin = relationship("Coin", back_populates="analyses")


class Valuation(Base):
    __tablename__ = "valuations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Estimated values
    estimated_value_low = Column(Numeric(10, 2))
    estimated_value_high = Column(Numeric(10, 2))
    estimated_value_avg = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    
    # Valuation factors
    rarity_score = Column(Integer)
    condition_multiplier = Column(Numeric(5, 2))
    market_demand = Column(String(50))
    
    # Market data
    recent_sales_data = Column(JSON)
    comparable_listings = Column(JSON)
    
    # Metadata
    valuation_source = Column(String(100))
    confidence_level = Column(String(50))
    
    # Relationship
    coin = relationship("Coin", back_populates="valuations")


class EbayListing(Base):
    __tablename__ = "ebay_listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # eBay data
    ebay_item_id = Column(String(100), unique=True)
    listing_title = Column(String(255))
    listing_description = Column(Text)
    starting_price = Column(Numeric(10, 2))
    buy_it_now_price = Column(Numeric(10, 2))
    
    # Status
    status = Column(String(50))  # 'draft', 'active', 'sold', 'ended', 'cancelled'
    listed_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # Sale information
    sold_price = Column(Numeric(10, 2))
    sold_at = Column(DateTime)
    buyer_username = Column(String(100))
    
    # eBay response
    ebay_response = Column(JSON)
    
    # Relationship
    coin = relationship("Coin", back_populates="ebay_listings")
