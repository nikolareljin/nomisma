# eBay Integration Guide

This guide explains how to set up and use eBay API integration for listing coins on eBay Marketplace.

## Prerequisites

- eBay account (seller account recommended)
- eBay Developer Account
- Verified PayPal account (for receiving payments)

## Step 1: Register as eBay Developer

1. Go to https://developer.ebay.com/
2. Click "Register" or "Join"
3. Sign in with your eBay account
4. Accept the API License Agreement
5. Complete your developer profile

## Step 2: Create an Application

1. Navigate to https://developer.ebay.com/my/keys
2. Click "Create a keyset" or "Create an App"
3. Choose application type:
   - **Sandbox** for testing (recommended to start)
   - **Production** for live listings
4. Fill in application details:
   - Application Title: "Nomisma Coin Cataloging"
   - Application Description: "Coin analysis and listing automation"

## Step 3: Get API Credentials

After creating your application, you'll receive:

- **App ID (Client ID)**: Your application identifier
- **Dev ID**: Developer identifier
- **Cert ID (Client Secret)**: Secret key for authentication

**Important**: Keep these credentials secure and never share them publicly.

## Step 4: Generate User Token

### For Sandbox (Testing):

1. Go to https://developer.ebay.com/my/auth/?env=sandbox
2. Click "Get a User Token"
3. Sign in with your **sandbox** eBay account
4. Grant permissions to your application
5. Copy the generated token

### For Production:

1. Go to https://developer.ebay.com/my/auth/?env=production
2. Follow the OAuth 2.0 flow
3. Generate a production user token

**Note**: User tokens expire. You'll need to implement OAuth 2.0 refresh flow for production use.

## Step 5: Configure Nomisma

1. Open your `.env` file:
   ```bash
   nano /home/nikos/Projects/nomisma/.env
   ```

2. Add your eBay credentials:
   ```env
   EBAY_APP_ID=your_app_id_here
   EBAY_DEV_ID=your_dev_id_here
   EBAY_CERT_ID=your_cert_id_here
   EBAY_USER_TOKEN=your_user_token_here
   EBAY_ENVIRONMENT=sandbox  # or 'production'
   ```

3. Save and restart the application:
   ```bash
   docker-compose restart backend
   ```

## Step 6: Test the Integration

1. Open Nomisma: http://localhost:3000
2. Navigate to a coin's detail page
3. Click "List on eBay"
4. Review the pre-populated listing information
5. Click "Create Listing"

### Verify in eBay Sandbox

1. Go to https://sandbox.ebay.com
2. Sign in with your sandbox seller account
3. Navigate to "My eBay" > "Selling"
4. Verify your listing appears

## Creating Effective Listings

### Title Best Practices

- Include key information: Year, Country, Denomination, Condition
- Use relevant keywords for searchability
- Stay within 80 character limit
- Example: "1943-D Steel Wheat Penny - Very Fine Condition - Wartime Coin"

### Description Tips

- Provide detailed condition information
- Mention any defects or notable features
- Include grading information if available
- Reference AI analysis results
- Add historical context if relevant

### Pricing Strategy

- Use AI valuation as a starting point
- Research completed listings for similar coins
- Consider:
  - Condition grade
  - Rarity
  - Market demand
  - Current metal prices (for bullion)
- Set competitive starting price
- Use Buy It Now for faster sales

### Images

- Nomisma automatically includes coin images
- Ensure high-quality, clear photos
- Show both obverse and reverse
- Include close-ups of notable features or defects

## Listing Categories

Common eBay categories for coins:

- **11116**: Coins: US
- **45086**: Coins: World
- **3452**: Coins: Ancient
- **39619**: Coins: Medieval
- **4733**: Bullion

The application defaults to "Coins: US" but you can modify this in the code.

## Managing Listings

### Check Listing Status

Use the API to check listing status:

```http
GET /api/ebay/status/{item_id}
```

Or view in eBay:
- Sandbox: https://sandbox.ebay.com
- Production: https://www.ebay.com

### Update Listings

Currently, listings must be updated through eBay's interface. Future versions may support programmatic updates.

### End Listings

End listings early through eBay's "My eBay" > "Selling" interface.

## Troubleshooting

### "Invalid Credentials" Error

**Problem**: API returns authentication error

**Solutions**:
1. Verify all credentials in `.env` are correct
2. Ensure no extra spaces in credential values
3. Check that you're using the right environment (sandbox vs production)
4. Regenerate user token if expired

### "Category Not Allowed" Error

**Problem**: Selected category doesn't accept your item

**Solutions**:
1. Verify category ID is correct
2. Check eBay's category requirements
3. Use eBay's category browser to find appropriate category

### "Token Expired" Error

**Problem**: User token has expired

**Solutions**:
1. Generate a new user token
2. Update `.env` with new token
3. Restart backend: `docker-compose restart backend`
4. For production, implement OAuth 2.0 refresh flow

### Listing Not Appearing

**Problem**: Listing created but not visible on eBay

**Solutions**:
1. Check you're looking in the right environment (sandbox vs production)
2. Verify listing status via API
3. Check eBay account for any holds or restrictions
4. Review eBay seller requirements

## Production Checklist

Before going live with production listings:

- [ ] Test thoroughly in sandbox environment
- [ ] Verify PayPal account is connected
- [ ] Review eBay seller requirements and policies
- [ ] Set up return policy
- [ ] Configure shipping options
- [ ] Add payment methods
- [ ] Verify tax settings
- [ ] Test with low-value items first
- [ ] Monitor initial listings closely

## API Limits and Fees

### API Call Limits

- Sandbox: 5,000 calls per day
- Production: Varies by subscription level
- Monitor usage in eBay Developer Portal

### eBay Fees

- Insertion fees: Vary by category and listing format
- Final value fees: Percentage of sale price
- Optional upgrade fees: Featured listings, etc.
- See: https://www.ebay.com/help/selling/fees-credits-invoices/selling-fees

## Advanced Features

### Bulk Listing

To list multiple coins:

1. Use the API directly:
   ```bash
   for coin_id in $(cat coin_ids.txt); do
     curl -X POST http://localhost:8000/api/ebay/list \
       -H "Content-Type: application/json" \
       -d "{\"coin_id\": \"$coin_id\", ...}"
   done
   ```

### Automated Repricing

Future feature: Automatically adjust prices based on market conditions.

### Listing Templates

Create templates for common coin types to speed up listing creation.

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables** for all sensitive data
3. **Rotate tokens regularly** in production
4. **Implement OAuth 2.0 refresh** for long-term use
5. **Monitor API usage** for unusual activity
6. **Use HTTPS** in production
7. **Limit token permissions** to only what's needed

## Resources

- eBay Developers Program: https://developer.ebay.com/
- API Documentation: https://developer.ebay.com/docs
- Sandbox: https://sandbox.ebay.com
- Seller Center: https://www.ebay.com/sh/ovw
- Community Forums: https://community.ebay.com/

## Support

For eBay API issues:
- Check eBay Developer Forums
- Review API documentation
- Contact eBay Developer Support

For Nomisma integration issues:
- Check application logs: `docker-compose logs backend`
- Review this documentation
- Verify credentials and configuration

## Future Enhancements

Planned features for eBay integration:

- OAuth 2.0 refresh token flow
- Bulk listing support
- Listing templates
- Automated repricing
- Sales tracking and analytics
- Inventory synchronization
- Multi-marketplace support (beyond eBay)
