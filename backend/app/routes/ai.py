from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import asyncio
import os

from ..database import get_db
from ..models import Coin, AIAnalysis, Valuation, User
from ..schemas import AnalyzeImageRequest
from ..services.vision_ai import vision_ai_service
from ..auth import get_request_user

router = APIRouter()

IMAGES_PATH = os.getenv("IMAGES_PATH", "/app/images")

@router.post("/analyze")
async def analyze_coin_image(
    request: AnalyzeImageRequest,
    current_user: User = Depends(get_request_user),
    db: Session = Depends(get_db)
):
    """Analyze a coin image using AI"""
    try:
        # Construct full image path
        image_path = os.path.join(IMAGES_PATH, request.image_path)
        images_root = os.path.abspath(IMAGES_PATH)
        image_path_abs = os.path.abspath(image_path)

        if os.path.commonpath([image_path_abs, images_root]) != images_root:
            raise HTTPException(status_code=400, detail="Invalid image path")

        if not os.path.exists(image_path_abs):
            raise HTTPException(status_code=404, detail="Image not found")

        # Perform AI analysis (may take a long time)
        result = await asyncio.to_thread(vision_ai_service.analyze_coin, image_path_abs)
        
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Analysis failed")
            }
        
        analysis_data = result["analysis"]
        
        # If coin_id provided, save analysis to database
        if request.coin_id:
            coin = db.query(Coin).filter(
                Coin.id == request.coin_id,
                Coin.user_id == current_user.id
            ).first()
            if not coin:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            # Create AI analysis record
            ai_analysis = AIAnalysis(
                coin_id=request.coin_id,
                identified_country=analysis_data.get("identification", {}).get("country"),
                identified_denomination=analysis_data.get("identification", {}).get("denomination"),
                identified_year=analysis_data.get("identification", {}).get("year"),
                identified_mint_mark=analysis_data.get("identification", {}).get("mint_mark"),
                ai_grade=analysis_data.get("condition", {}).get("grade"),
                wear_level=analysis_data.get("condition", {}).get("wear_level"),
                surface_quality=analysis_data.get("condition", {}).get("surface_quality"),
                strike_quality=analysis_data.get("condition", {}).get("strike_quality"),
                luster_rating=analysis_data.get("condition", {}).get("luster"),
                detected_defects=str(analysis_data.get("defects", {})),
                detected_errors=str(analysis_data.get("errors", {})),
                authenticity_assessment=analysis_data.get("authenticity", {}).get("assessment"),
                authenticity_confidence=analysis_data.get("authenticity", {}).get("confidence"),
                raw_response=result,
                model_version=result.get("model_version")
            )
            
            db.add(ai_analysis)
            
            # Update coin with identified information
            if analysis_data.get("identification"):
                ident = analysis_data["identification"]
                if not coin.country and ident.get("country"):
                    coin.country = ident["country"]
                if not coin.denomination and ident.get("denomination"):
                    coin.denomination = ident["denomination"]
                if not coin.year and ident.get("year"):
                    coin.year = ident["year"]
                if not coin.mint_mark and ident.get("mint_mark"):
                    coin.mint_mark = ident["mint_mark"]
                if not coin.composition and ident.get("composition"):
                    coin.composition = ident["composition"]
            
            if analysis_data.get("condition") and not coin.condition_grade:
                coin.condition_grade = analysis_data["condition"].get("grade")
            
            db.commit()
            db.refresh(ai_analysis)
            
            return {
                "success": True,
                "analysis": analysis_data,
                "analysis_id": ai_analysis.id,
                "coin_updated": True
            }
        
        return {
            "success": True,
            "analysis": analysis_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/estimate-value/{coin_id}")
async def estimate_coin_value(
    coin_id: UUID,
    current_user: User = Depends(get_request_user),
    db: Session = Depends(get_db)
):
    """Estimate the value of a coin based on AI analysis"""
    try:
        coin = db.query(Coin).filter(
            Coin.id == coin_id,
            Coin.user_id == current_user.id
        ).first()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")
        
        # Get latest AI analysis
        if not coin.analyses:
            raise HTTPException(
                status_code=400, 
                detail="No AI analysis found. Please analyze the coin first."
            )
        
        latest_analysis = max(coin.analyses, key=lambda a: a.created_at)
        
        # Prepare coin data
        coin_data = {
            "country": coin.country,
            "denomination": coin.denomination,
            "year": coin.year,
            "mint_mark": coin.mint_mark,
            "composition": coin.composition,
            "condition_grade": coin.condition_grade,
            "catalog_number": coin.catalog_number,
            "variety": coin.variety,
            "error_type": coin.error_type
        }
        
        # Prepare analysis data
        analysis_data = {
            "grade": latest_analysis.ai_grade,
            "wear_level": latest_analysis.wear_level,
            "surface_quality": latest_analysis.surface_quality,
            "defects": latest_analysis.detected_defects,
            "errors": latest_analysis.detected_errors,
            "authenticity": latest_analysis.authenticity_assessment,
            "rarity": latest_analysis.raw_response.get("analysis", {}).get("rarity_estimate") if latest_analysis.raw_response else None
        }
        
        primary_image = next((img.file_path for img in coin.images if img.is_primary), None)
        if not primary_image and coin.images:
            primary_image = coin.images[0].file_path

        if not primary_image:
            raise HTTPException(status_code=400, detail="No coin image available for valuation")

        image_path = os.path.join(IMAGES_PATH, primary_image)
        images_root = os.path.abspath(IMAGES_PATH)
        image_path_abs = os.path.abspath(image_path)

        if os.path.commonpath([image_path_abs, images_root]) != images_root:
            raise HTTPException(status_code=400, detail="Invalid image path")

        if not os.path.exists(image_path_abs):
            raise HTTPException(status_code=404, detail="Image not found")

        # Get valuation estimate
        result = vision_ai_service.estimate_value_from_image(image_path_abs, analysis_data, coin_data)
        
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error", "Valuation failed")
            }
        
        valuation_data = result["valuation"]
        
        # Save valuation to database
        valuation = Valuation(
            coin_id=coin_id,
            estimated_value_low=valuation_data.get("estimated_value_low"),
            estimated_value_high=valuation_data.get("estimated_value_high"),
            estimated_value_avg=valuation_data.get("estimated_value_avg"),
            rarity_score=valuation_data.get("rarity_score"),
            condition_multiplier=valuation_data.get("condition_multiplier"),
            market_demand=valuation_data.get("market_demand"),
            confidence_level=valuation_data.get("confidence_level"),
            recent_sales_data={
                "formatted_response": result.get("formatted_response"),
                "raw_response": result.get("raw_response"),
                "model_version": result.get("model_version")
            },
            valuation_source=f"AI - {result.get('model_version') or 'Gemini'}"
        )
        
        db.add(valuation)
        db.commit()
        db.refresh(valuation)
        
        return {
            "success": True,
            "valuation": valuation_data,
            "valuation_id": valuation.id,
            "formatted_response": result.get("formatted_response"),
            "raw_response": result.get("raw_response"),
            "model_version": result.get("model_version")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{coin_id}")
async def find_similar_coins(
    coin_id: UUID,
    limit: int = 5,
    current_user: User = Depends(get_request_user),
    db: Session = Depends(get_db)
):
    """Find similar coins based on characteristics"""
    try:
        coin = db.query(Coin).filter(
            Coin.id == coin_id,
            Coin.user_id == current_user.id
        ).first()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")
        
        # Build similarity query - only search within user's coins
        query = db.query(Coin).filter(
            Coin.id != coin_id,
            Coin.user_id == current_user.id
        )
        
        # Match on country, denomination, and year range
        if coin.country:
            query = query.filter(Coin.country == coin.country)
        if coin.denomination:
            query = query.filter(Coin.denomination == coin.denomination)
        if coin.year:
            query = query.filter(Coin.year.between(coin.year - 5, coin.year + 5))
        
        similar_coins = query.limit(limit).all()
        
        # Format response
        results = []
        for similar_coin in similar_coins:
            primary_image = next((img.file_path for img in similar_coin.images if img.is_primary), None)
            if not primary_image and similar_coin.images:
                primary_image = similar_coin.images[0].file_path
            
            estimated_value = None
            if similar_coin.valuations:
                latest_val = max(similar_coin.valuations, key=lambda v: v.created_at)
                estimated_value = float(latest_val.estimated_value_avg) if latest_val.estimated_value_avg else None
            
            results.append({
                "id": similar_coin.id,
                "country": similar_coin.country,
                "denomination": similar_coin.denomination,
                "year": similar_coin.year,
                "condition_grade": similar_coin.condition_grade,
                "primary_image": primary_image,
                "estimated_value": estimated_value
            })
        
        return {
            "success": True,
            "similar_coins": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
