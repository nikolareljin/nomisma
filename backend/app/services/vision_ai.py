from google import genai
from google.genai import types
import io
import mimetypes
import os
import re
from typing import Dict, Any, Optional, Tuple
import httpx
from PIL import Image
import json

class VisionAIService:
    """Service for AI-powered coin analysis using Google Gemini Vision"""

    DEFAULT_MODEL_CANDIDATES = (
        "gemini-2.5-flash-image",
        "gemini-3-flash-preview",
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-latest",
        "gemini-1.0-pro-vision",
        "gemini-1.0-pro-vision-latest",
    )
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.api_version = os.getenv("GEMINI_API_VERSION", "v1")
            try:
                self.client = genai.Client(api_key=api_key, api_version=self.api_version)
            except TypeError:
                self.client = genai.Client(api_key=api_key)
                self.api_version = None
            self.model_name = os.getenv("GEMINI_MODEL")
            self.estimate_api_version = os.getenv("GEMINI_ESTIMATE_API_VERSION", "v1beta")
            self.estimate_model_name = os.getenv("GEMINI_ESTIMATE_MODEL", "gemini-2.5-flash")
            self.api_key = api_key
        else:
            self.client = None
            self.model_name = None
            self.api_version = None
            self.estimate_api_version = None
            self.estimate_model_name = None
            self.api_key = None

    def _normalize_model_name(self, name: str) -> str:
        if name.startswith("models/"):
            return name.split("/", 1)[1]
        return name

    def _list_models(self) -> list:
        if not self.client:
            return []
        try:
            return list(self.client.models.list())
        except Exception:
            return []

    def _select_model_name(self, force_refresh: bool = False) -> Optional[str]:
        if self.model_name and not force_refresh:
            return self.model_name

        models = self._list_models()
        available = set()
        for model in models:
            name = getattr(model, "name", None)
            if name:
                available.add(self._normalize_model_name(name))

        for candidate in self.DEFAULT_MODEL_CANDIDATES:
            if candidate in available:
                self.model_name = candidate
                return self.model_name

        if self.model_name:
            return self.model_name
        if self.DEFAULT_MODEL_CANDIDATES:
            self.model_name = self.DEFAULT_MODEL_CANDIDATES[0]
        return self.model_name

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
            model_name = self._select_model_name()
            response = self.client.models.generate_content(
                model=model_name,
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
            error_message = str(e)
            if "NOT_FOUND" in error_message or "not found" in error_message:
                fallback_model = self._select_model_name(force_refresh=True)
                if fallback_model and fallback_model != model_name:
                    try:
                        response = self.client.models.generate_content(
                            model=fallback_model,
                            contents=[prompt, image_part],
                        )
                        response_text = (response.text or "").strip()
                        if not response_text:
                            raise ValueError("Empty response from Gemini API")
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
                            "model_version": fallback_model,
                            "raw_response": response.text or ""
                        }
                    except Exception as retry_error:
                        error_message = str(retry_error)

            print(f"AI Analysis error: {error_message}")
            return {
                "success": False,
                "error": error_message,
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

            model_name = self._select_model_name()
            response = self.client.models.generate_content(
                model=model_name,
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
            error_message = str(e)
            if "NOT_FOUND" in error_message or "not found" in error_message:
                fallback_model = self._select_model_name(force_refresh=True)
                if fallback_model and fallback_model != model_name:
                    try:
                        response = self.client.models.generate_content(
                            model=fallback_model,
                            contents=[prompt],
                        )
                        response_text = (response.text or "").strip()
                        if not response_text:
                            raise ValueError("Empty response from Gemini API")

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
                    except Exception as retry_error:
                        error_message = str(retry_error)

            print(f"Valuation error: {error_message}")
            return {
                "success": False,
                "error": error_message,
                "valuation": self._mock_valuation()["valuation"]
            }

    def estimate_value_from_image(
        self,
        image_path: str,
        analysis: Dict[str, Any],
        coin_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate coin value using the image upload flow (v1beta)."""
        if not self.api_key:
            return self._mock_valuation()

        try:
            file_uri, mime_type = self._upload_image(image_path)
            prompt = self._build_estimate_prompt(analysis, coin_data)
            response_json = self._generate_content_with_file(file_uri, mime_type, prompt)
            formatted_text = self._extract_text(response_json)
            low, high, avg = self._extract_value_range(formatted_text)

            valuation = {
                "estimated_value_low": low,
                "estimated_value_high": high,
                "estimated_value_avg": avg,
                "rarity_score": None,
                "condition_multiplier": None,
                "market_demand": "Unknown",
                "confidence_level": None,
                "valuation_notes": formatted_text
            }

            return {
                "success": True,
                "valuation": valuation,
                "formatted_response": formatted_text,
                "raw_response": response_json,
                "model_version": response_json.get("modelVersion")
            }
        except Exception as e:
            error_message = str(e)
            print(f"Valuation error: {error_message}")
            return {
                "success": False,
                "error": error_message,
                "valuation": self._mock_valuation()["valuation"]
            }

    def _upload_image(self, image_path: str) -> Tuple[str, str]:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"

        file_size = os.path.getsize(image_path)
        base_url = "https://generativelanguage.googleapis.com"
        upload_url = f"{base_url}/upload/{self.estimate_api_version}/files"

        headers = {
            "x-goog-api-key": self.api_key,
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(file_size),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json",
        }
        metadata = {"file": {"display_name": os.path.basename(image_path)}}

        with httpx.Client(timeout=60.0) as client:
            init_response = client.post(upload_url, headers=headers, json=metadata)
            init_response.raise_for_status()
            upload_location = init_response.headers.get("x-goog-upload-url")
            if not upload_location:
                raise ValueError("Missing upload URL from Gemini API")

            with open(image_path, "rb") as handle:
                upload_headers = {
                    "x-goog-api-key": self.api_key,
                    "Content-Length": str(file_size),
                    "X-Goog-Upload-Offset": "0",
                    "X-Goog-Upload-Command": "upload, finalize",
                }
                upload_response = client.post(
                    upload_location,
                    headers=upload_headers,
                    content=handle.read()
                )
                upload_response.raise_for_status()
                payload = upload_response.json()

        file_uri = payload.get("file", {}).get("uri")
        if not file_uri:
            raise ValueError("Gemini upload did not return a file URI")

        return file_uri, mime_type

    def _generate_content_with_file(self, file_uri: str, mime_type: str, prompt: str) -> Dict[str, Any]:
        base_url = "https://generativelanguage.googleapis.com"
        model = self.estimate_model_name
        endpoint = f"{base_url}/{self.estimate_api_version}/models/{model}:generateContent"
        payload = {
            "contents": [{
                "parts": [
                    {"file_data": {"mime_type": mime_type, "file_uri": file_uri}},
                    {"text": prompt}
                ]
            }]
        }
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _build_estimate_prompt(self, analysis: Dict[str, Any], coin_data: Dict[str, Any]) -> str:
        return (
            "Caption this image and estimate value on the collectibles market for this coin. "
            "Compare to other similar coins and recommend pricing. "
            "Use clear markdown headings and bullet points where helpful.\n\n"
            "Coin Details:\n"
            f"{json.dumps(coin_data, indent=2)}\n\n"
            "AI Analysis:\n"
            f"{json.dumps(analysis, indent=2)}\n"
        )

    def _extract_text(self, response_json: Dict[str, Any]) -> str:
        candidates = response_json.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            texts = [part.get("text", "") for part in parts if part.get("text")]
            if texts:
                return "\n".join(texts).strip()
        return ""

    def _extract_value_range(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        range_matches = re.findall(r"\\$([0-9]+(?:\\.[0-9]+)?)\\s*(?:-|to)\\s*\\$([0-9]+(?:\\.[0-9]+)?)", text, flags=re.IGNORECASE)
        if range_matches:
            low, high = range_matches[0]
            low_val = float(low)
            high_val = float(high)
            avg_val = round((low_val + high_val) / 2, 2)
            return low_val, high_val, avg_val

        values = [float(val) for val in re.findall(r"\\$([0-9]+(?:\\.[0-9]+)?)", text)]
        if not values:
            return None, None, None
        low_val = min(values)
        high_val = max(values)
        avg_val = round((low_val + high_val) / 2, 2)
        return low_val, high_val, avg_val

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
