# Nomisma User Guide

Complete guide to using the Nomisma coin analysis and cataloging system.

## Getting Started

### Accessing the Application

After starting Nomisma with `./start`, open your web browser and navigate to:

```
http://localhost:3000
```

### Main Navigation

The application has four main sections:

1. **Dashboard** - Overview of your collection with statistics
2. **Scan Coin** - Capture and analyze new coins
3. **Collection** - Browse and search your cataloged coins

## Dashboard

The dashboard provides an at-a-glance view of your coin collection.

### Statistics Cards

- **Total Coins**: Number of coins in your collection
- **Total Value**: Combined estimated value of all coins
- **Scanned Today**: Coins added today
- **For Sale**: Coins marked for sale on eBay

### Quick Actions

- **Scan New Coin**: Jump directly to the scanning interface
- **Browse Collection**: View all your coins
- **Manage Listings**: See coins listed on eBay

### Recent Coins

View the 6 most recently added coins with:
- Inventory number (e.g., NOM-0001)
- Primary image
- Country and denomination
- Year
- Condition grade
- Estimated value

## Scanning a Coin

### Step 1: Capture

1. Click **Scan Coin** in the navigation
2. Select your microscope from the dropdown
3. Position the coin under the microscope
4. Adjust focus and lighting
5. Click **Capture Image**

**Tips**:
- Ensure the coin is centered in the frame
- Use adequate lighting for clear images
- Keep the coin flat and parallel to the lens

### Step 2: AI Analysis

The system automatically analyzes the captured image:

- Identifies country, denomination, and year
- Detects mint marks
- Assesses condition and wear
- Identifies defects or errors
- Estimates authenticity

This process takes 5-10 seconds.

### Step 3: Review and Edit

Review the AI-detected information:

- **Auto-filled fields**: Country, denomination, year, mint mark, composition, condition grade
- **Editable**: All fields can be modified
- **Additional fields**: Add notes, acquisition information, etc.

**Fields**:
- **Country**: Country of origin
- **Denomination**: Face value (e.g., "1 Cent", "Quarter Dollar")
- **Year**: Year minted
- **Mint Mark**: Letter indicating mint location (D, S, P, etc.)
- **Composition**: Metal content (e.g., "Copper", "Silver")
- **Condition Grade**: Condition from Poor to Uncirculated
- **Notes**: Any additional information

### Step 4: Save

Click **Save Coin** to add it to your collection.

The system will:
- Assign an inventory number (NOM-0001, NOM-0002, etc.)
- Store the image
- Save AI analysis results
- Generate a value estimate
- Redirect to the coin's detail page

## Browsing Your Collection

### List View

The Collection page shows all your coins in a grid or list format.

**Grid View**:
- Card-based layout
- Shows primary image
- Displays key information
- Click any coin to view details

**List View**:
- Compact table format
- Shows thumbnail, inventory number, and details
- Sortable columns
- Ideal for large collections

### Search and Filter

**Search Bar**:
- Search by inventory number, country, denomination, or notes
- Real-time results as you type
- Searches across all text fields

**Filters**:
- **Country**: Filter by country of origin
- **Condition**: Filter by condition grade
- **Year Range**: Set minimum and maximum years
- **For Sale**: Show only coins marked for sale

**Sorting**:
- Sort by date added, year, country, or value
- Ascending or descending order

## Coin Details

Click any coin to view its complete information.

### Images

- View all captured images
- Obverse (front), reverse (back), edge, and detail shots
- Click to enlarge
- Zoom and pan for close inspection

### Information Sections

**Basic Details**:
- Inventory number
- Country, denomination, year
- Mint mark, composition
- Weight and diameter
- Condition grade
- Catalog number
- Personal notes

**AI Analysis**:
- Authenticity assessment with confidence level
- Wear level and surface quality
- Strike quality and luster rating
- Detected defects
- Identified errors

**Valuation**:
- Estimated value range (low, average, high)
- Rarity score
- Market demand indicator
- Confidence level
- Valuation date

**Similar Coins**:
- Other coins in your collection with similar characteristics
- Useful for comparison and valuation
- Click to view similar coin details

### Actions

**Edit**:
1. Click **Edit** button
2. Modify any fields
3. Click **Save** to update

**List on eBay**:
1. Click **List on eBay**
2. Review pre-populated listing information
3. Adjust title, description, and pricing
4. Click **Create Listing**

