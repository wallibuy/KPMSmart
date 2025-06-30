"""
KPMS TRUST Complete Working Multi-Item Stationery Management System
Fully functional web application with multi-item cart, admin dashboard, and invoice generation
"""

import os
import sqlite3
import threading
import queue
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json

app = Flask(__name__)
app.secret_key = 'kpms_trust_secret_key_2025'

# Request processing queue
request_queue = queue.Queue()

def get_db_connection():
    """Get database connection with optimized settings"""
    conn = sqlite3.connect('kpms_categorized.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=1000')
    conn.execute('PRAGMA temp_store=memory')
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            store_name TEXT
        )
    ''')
    
    # Create items table with categories
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_level INTEGER NOT NULL DEFAULT 100
        )
    ''')
    
    # Create requests table with order_id for multi-item orders
    conn.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            store_id TEXT NOT NULL,
            store_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fulfilled_at TIMESTAMP,
            fulfilled_by TEXT
        )
    ''')
    
    # Create invoices table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            request_id INTEGER NOT NULL,
            store_id TEXT NOT NULL,
            store_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            pdf_filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin user
    try:
        conn.execute('''
            INSERT OR IGNORE INTO users (username, password, role, store_name)
            VALUES (?, ?, ?, ?)
        ''', ('admin', generate_password_hash('adminpass'), 'admin', 'Admin'))
    except:
        pass
    
    # Insert 31 store users
    store_names = [
        'SS PLAZA', 'SS CORNUBIA', 'SS WESTWOOD', 'SS GATEWAY', 'SS PAVILION',
        'SS MUSGRAVE', 'SS DURBAN NORTH', 'SS BALLITO', 'SS UMHLANGA', 'SS CHATSWORTH',
        'SS PHOENIX', 'SS PINETOWN', 'SS HILLCREST', 'SS KLOOF', 'SS GILLITTS',
        'SS WESTVILLE', 'SS DURBAN CENTRAL', 'SS POINT', 'SS BEREA', 'SS MORNINGSIDE',
        'SS GLENWOOD', 'SS OVERPORT', 'SS CLAIRWOOD', 'SS ISIPINGO', 'SS AMANZIMTOTI',
        'SS QUEENSBURGH', 'SS MALVERN', 'SS BELLAIR', 'SS WOODLANDS', 'SS SHALLCROSS',
        'SS UMLAZI'
    ]
    
    for i, store_name in enumerate(store_names, 1):
        try:
            conn.execute('''
                INSERT OR IGNORE INTO users (username, password, role, store_name)
                VALUES (?, ?, ?, ?)
            ''', (f'store{i:02d}', generate_password_hash('123'), 'store', store_name))
        except:
            continue
    
    # Insert categorized items
    items_data = [
        # Stationery Items (18)
        ('Cello Tape', 'Stationery', 12.00, 50),
        ('Scissors', 'Stationery', 25.00, 30),
        ('Stapler', 'Stationery', 45.00, 25),
        ('Calculator', 'Stationery', 85.00, 15),
        ('Markers', 'Stationery', 35.00, 40),
        ('Blue Pens', 'Stationery', 10.00, 100),
        ('Red Pens', 'Stationery', 10.00, 100),
        ('Black Pens', 'Stationery', 10.00, 100),
        ('Files', 'Stationery', 8.00, 75),
        ('Folders', 'Stationery', 6.00, 80),
        ('Paper', 'Stationery', 65.00, 200),
        ('Notebooks', 'Stationery', 15.00, 60),
        ('Highlighters', 'Stationery', 18.00, 45),
        ('Rubber Bands', 'Stationery', 12.00, 35),
        ('Paper Clips', 'Stationery', 8.00, 50),
        ('Sticky Notes', 'Stationery', 22.00, 40),
        ('Rulers', 'Stationery', 14.00, 30),
        ('Erasers', 'Stationery', 5.00, 60),
        
        # Stock Items (5)
        ('Lens Cloths Black', 'Stock', 8.00, 100),
        ('Lens Cloths Blue', 'Stock', 8.00, 100),
        ('Tissue', 'Stock', 15.00, 80),
        ('Alcohol Swabs', 'Stock', 25.00, 75),
        ('Cleaning Wipes', 'Stock', 18.00, 60),
        
        # Tech Items (6)
        ('Flash Drives', 'Tech', 65.00, 40),
        ('Monitors', 'Tech', 1250.00, 8),
        ('Keyboards', 'Tech', 180.00, 15),
        ('Mouse', 'Tech', 120.00, 20),
        ('HDMI Cables', 'Tech', 85.00, 25),
        ('Power Supply', 'Tech', 450.00, 10)
    ]
    
    for item_name, category, price, stock in items_data:
        try:
            conn.execute('''
                INSERT OR IGNORE INTO items (name, category, price, stock_level)
                VALUES (?, ?, ?, ?)
            ''', (item_name, category, price, stock))
        except:
            continue
    
    conn.commit()
    conn.close()

def process_request_queue():
    """Background thread to process requests"""
    while True:
        try:
            request_data = request_queue.get(timeout=1)
            if request_data:
                process_fulfill_request(request_data)
                request_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Queue processing error: {e}")

def process_fulfill_request(request_data):
    """Process fulfill request for complete orders (single or multi-item)"""
    request_id, username = request_data
    
    conn = get_db_connection()
    try:
        # Get request details to find if it's part of a multi-item order
        request_info = conn.execute('''
            SELECT * FROM requests WHERE id = ? AND status = 'pending'
        ''', (request_id,)).fetchone()
        
        if not request_info:
            return
            
        order_id = request_info['order_id']
        
        if order_id:
            # Multi-item order - fulfill all items in the order
            order_items = conn.execute('''
                SELECT * FROM requests WHERE order_id = ? AND status = 'pending'
            ''', (order_id,)).fetchall()
            
            # Update all items in the order
            for item in order_items:
                conn.execute('''
                    UPDATE requests 
                    SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP, fulfilled_by = ?
                    WHERE id = ?
                ''', (username, item['id']))
                
                # Update stock
                conn.execute('''
                    UPDATE items 
                    SET stock_level = stock_level - ?
                    WHERE name = ?
                ''', (item['quantity'], item['item_name']))
            
            conn.commit()
            
            # Generate combined invoice for the entire order
            generate_combined_invoice_for_order(order_id)
            
        else:
            # Single item request - fulfill just this one
            conn.execute('''
                UPDATE requests 
                SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP, fulfilled_by = ?
                WHERE id = ?
            ''', (username, request_id))
            
            # Update stock
            conn.execute('''
                UPDATE items 
                SET stock_level = stock_level - ?
                WHERE name = ?
            ''', (request_info['quantity'], request_info['item_name']))
            
            conn.commit()
            
            # Generate single item invoice
            generate_invoice_for_request(request_id)
            
    except Exception as e:
        print(f"Error processing fulfill request: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_invoice_for_request(request_id):
    """Generate PDF invoice for fulfilled request"""
    try:
        conn = get_db_connection()
        
        # Get request details with store information
        request_data = conn.execute('''
            SELECT r.*, u.store_name as full_store_name 
            FROM requests r
            JOIN users u ON r.store_id = u.username
            WHERE r.id = ?
        ''', (request_id,)).fetchone()
        
        if not request_data:
            conn.close()
            return None
        
        # Generate invoice ID
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create invoices directory
        os.makedirs('invoices', exist_ok=True)
        
        # Generate PDF
        pdf_filename = f"invoice_{invoice_id}.pdf"
        pdf_path = os.path.join('invoices', pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        header_style = styles['Heading1']
        header_style.alignment = 1  # Center
        story.append(Paragraph("KPMS TRUST", header_style))
        story.append(Paragraph("STATIONERY SUPPLY INVOICE", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Invoice details
        invoice_data = [
            ['Invoice ID:', invoice_id],
            ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Store:', request_data['full_store_name']],
            ['Request ID:', str(request_data['id'])]
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*72, 4*72])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 20))
        
        # Items table
        items_data = [
            ['Item', 'Category', 'Quantity', 'Unit Price', 'Total']
        ]
        items_data.append([
            request_data['item_name'],
            request_data['item_category'],
            str(request_data['quantity']),
            f"R{request_data['unit_price']:.2f}",
            f"R{request_data['total_price']:.2f}"
        ])
        
        items_table = Table(items_data, colWidths=[2.5*72, 1.5*72, 1*72, 1*72, 1*72])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(Paragraph("Thank you for your business!", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Save invoice record
        conn.execute('''
            INSERT INTO invoices (invoice_id, request_id, store_id, store_name, 
                                 item_name, item_category, quantity, unit_price, 
                                 total_price, pdf_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_id, request_data['id'], request_data['store_id'], 
              request_data['store_name'], request_data['item_name'], 
              request_data['item_category'], request_data['quantity'], 
              request_data['unit_price'], request_data['total_price'], pdf_filename))
        
        conn.commit()
        conn.close()
        
        return invoice_id
        
    except Exception as e:
        print(f"Error generating invoice: {e}")
        return None

