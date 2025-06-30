// KPMS TRUST - Complete Working System JavaScript

// Global variables
let cart = [];
let itemsData = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadAllItems();
    updateCartDisplay();
});

// Load all items from API
async function loadAllItems() {
    try {
        const response = await fetch('/api/items');
        if (response.ok) {
            itemsData = await response.json();
        } else {
            console.error('Failed to load items');
        }
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

// Load items by category
async function loadCategoryItems() {
    const categorySelect = document.getElementById('category');
    const itemSelect = document.getElementById('item_name');
    const selectedCategory = categorySelect.value;
    
    // Clear and disable item select
    itemSelect.innerHTML = '<option value="">Select an item</option>';
    itemSelect.disabled = true;
    
    if (!selectedCategory) {
        return;
    }
    
    try {
        const response = await fetch(`/api/items/${selectedCategory}`);
        if (response.ok) {
            const items = await response.json();
            
            // Populate item select
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.name;
                option.textContent = `${item.name} - R${item.price.toFixed(2)}`;
                option.dataset.price = item.price;
                option.dataset.category = item.category;
                option.dataset.stock = item.stock_level;
                itemSelect.appendChild(option);
            });
            
            itemSelect.disabled = false;
        } else {
            console.error('Failed to load category items');
        }
    } catch (error) {
        console.error('Error loading category items:', error);
    }
}

// Show item details (price and stock)
function showItemDetails() {
    const itemSelect = document.getElementById('item_name');
    const itemDetails = document.getElementById('itemDetails');
    const itemPrice = document.getElementById('itemPrice');
    const itemStock = document.getElementById('itemStock');
    
    const selectedOption = itemSelect.options[itemSelect.selectedIndex];
    
    if (!selectedOption.value) {
        itemDetails.style.display = 'none';
        return;
    }
    
    const price = parseFloat(selectedOption.dataset.price);
    const stock = parseInt(selectedOption.dataset.stock);
    
    itemPrice.textContent = `R${price.toFixed(2)}`;
    itemStock.textContent = `${stock} units`;
    
    // Add color coding for stock levels
    if (stock <= 5) {
        itemStock.className = 'fw-bold text-danger';
        itemStock.textContent += ' (Low Stock!)';
    } else if (stock <= 15) {
        itemStock.className = 'fw-bold text-warning';
        itemStock.textContent += ' (Medium Stock)';
    } else {
        itemStock.className = 'fw-bold text-success';
        itemStock.textContent += ' (Good Stock)';
    }
    
    itemDetails.style.display = 'block';
}

// Add item to cart
function addToCart() {
    const categorySelect = document.getElementById('category');
    const itemSelect = document.getElementById('item_name');
    const quantityInput = document.getElementById('quantity');
    
    const selectedOption = itemSelect.options[itemSelect.selectedIndex];
    
    if (!selectedOption.value || !quantityInput.value) {
        alert('Please select an item and enter quantity');
        return;
    }
    
    const item = {
        name: selectedOption.value,
        category: selectedOption.dataset.category,
        unit_price: parseFloat(selectedOption.dataset.price),
        quantity: parseInt(quantityInput.value),
        stock_level: parseInt(selectedOption.dataset.stock)
    };
    
    // Check if requested quantity exceeds stock
    if (item.quantity > item.stock_level) {
        alert(`Sorry, only ${item.stock_level} units available in stock for ${item.name}`);
        return;
    }
    
    // Calculate total price
    item.total_price = item.unit_price * item.quantity;
    
    // Check if item already in cart
    const existingIndex = cart.findIndex(cartItem => cartItem.name === item.name);
    
    if (existingIndex !== -1) {
        // Update existing item
        cart[existingIndex].quantity += item.quantity;
        cart[existingIndex].total_price = cart[existingIndex].unit_price * cart[existingIndex].quantity;
    } else {
        // Add new item
        cart.push(item);
    }
    
    // Reset form
    quantityInput.value = 1;
    
    // Update display
    updateCartDisplay();
    
    // Show success message
    showSuccessMessage(`Added ${item.quantity} ${item.name} to cart`);
}

// Remove item from cart
function removeFromCart(itemName) {
    cart = cart.filter(item => item.name !== itemName);
    updateCartDisplay();
    showSuccessMessage('Item removed from cart');
}

