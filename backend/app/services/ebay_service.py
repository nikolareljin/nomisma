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
        self.paypal_email = os.getenv("EBAY_PAYPAL_EMAIL")
        self.postal_code = os.getenv("EBAY_POSTAL_CODE", "95125")
        self.location = os.getenv("EBAY_LOCATION", "San Jose, CA")
        self.country = os.getenv("EBAY_COUNTRY", "US")
        self.site = os.getenv("EBAY_SITE", "US")
        self.shipping_service = os.getenv("EBAY_SHIPPING_SERVICE", "USPSMedia")
        self.shipping_cost = os.getenv("EBAY_SHIPPING_COST", "2.50")
        self.listing_duration = os.getenv("EBAY_LISTING_DURATION", "Days_7")
        self.dispatch_time_max = os.getenv("EBAY_DISPATCH_TIME_MAX", "3")
        self.default_condition_id = os.getenv("EBAY_CONDITION_ID", "3000")
        
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

        title = (listing_data.get("listing_title") or "").strip()
        if not title:
            return {"success": False, "error": "Listing title is required"}
        if len(title) > 80:
            title = title[:80]

        description = (listing_data.get("listing_description") or "").strip()
        if not description:
            return {"success": False, "error": "Listing description is required"}

        start_price = listing_data.get("starting_price")
        if start_price is None:
            return {"success": False, "error": "Starting price is required"}

        buy_it_now_price = listing_data.get("buy_it_now_price")
        listing_type = "FixedPriceItem" if buy_it_now_price else "Chinese"
        call_name = "AddFixedPriceItem" if buy_it_now_price else "AddItem"

        payment_methods = listing_data.get("payment_methods") or ["PayPal"]
        paypal_email = listing_data.get("paypal_email") or self.paypal_email
        if "PayPal" in payment_methods and not paypal_email:
            return {
                "success": False,
                "error": "EBAY_PAYPAL_EMAIL is required when using PayPal"
            }
        
        try:
            # Prepare listing
            item = {
                "Item": {
                    "Title": title,
                    "Description": description,
                    "PrimaryCategory": {"CategoryID": "11116"},  # Coins: US category
                    "StartPrice": start_price,
                    "CategoryMappingAllowed": "true",
                    "Country": self.country,
                    "Currency": "USD",
                    "DispatchTimeMax": self.dispatch_time_max,
                    "ListingDuration": self.listing_duration,
                    "ListingType": listing_type,
                    "PaymentMethods": payment_methods,
                    "PostalCode": self.postal_code,
                    "Location": self.location,
                    "Quantity": "1",
                    "ConditionID": listing_data.get("condition_id") or self.default_condition_id,
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
                            "ShippingService": listing_data.get("shipping_service") or self.shipping_service,
                            "ShippingServiceCost": listing_data.get("shipping_cost") or self.shipping_cost
                        }
                    },
                    "Site": self.site
                }
            }

            if "PayPal" in payment_methods and paypal_email:
                item["Item"]["PayPalEmailAddress"] = paypal_email

            if buy_it_now_price:
                item["Item"]["BuyItNowPrice"] = buy_it_now_price

            image_urls = listing_data.get("image_urls") or []
            if image_urls:
                item["Item"]["PictureDetails"] = {"PictureURL": image_urls}
            
            # Add listing
            response = self.api.execute(call_name, item)
            
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