def generate_combined_invoice_for_order(order_id):
    """Generate combined PDF invoice for multi-item order"""
    try:
        conn = get_db_connection()
        
        # Get all items in the order
        order_items = conn.execute('''
            SELECT r.*, u.store_name as full_store_name 
            FROM requests r
            JOIN users u ON r.store_id = u.username
            WHERE r.order_id = ?
            ORDER BY r.item_name
        ''', (order_id,)).fetchall()
        
        if not order_items:
            conn.close()
            return None
        
        # Use first item for order details
        first_item = order_items[0]
        
        # Generate invoice ID
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create invoices directory
        os.makedirs('invoices', exist_ok=True)
        
        # Generate PDF
        pdf_filename = f"invoice_{invoice_id}.pdf"
        pdf_path = os.path.join('invoices', pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        header_style = styles['Heading1']
        header_style.alignment = 1  # Center
        story.append(Paragraph("KPMS TRUST", header_style))
        story.append(Paragraph("STATIONERY SUPPLY INVOICE", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Calculate totals
        total_quantity = sum(item['quantity'] for item in order_items)
        total_amount = sum(item['total_price'] for item in order_items)
        
        # Invoice details
        invoice_data = [
            ['Invoice ID:', invoice_id],
            ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Store:', first_item['full_store_name']],
            ['Order ID:', order_id],
            ['Total Items:', f"{len(order_items)} types, {total_quantity} units"]
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*72, 4*72])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 20))
        
        # Items table header
        items_data = [
            ['Item', 'Category', 'Quantity', 'Unit Price', 'Total']
        ]
        
        # Add all items
        for item in order_items:
            items_data.append([
                item['item_name'],
                item['item_category'],
                str(item['quantity']),
                f"R{item['unit_price']:.2f}",
                f"R{item['total_price']:.2f}"
            ])
        
        # Add total row
        items_data.append([
            'TOTAL', '', str(total_quantity), '', f"R{total_amount:.2f}"
        ])
        
        items_table = Table(items_data, colWidths=[2.5*72, 1.5*72, 1*72, 1*72, 1*72])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(Paragraph("Thank you for your business!", styles['Normal']))
        story.append(Paragraph(f"Multi-item Order: {order_id}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Save one combined invoice record for the order
        total_quantity = sum(item['quantity'] for item in order_items)
        total_amount = sum(item['total_price'] for item in order_items)
        first_item = order_items[0]
        
        conn.execute('''
            INSERT INTO invoices (invoice_id, request_id, store_id, store_name, 
                                 item_name, item_category, quantity, unit_price, 
                                 total_price, pdf_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_id, first_item['id'], first_item['store_id'], 
              first_item['store_name'], f"Multi-item Order ({len(order_items)} items)", 
              "Mixed", total_quantity, 0, total_amount, pdf_filename))
        
        conn.commit()
        conn.close()
        
        return invoice_id
        
    except Exception as e:
        print(f"Error generating combined invoice: {e}")
        return None

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('store_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['store_name'] = user['store_name']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('store_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/store_dashboard')
def store_dashboard():
    if 'user_id' not in session or session.get('role') != 'store':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get items by category
    items = conn.execute('SELECT * FROM items ORDER BY category, name').fetchall()
    
    # Get recent requests
    recent_requests = conn.execute('''
        SELECT * FROM requests 
        WHERE store_id = ? 
        ORDER BY requested_at DESC 
        LIMIT 10
    ''', (session['username'],)).fetchall()
    
    conn.close()
    
    return render_template('store_dashboard.html', 
                         items=items, 
                         requests=recent_requests,
                         store_name=session['store_name'])

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get all requests grouped by order_id for multi-item orders
    requests = conn.execute('''
        SELECT r.*, 
               CASE WHEN r.order_id IS NOT NULL 
                    THEN (SELECT COUNT(*) FROM requests WHERE order_id = r.order_id)
                    ELSE 1 
               END as order_item_count,
               CASE WHEN r.order_id IS NOT NULL 
                    THEN (SELECT SUM(total_price) FROM requests WHERE order_id = r.order_id)
                    ELSE r.total_price 
               END as order_total
        FROM requests r
        ORDER BY r.requested_at DESC
    ''').fetchall()
    
    # Get statistics
    total_requests = conn.execute('SELECT COUNT(*) FROM requests').fetchone()[0]
    pending_requests = conn.execute('SELECT COUNT(*) FROM requests WHERE status = "pending"').fetchone()[0]
    fulfilled_requests = conn.execute('SELECT COUNT(*) FROM requests WHERE status = "fulfilled"').fetchone()[0]
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         requests=requests,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         fulfilled_requests=fulfilled_requests)

@app.route('/inventory')
def inventory():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY category, name').fetchall()
    conn.close()
    
    return render_template('inventory.html', items=items)

@app.route('/update_item/<int:item_id>', methods=['POST'])
def update_item(item_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    unit_price = float(request.form.get('unit_price'))
    stock_level = int(request.form.get('stock_level'))
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE items 
        SET price = ?, stock_level = ?
        WHERE id = ?
    ''', (unit_price, stock_level, item_id))
    conn.commit()
    conn.close()
    
    flash('Item updated successfully', 'success')
    return redirect(url_for('inventory'))

@app.route('/submit_request', methods=['POST'])
def submit_request():
    if 'user_id' not in session or session.get('role') != 'store':
        return redirect(url_for('login'))
    
    try:
        # Get form data
        item_name = request.form.get('item_name')
        quantity = int(request.form.get('quantity', 0))
        
        if not item_name or quantity <= 0:
            flash('Please select an item and enter a valid quantity', 'error')
            return redirect(url_for('store_dashboard'))
        
        conn = get_db_connection()
        
        # Get item details by name
        item = conn.execute('SELECT * FROM items WHERE name = ?', (item_name,)).fetchone()
        
        if item:
            total_price = item['price'] * quantity
            
            # Insert request
            conn.execute('''
                INSERT INTO requests (store_id, store_name, item_name, item_category, 
                                    quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session['username'], session['store_name'], item['name'], 
                  item['category'], quantity, item['price'], total_price))
            
            conn.commit()
            flash('Request submitted successfully!', 'success')
        else:
            flash('Item not found', 'error')
        
        conn.close()
        
    except ValueError:
        flash('Please enter a valid quantity', 'error')
    except Exception as e:
        flash(f'Error submitting request: {str(e)}', 'error')
    
    return redirect(url_for('store_dashboard'))

@app.route('/submit_multi_request', methods=['POST'])
def submit_multi_request():
    if 'user_id' not in session or session.get('role') != 'store':
        return redirect(url_for('login'))
    
    try:
        import json
        import uuid
        
        # Get cart data
        cart_data = request.form.get('cart_data')
        if not cart_data:
            flash('No items in cart', 'error')
            return redirect(url_for('store_dashboard'))
        
        cart_items = json.loads(cart_data)
        if not cart_items:
            flash('Cart is empty', 'error')
            return redirect(url_for('store_dashboard'))
        
        # Generate unique order ID
        order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        
        conn = get_db_connection()
        
        # Insert all items with the same order_id
        for item in cart_items:
            conn.execute('''
                INSERT INTO requests (order_id, store_id, store_name, item_name, item_category, 
                                    quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, session['username'], session['store_name'], 
                  item['name'], item['category'], item['quantity'], 
                  item['unit_price'], item['total_price']))
        
        conn.commit()
        conn.close()
        
        flash(f'Multi-item order submitted successfully! Order ID: {order_id}', 'success')
        
    except Exception as e:
        flash(f'Error submitting order: {str(e)}', 'error')
    
    return redirect(url_for('store_dashboard'))

@app.route('/fulfill_request/<int:request_id>', methods=['POST'])
def fulfill_request(request_id):
    """Fulfill complete order immediately (handles multi-item orders)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Process immediately instead of queueing
    try:
        process_fulfill_request((request_id, session['username']))
        flash('Order fulfilled successfully! Invoice generated.', 'success')
    except Exception as e:
        flash(f'Error fulfilling order: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/unfulfill_request/<int:request_id>', methods=['POST'])
def unfulfill_request(request_id):
    """Mark a fulfilled request back to pending and restore stock"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get request details
    request_info = conn.execute('''
        SELECT * FROM requests WHERE id = ? AND status = 'fulfilled'
    ''', (request_id,)).fetchone()
    
    if request_info:
        # Update request status back to pending
        conn.execute('''
            UPDATE requests 
            SET status = 'pending', fulfilled_at = NULL, fulfilled_by = NULL
            WHERE id = ?
        ''', (request_id,))
        
        # Restore stock
        conn.execute('''
            UPDATE items 
            SET stock_level = stock_level + ?
            WHERE name = ?
        ''', (request_info['quantity'], request_info['item_name']))
        
        conn.commit()
        flash('Request marked as pending and stock restored', 'success')
    else:
        flash('Request not found or not fulfilled', 'error')
    
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/store_invoices')
def store_invoices():
    if 'user_id' not in session or session.get('role') != 'store':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    invoices = conn.execute('''
        SELECT * FROM invoices 
        WHERE store_id = ? 
        ORDER BY created_at DESC
    ''', (session['username'],)).fetchall()
    
    conn.close()
    
    return render_template('store_invoices.html', invoices=invoices)

@app.route('/download_invoice/<invoice_id>')
def download_invoice(invoice_id):
    """Download invoice PDF with comprehensive error handling"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    print(f"DEBUG: Download request for invoice_id: {invoice_id}")
    print(f"DEBUG: User: {session.get('username')}, Role: {session.get('role')}")
    
    conn = get_db_connection()
    
    # Get invoice details
    invoice = conn.execute('''
        SELECT * FROM invoices WHERE invoice_id = ?
    ''', (invoice_id,)).fetchone()
    
    if not invoice:
        conn.close()
        flash('Invoice not found', 'error')
        return redirect(url_for('store_invoices'))
    
    # Check access permissions
    if session.get('role') == 'store' and invoice['store_id'] != session.get('username'):
        conn.close()
        flash('Access denied', 'error')
        return redirect(url_for('store_invoices'))
    
    conn.close()
    
    # Find the PDF file
    pdf_filename = invoice['pdf_filename']
    pdf_path = os.path.join('invoices', pdf_filename)
    
    print(f"DEBUG: Checking direct path: {pdf_path}")
    
    if os.path.exists(pdf_path):
        print(f"DEBUG: File exists at {pdf_path}")
        
        # Verify file is readable
        try:
            with open(pdf_path, 'rb') as f:
                first_bytes = f.read(10)
                print(f"DEBUG: File readable, first 10 bytes: {first_bytes}")
        except Exception as e:
            print(f"DEBUG: File read error: {e}")
            flash('File read error', 'error')
            return redirect(url_for('store_invoices'))
        
        # Get absolute path for send_file
        abs_path = os.path.abspath(pdf_path)
        print(f"DEBUG: Absolute path: {abs_path}")
        
        try:
            file_size = os.path.getsize(abs_path)
            print(f"DEBUG: Sending response with {file_size} bytes")
            return send_file(abs_path, as_attachment=True, download_name=pdf_filename)
        except Exception as e:
            print(f"DEBUG: Send file error: {e}")
            flash('Error sending file', 'error')
            return redirect(url_for('store_invoices'))
    else:
        print(f"DEBUG: File not found at {pdf_path}")
        flash('Invoice file not found', 'error')
        return redirect(url_for('store_invoices'))

# API Routes
@app.route('/api/items')
def api_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY category, name').fetchall()
    conn.close()
    
    return jsonify([{
        'id': item['id'],
        'name': item['name'],
        'category': item['category'],
        'price': item['price'],
        'stock_level': item['stock_level']
    } for item in items])

@app.route('/api/items/<category>')
def api_items_by_category(category):
    conn = get_db_connection()
    items = conn.execute(
        'SELECT * FROM items WHERE category = ? ORDER BY name', 
        (category,)
    ).fetchall()
    conn.close()
    
    return jsonify([{
        'id': item['id'],
        'name': item['name'],
        'category': item['category'],
        'price': item['price'],
        'stock_level': item['stock_level']
    } for item in items])

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start background processing thread
    processing_thread = threading.Thread(target=process_request_queue, daemon=True)
    processing_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)