// Clear entire cart
function clearCart() {
    if (cart.length === 0) {
        return;
    }
    
    if (confirm('Are you sure you want to clear the entire cart?')) {
        cart = [];
        updateCartDisplay();
        showSuccessMessage('Cart cleared');
    }
}

// Update cart display
function updateCartDisplay() {
    const cartSection = document.getElementById('cartSection');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (cart.length === 0) {
        cartSection.style.display = 'none';
        return;
    }
    
    cartSection.style.display = 'block';
    
    // Generate cart items HTML
    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-details">
                        <span class="badge bg-${item.category === 'Stationery' ? 'primary' : item.category === 'Stock' ? 'info' : 'secondary'}">${item.category}</span>
                        Qty: ${item.quantity} × R${item.unit_price.toFixed(2)}
                        ${item.stock_level <= 5 ? '<span class="badge bg-danger ms-2">Low Stock</span>' : ''}
                    </div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="cart-item-price me-3">R${item.total_price.toFixed(2)}</div>
                    <span class="cart-item-remove" onclick="removeFromCart('${item.name}')" title="Remove item">
                        <i class="fas fa-times"></i>
                    </span>
                </div>
            </div>
        </div>
    `).join('');
    
    // Calculate and display total
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    cartTotal.textContent = total.toFixed(2);
}

// Submit cart as multi-item order
function submitCart() {
    if (cart.length === 0) {
        alert('Cart is empty. Please add items before submitting.');
        return;
    }
    
    // Confirm submission
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    const itemCount = cart.length;
    
    if (!confirm(`Submit order with ${itemCount} items for total R${total.toFixed(2)}?`)) {
        return;
    }
    
    // Prepare data for submission
    const cartData = document.getElementById('cartData');
    cartData.value = JSON.stringify(cart);
    
    // Submit form
    const form = document.getElementById('multiItemForm');
    form.submit();
    
    // Clear cart after submission
    cart = [];
    updateCartDisplay();
}

// Show success message
function showSuccessMessage(message) {
    // Create a temporary alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 3000);
}

// Show error message
function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Utility function to format currency
function formatCurrency(amount) {
    return `R${parseFloat(amount).toFixed(2)}`;
}

// Utility function to get stock status class
function getStockStatusClass(stockLevel) {
    if (stockLevel > 20) return 'stock-good';
    if (stockLevel > 5) return 'stock-low';
    return 'stock-critical';
}

// Auto-refresh functionality for admin dashboard
function enableAutoRefresh() {
    if (window.location.pathname === '/admin_dashboard') {
        // Refresh every 30 seconds for admin dashboard
        setInterval(() => {
            const pendingCount = document.querySelectorAll('.badge.bg-warning').length;
            if (pendingCount > 0) {
                // Only refresh if there are pending requests
                window.location.reload();
            }
        }, 30000);
    }
}

// Initialize auto-refresh on page load
document.addEventListener('DOMContentLoaded', enableAutoRefresh);

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Loading state management
function setLoadingState(buttonElement, isLoading) {
    if (isLoading) {
        buttonElement.disabled = true;
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    } else {
        buttonElement.disabled = false;
        // Restore original text - this would need to be tracked separately
    }
}

// Local storage helpers for cart persistence
function saveCartToStorage() {
    localStorage.setItem('kpms_cart', JSON.stringify(cart));
}

function loadCartFromStorage() {
    const savedCart = localStorage.getItem('kpms_cart');
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
            updateCartDisplay();
        } catch (error) {
            console.error('Error loading cart from storage:', error);
            cart = [];
        }
    }
}

// Clear cart storage on successful submission
function clearCartStorage() {
    localStorage.removeItem('kpms_cart');
}

// Enhanced cart management with persistence
function addToCartWithPersistence() {
    addToCart();
    saveCartToStorage();
}

function removeFromCartWithPersistence(itemName) {
    removeFromCart(itemName);
    saveCartToStorage();
}

function clearCartWithPersistence() {
    clearCart();
    clearCartStorage();
}

// Initialize cart from storage on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCartFromStorage();
});

// Export functions for global use
window.loadCategoryItems = loadCategoryItems;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.clearCart = clearCart;
window.submitCart = submitCart;