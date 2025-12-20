from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class EbayService:
    """Service for eBay API integration"""
    
    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.dev_id = os.getenv("EBAY_DEV_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.token = os.getenv("EBAY_USER_TOKEN")
        self.environment = os.getenv("EBAY_ENVIRONMENT", "sandbox")
        
        self.api = None
        if all([self.app_id, self.dev_id, self.cert_id, self.token]):
            try:
                self.api = Trading(
                    domain='api.sandbox.ebay.com' if self.environment == 'sandbox' else 'api.ebay.com',
                    appid=self.app_id,
                    devid=self.dev_id,
                    certid=self.cert_id,
                    token=self.token,
                    config_file=None
                )
            except Exception as e:
                print(f"eBay API initialization error: {str(e)}")
    
    def create_listing(self, coin_data: Dict[str, Any], listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an eBay listing for a coin"""
        
        if not self.api:
            return self._mock_listing(coin_data, listing_data)
        
        try:
            # Prepare listing
            item = {
                "Item": {
                    "Title": listing_data.get("listing_title"),
                    "Description": listing_data.get("listing_description"),
                    "PrimaryCategory": {"CategoryID": "11116"},  # Coins: US category
                    "StartPrice": listing_data.get("starting_price"),
                    "CategoryMappingAllowed": "true",
                    "Country": "US",
                    "Currency": "USD",
                    "DispatchTimeMax": "3",
                    "ListingDuration": "Days_7",
                    "ListingType": "FixedPriceItem" if listing_data.get("buy_it_now_price") else "Chinese",
                    "PaymentMethods": "PayPal",
                    "PayPalEmailAddress": "seller@example.com",  # Should be configured
                    "PictureDetails": {
                        "PictureURL": []  # Add image URLs
                    },
                    "PostalCode": "95125",  # Should be configured
                    "Quantity": "1",
                    "ReturnPolicy": {
                        "ReturnsAcceptedOption": "ReturnsAccepted",
                        "RefundOption": "MoneyBack",
                        "ReturnsWithinOption": "Days_30",
                        "ShippingCostPaidByOption": "Buyer"
                    },
                    "ShippingDetails": {
                        "ShippingType": "Flat",
                        "ShippingServiceOptions": {
                            "ShippingServicePriority": "1",
                            "ShippingService": "USPSMedia",
                            "ShippingServiceCost": "2.50"
                        }
                    },
                    "Site": "US"
                }
            }
            
            if listing_data.get("buy_it_now_price"):
                item["Item"]["BuyItNowPrice"] = listing_data.get("buy_it_now_price")
            
            # Add listing
            response = self.api.execute('AddFixedPriceItem', item)
            
            return {
                "success": True,
                "item_id": response.reply.ItemID,
                "fees": response.reply.Fees,
                "start_time": response.reply.StartTime,
                "end_time": response.reply.EndTime,
                "response": response.dict()
            }
            
        except ConnectionError as e:
            return {
                "success": False,
                "error": str(e),
                "details": e.response.dict() if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_listing_status(self, item_id: str) -> Dict[str, Any]:
        """Get the status of an eBay listing"""
        
        if not self.api:
            return self._mock_status(item_id)
        
        try:
            response = self.api.execute('GetItem', {'ItemID': item_id})
            item = response.reply.Item
            
            return {
                "success": True,
                "item_id": item_id,
                "status": item.SellingStatus.ListingStatus,
                "current_price": float(item.SellingStatus.CurrentPrice.value),
                "quantity_sold": int(item.SellingStatus.QuantitySold),
                "view_count": int(item.HitCount) if hasattr(item, 'HitCount') else 0,
                "watchers": int(item.WatchCount) if hasattr(item, 'WatchCount') else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mock_listing(self, coin_data: Dict[str, Any], listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock listing creation for testing"""
        import random
        item_id = f"MOCK{random.randint(100000000000, 999999999999)}"
        
        return {
            "success": True,
            "item_id": item_id,
            "fees": {"ListingFee": "0.35"},
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "response": {"mock": True, "message": "No eBay API credentials configured"}
        }
    
    def _mock_status(self, item_id: str) -> Dict[str, Any]:
        """Mock status check for testing"""
        return {
            "success": True,
            "item_id": item_id,
            "status": "Active",
            "current_price": 10.00,
            "quantity_sold": 0,
            "view_count": 15,
            "watchers": 2
        }

# Global instance
ebay_service = EbayService()