**Delete**:
1. Scroll to "Danger Zone"
2. Click **Delete Coin**
3. Confirm deletion
4. Coin and all associated data will be permanently removed

## eBay Listing

### Creating a Listing

From a coin's detail page:

1. Click **List on eBay**
2. Review the listing modal:
   - **Title**: Auto-generated from coin data (editable, 80 char max)
   - **Description**: Detailed description with condition and notes
   - **Starting Price**: Based on low estimate
   - **Buy It Now Price**: Based on average estimate

3. Edit as needed
4. Click **Create Listing**

### Listing Status

After creating a listing:
- Listing appears on eBay (sandbox or production)
- Coin is marked as "For Sale"
- Track views, watchers, and bids through eBay

### Managing Listings

- View all listings in eBay's Seller Hub
- Update prices and descriptions through eBay
- End listings early if needed
- Mark as sold when transaction completes

## Inventory Management

### Inventory Numbers

Each coin receives a unique inventory number:
- Format: `NOM-0001`, `NOM-0002`, etc.
- Auto-generated sequentially
- Never reused
- Searchable

**Uses**:
- Label physical storage containers
- Reference in conversations
- Track coins across systems
- Organize inventory

### Organization Tips

1. **Physical Storage**:
   - Label containers with inventory numbers
   - Store coins in protective holders
   - Keep similar coins together
   - Maintain consistent organization

2. **Digital Organization**:
   - Use consistent naming for conditions
   - Add detailed notes for special coins
   - Tag coins with custom categories (future feature)
   - Regular backups of database

3. **Valuation Tracking**:
   - Re-run valuations periodically
   - Track market trends
   - Update acquisition prices
   - Monitor eBay sold listings

## Best Practices

### Image Capture

- **Multiple Angles**: Capture obverse, reverse, and edge
- **Detail Shots**: Close-ups of interesting features
- **Consistent Lighting**: Use same setup for all coins
- **High Resolution**: Use maximum camera resolution
- **Clean Coins**: Gently clean if appropriate (research first!)

### Data Entry

- **Accuracy**: Verify AI-detected information
- **Completeness**: Fill in all relevant fields
- **Notes**: Add context, provenance, or special features
- **Consistency**: Use standard terminology

### Valuation

- **Regular Updates**: Re-estimate values periodically
- **Market Research**: Compare with recent sales
- **Condition Matters**: Accurate grading affects value
- **Multiple Sources**: Don't rely solely on AI estimates

### Security

- **Backups**: Regular database backups
- **Privacy**: Don't share sensitive information publicly
- **Insurance**: Consider insuring valuable collections
- **Documentation**: Keep purchase receipts and certificates

## Keyboard Shortcuts

(Future feature - not yet implemented)

- `Ctrl+N`: New coin scan
- `Ctrl+F`: Focus search
- `Ctrl+S`: Save current edit
- `Esc`: Close modals

## Troubleshooting

### Can't Connect to Microscope

- Check USB connection
- Verify camera permissions
- Restart Docker containers
- See [Microscope Setup Guide](MICROSCOPE_SETUP.md)

### AI Analysis Fails

- Verify Gemini API key in `.env`
- Check API quota limits
- Ensure image is clear and well-lit
- Try capturing image again

### Slow Performance

- Check Docker container resources
- Optimize database (future feature)
- Clear browser cache
- Restart application

### Data Not Saving

- Check backend logs: `./log -t backend`
- Verify database connection
- Ensure sufficient disk space
- Check for error messages

## Tips and Tricks

1. **Batch Scanning**: Prepare multiple coins before starting to scan efficiently
2. **Lighting Setup**: Create a consistent lighting setup for best results
3. **Grading Reference**: Keep a grading guide handy for accurate condition assessment
4. **Market Research**: Check eBay sold listings for realistic valuations
5. **Backup Regularly**: Export data periodically (future feature)
6. **Clean Workspace**: Keep microscope and coins clean for best image quality

## Getting Help

- **Documentation**: Check docs folder for detailed guides
- **Logs**: Review application logs for error messages (`./log -t backend`)
- **Community**: Join numismatic forums for coin-specific questions
- **Support**: Open issues on GitHub for bugs or feature requests

## Future Features

Planned enhancements:

- Custom tags and categories
- Export to CSV/Excel
- Bulk operations
- Advanced reporting
- Mobile app
- Cloud sync
- Multi-user support
- Automated market tracking
