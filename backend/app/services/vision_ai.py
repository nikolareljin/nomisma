from google import genai
from google.genai import types
import io
import os
from typing import Dict, Any, Optional
from PIL import Image
import json

class VisionAIService:
    """Service for AI-powered coin analysis using Google Gemini Vision"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-1.5-flash"
        else:
            self.client = None
            self.model_name = None
    
    def analyze_coin(self, image_path: str) -> Dict[str, Any]:
        """Analyze a coin image and extract detailed information"""
        
        if not self.client:
            return self._mock_analysis()
        
        try:
            # Load image
            img = Image.open(image_path)
            image_part = self._image_part(img)
            
            # Comprehensive prompt for coin analysis
            prompt = """Analyze this coin image in detail and provide the following information in JSON format:

{
  "identification": {
    "country": "Country of origin",
    "denomination": "Coin denomination/value",
    "year": "Year minted (number only)",
    "mint_mark": "Mint mark if visible",
    "composition": "Metal composition"
  },
  "condition": {
    "grade": "Condition grade (e.g., Poor, Fair, Good, Very Good, Fine, Very Fine, Extremely Fine, About Uncirculated, Uncirculated)",
    "wear_level": "Level of wear (Minimal, Light, Moderate, Heavy, Severe)",
    "surface_quality": "Surface condition (Excellent, Good, Fair, Poor)",
    "strike_quality": "Strike quality (Sharp, Average, Weak)",
    "luster": "Luster rating (Full, Partial, Minimal, None)"
  },
  "defects": {
    "scratches": "Description of scratches if any",
    "dents": "Description of dents if any",
    "corrosion": "Description of corrosion if any",
    "cleaning": "Signs of cleaning (Yes/No)",
    "other": "Other defects"
  },
  "errors": {
    "doubled_die": "Doubled die errors (Yes/No)",
    "off_center": "Off-center strike (Yes/No)",
    "missing_elements": "Missing design elements",
    "other_errors": "Other minting errors"
  },
  "authenticity": {
    "assessment": "Likely Authentic, Questionable, or Likely Counterfeit",
    "confidence": "Confidence percentage (0-100)",
    "concerns": "Any authenticity concerns"
  },
  "notable_features": "Any special or notable features",
  "rarity_estimate": "Rarity estimate (Common, Scarce, Rare, Very Rare, Extremely Rare)"
}

Provide only the JSON response, no additional text."""

            # Generate analysis
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image_part],
            )
            
            # Parse JSON response
            response_text = (response.text or "").strip()
            if not response_text:
                raise ValueError("Empty response from Gemini API")
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            analysis = json.loads(response_text.strip())
            
            return {
                "success": True,
                "analysis": analysis,
                "model_version": self.model_name,
                "raw_response": response.text or ""
            }
            
        except Exception as e:
            print(f"AI Analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": self._mock_analysis()["analysis"]
            }
    
    def estimate_value(self, analysis: Dict[str, Any], coin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate coin value based on analysis and market data"""
        
        if not self.client:
            return self._mock_valuation()
        
        try:
            prompt = f"""Based on the following coin information, provide a market value estimate in JSON format:

Coin Details:
{json.dumps(coin_data, indent=2)}

AI Analysis:
{json.dumps(analysis, indent=2)}

Provide a value estimate in this JSON format:
{{
  "estimated_value_low": "Lower bound in USD",
  "estimated_value_high": "Upper bound in USD",
  "estimated_value_avg": "Average estimate in USD",
  "rarity_score": "Rarity score 1-10",
  "condition_multiplier": "Condition multiplier (e.g., 1.5 for excellent condition)",
  "market_demand": "Low, Moderate, High, or Very High",
  "confidence_level": "Low, Medium, or High",
  "valuation_notes": "Brief explanation of the valuation"
}}

Provide only the JSON response."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
            )
            response_text = (response.text or "").strip()
            if not response_text:
                raise ValueError("Empty response from Gemini API")
            
            # Clean response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            valuation = json.loads(response_text.strip())
            
            return {
                "success": True,
                "valuation": valuation
            }
            
        except Exception as e:
            print(f"Valuation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "valuation": self._mock_valuation()["valuation"]
            }

    def _image_part(self, img: Image.Image) -> types.Part:
        """Convert a PIL image to a Gemini image part."""
        img_format = img.format if img.format in Image.MIME else "PNG"
        mime_type = Image.MIME.get(img_format, "image/png")
        buffer = io.BytesIO()
        if img_format.upper() in ("JPEG", "JPG") and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(buffer, format=img_format)
        return types.Part.from_bytes(data=buffer.getvalue(), mime_type=mime_type)
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """Mock analysis for testing without API key"""
        return {
            "success": True,
            "analysis": {
                "identification": {
                    "country": "United States",
                    "denomination": "1 Cent",
                    "year": 1943,
                    "mint_mark": "D",
                    "composition": "Steel with zinc coating"
                },
                "condition": {
                    "grade": "Very Fine",
                    "wear_level": "Light",
                    "surface_quality": "Good",
                    "strike_quality": "Average",
                    "luster": "Partial"
                },
                "defects": {
                    "scratches": "Minor surface scratches",
                    "dents": "None visible",
                    "corrosion": "Light oxidation",
                    "cleaning": "No",
                    "other": "None"
                },
                "errors": {
                    "doubled_die": "No",
                    "off_center": "No",
                    "missing_elements": "None",
                    "other_errors": "None"
                },
                "authenticity": {
                    "assessment": "Likely Authentic",
                    "confidence": 85,
                    "concerns": "None significant"
                },
                "notable_features": "Wartime steel penny",
                "rarity_estimate": "Common"
            },
            "model_version": "mock",
            "raw_response": "Mock response - no API key configured"
        }
    
    def _mock_valuation(self) -> Dict[str, Any]:
        """Mock valuation for testing"""
        return {
            "success": True,
            "valuation": {
                "estimated_value_low": 0.50,
                "estimated_value_high": 2.00,
                "estimated_value_avg": 1.00,
                "rarity_score": 3,
                "condition_multiplier": 1.2,
                "market_demand": "Moderate",
                "confidence_level": "Medium",
                "valuation_notes": "Common wartime steel penny in circulated condition"
            }
        }

# Global instance
vision_ai_service = VisionAIService()
