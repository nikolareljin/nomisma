from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models import Coin, EbayListing, User
from ..schemas import EbayListingCreate, EbayListingSchema
from ..services.ebay_service import ebay_service
from ..auth import get_request_user

router = APIRouter()

@router.post("/list", response_model=EbayListingSchema)
async def create_ebay_listing(
    listing: EbayListingCreate,
    current_user: User = Depends(get_request_user),
    db: Session = Depends(get_db)
):
    """Create an eBay listing for a coin"""
    try:
        # Get coin - ensure it belongs to current user
        coin = db.query(Coin).filter(
            Coin.id == listing.coin_id,
            Coin.user_id == current_user.id
        ).first()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")
        
        # Prepare coin data
        coin_data = {
            "id": str(coin.id),
            "country": coin.country,
            "denomination": coin.denomination,
            "year": coin.year,
            "mint_mark": coin.mint_mark,
            "condition_grade": coin.condition_grade,
            "catalog_number": coin.catalog_number
        }
        
        # Prepare listing data
        listing_data = {
            "listing_title": listing.listing_title,
            "listing_description": listing.listing_description,
            "starting_price": listing.starting_price,
            "buy_it_now_price": listing.buy_it_now_price
        }
        
        # Create eBay listing
        result = ebay_service.create_listing(coin_data, listing_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create eBay listing: {result.get('error', 'Unknown error')}"
            )
        
        # Save listing to database
        ebay_listing = EbayListing(
            coin_id=listing.coin_id,
            ebay_item_id=result.get("item_id"),
            listing_title=listing.listing_title,
            listing_description=listing.listing_description,
            starting_price=listing.starting_price,
            buy_it_now_price=listing.buy_it_now_price,
            status="active",
            listed_at=result.get("start_time"),
            ebay_response=result.get("response")
        )
        
        db.add(ebay_listing)
        
        # Mark coin as for sale
        coin.is_for_sale = True
        
        db.commit()
        db.refresh(ebay_listing)
        
        return ebay_listing
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listings/{coin_id}")
async def get_coin_listings(
    coin_id: UUID,
    current_user: User = Depends(get_request_user),
    db: Session = Depends(get_db)
):
    """Get all eBay listings for a coin"""
    try:
        coin = db.query(Coin).filter(
            Coin.id == coin_id,
            Coin.user_id == current_user.id
        ).first()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")
        
        return {
            "success": True,
            "listings": coin.ebay_listings,
            "count": len(coin.ebay_listings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{item_id}")
async def get_listing_status(
    item_id: str,
    current_user: User = Depends(get_request_user)
):
    """Get the status of an eBay listing"""
    try:
        result = ebay_service.get_listing_status(item_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get listing status: {result.get('error', 'Unknown error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth")
async def ebay_auth():
    """Handle eBay OAuth authentication"""
    # This would typically redirect to eBay's OAuth flow
    # For now, return instructions
    return {
        "message": "eBay OAuth integration",
        "instructions": [
            "1. Register your application at https://developer.ebay.com/",
            "2. Obtain App ID, Dev ID, and Cert ID",
            "3. Generate a User Token",
            "4. Add credentials to .env file",
            "5. Restart the application"
        ],
        "documentation": "https://developer.ebay.com/api-docs/static/oauth-tokens.html"
    }

@router.get("/categories")
async def get_ebay_categories():
    """Get common eBay categories for coins"""
    return {
        "categories": [
            {"id": "11116", "name": "Coins: US"},
            {"id": "45086", "name": "Coins: World"},
            {"id": "3452", "name": "Coins: Ancient"},
            {"id": "39619", "name": "Coins: Medieval"},
            {"id": "4733", "name": "Bullion"}
        ]
    }
