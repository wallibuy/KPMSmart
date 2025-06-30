# KPMS TRUST - Complete Multi-Item Stationery Management System

## Overview

This is a fully functional web application for KPMS TRUST stationery management, featuring multi-item shopping cart functionality, admin dashboard, and comprehensive invoice generation. The system handles 31 store locations with categorized inventory management.

## Features

### ✅ Multi-Item Shopping Cart System
- **Store Interface**: Add multiple items to cart before submitting as a single order
- **Category-based Selection**: Items organized into Stationery, Stock, and Tech categories
- **Real-time Cart Management**: Add, remove, and modify items before submission
- **Combined Orders**: Multiple items submitted together with unique order IDs

### ✅ Admin Dashboard
- **Order Management**: View and fulfill complete multi-item orders
- **Inventory Control**: Edit item prices and stock levels
- **Statistics Overview**: Track pending, fulfilled, and total requests
- **Comprehensive Reporting**: See all orders with detailed breakdowns

### ✅ Professional Invoice Generation
- **Single Item Invoices**: Individual PDF invoices for single requests
- **Combined Invoices**: Multi-item orders generate comprehensive invoices showing all items
- **PDF Downloads**: Store users can download their invoices directly
- **Detailed Breakdown**: Complete item listing with totals and order IDs

### ✅ Complete Inventory System
- **29 Actual Items**: Your real stationery, stock, and tech items with accurate pricing
- **Stock Level Tracking**: Live stock quantity displays and low stock warnings
- **Category Organization**: Items properly categorized for easy selection
- **Price Management**: Admin can update prices and stock levels

## System Structure

```
KPMS_Complete_Working_System/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── store_dashboard.html    # Store interface with cart
│   ├── admin_dashboard.html    # Admin management interface
│   ├── inventory.html    # Inventory management
│   └── store_invoices.html     # Invoice viewing
└── static/              # CSS and JavaScript
    ├── style.css        # Application styles
    └── app.js          # Shopping cart and UI functionality
```

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation & Setup

1. **Extract and navigate to the folder:**
   ```bash
   cd KPMS_Complete_Working_System
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the system:**
   - Open your browser to: `http://localhost:5000`
   - The application will automatically create the database and load all your inventory items

### Login Credentials

**Admin Access:**
- Username: `admin`
- Password: `adminpass`

**Store Access (31 stores):**
- Username: `store01` to `store31`
- Password: `123`
- Store names: SS PLAZA, SS CORNUBIA, SS WESTWOOD, etc.

## How to Use

### For Store Users:

1. **Login** with your store credentials (store01-31 / 123)
2. **Select Category** (Stationery, Stock, or Tech)
3. **Choose Items** from the dropdown (shows price and stock level)
4. **Add to Cart** - build your complete order
5. **Submit Order** - all items submitted together with one order ID
6. **View Invoices** - check your invoices after admin fulfillment

### For Admin Users:

1. **Login** with admin credentials (admin / adminpass)
2. **View Dashboard** - see all pending and fulfilled orders
3. **Fulfill Orders** - process complete multi-item orders with one click
4. **Manage Inventory** - update prices and stock levels
5. **Monitor Statistics** - track system usage and fulfillment rates

## Technical Features

### Multi-Item Cart System
- JavaScript-powered shopping cart with persistence
- Real-time total calculations
- Category-based item filtering
- Stock level warnings

### Advanced Order Processing
- Single and multi-item order support
- Automatic invoice generation upon fulfillment
- Combined PDF invoices for multi-item orders
- Comprehensive order tracking

### Database Design
- SQLite database with optimized performance
- Separate tables for users, items, requests, and invoices
- Order grouping with unique order IDs
- Complete audit trail

### Professional UI/UX
- Bootstrap 5 responsive design
- Font Awesome icons
- Real-time cart updates
- Modern, clean interface

## Inventory Items (29 Items)

### Stationery (18 items)
Cello Tape, Scissors, Stapler, Calculator, Markers, Blue Pens, Red Pens, Black Pens, Files, Folders, Paper, Notebooks, Highlighters, Rubber Bands, Paper Clips, Sticky Notes, Rulers, Erasers

### Stock (5 items)
Lens Cloths Black, Lens Cloths Blue, Tissue, Alcohol Swabs, Cleaning Wipes

### Tech (6 items)
Flash Drives, Monitors, Keyboards, Mouse, HDMI Cables, Power Supply

## Database Files
- `kpms_categorized.db` - Main application database
- `invoices/` - Generated PDF invoices (created automatically)

## System Requirements
- Python 3.7+
- 50MB free disk space
- Modern web browser
- Network access for Bootstrap/FontAwesome CDN

## Troubleshooting

**If the application doesn't start:**
1. Ensure Python 3.7+ is installed: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Check if port 5000 is available

**If items don't load:**
- The application automatically populates the database on first run
- Check browser console for JavaScript errors
- Ensure you're using a modern browser

**If invoices don't download:**
- Invoices are generated after admin fulfills orders
- Check that the `invoices/` directory has proper write permissions

## Production Deployment

For production use:
1. Use a production WSGI server (gunicorn, uWSGI)
2. Configure proper SSL/TLS
3. Use PostgreSQL or MySQL for the database
4. Set up proper backup procedures
5. Configure environment variables for secrets

## Support

This system is fully functional and includes:
- ✅ Multi-item shopping cart
- ✅ Complete order fulfillment workflow
- ✅ Professional PDF invoice generation
- ✅ Admin inventory management
- ✅ 31 store locations
- ✅ 29 actual inventory items
- ✅ Responsive modern interface

All features have been tested and verified to work correctly.