"""Example Playwright tests for saucedemo.com demo application.

These tests demonstrate the capabilities of the Python Playwright Test Runner
by testing the Sauce Labs demo e-commerce site.

Site: https://www.saucedemo.com/
Credentials: standard_user / secret_sauce
"""

import pytest


@pytest.mark.example
def test_valid_login(page):
    """Test successful login with valid credentials."""
    # Navigate to the site
    page.goto("https://www.saucedemo.com/")
    
    # Fill in login credentials
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    
    # Click login button
    page.click("#login-button")
    
    # Verify we're on the inventory page
    assert page.url == "https://www.saucedemo.com/inventory.html"
    assert page.is_visible(".inventory_list")


@pytest.mark.example
def test_invalid_login(page):
    """Test login with invalid credentials."""
    # Navigate to the site
    page.goto("https://www.saucedemo.com/")
    
    # Fill in invalid credentials
    page.fill("#user-name", "invalid_user")
    page.fill("#password", "wrong_password")
    
    # Click login button
    page.click("#login-button")
    
    # Verify error message is displayed
    error = page.locator("[data-test='error']")
    assert error.is_visible()
    assert "Epic sadface" in error.text_content()


@pytest.mark.example
class TestInventory:
    """Tests for the product inventory page."""
    
    def test_view_inventory(self, page):
        """Test viewing the product inventory."""
        # Login first
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        
        # Verify inventory items are displayed
        items = page.locator(".inventory_item")
        assert items.count() > 0
        
        # Verify first item has expected elements
        first_item = items.first
        assert first_item.locator(".inventory_item_name").is_visible()
        assert first_item.locator(".inventory_item_price").is_visible()
    
    def test_add_to_cart(self, page):
        """Test adding a product to the cart."""
        # Login
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        
        # Add first item to cart
        page.click(".inventory_item:first-child button")
        
        # Verify cart badge shows 1 item
        cart_badge = page.locator(".shopping_cart_badge")
        assert cart_badge.is_visible()
        assert cart_badge.text_content() == "1"


@pytest.mark.example
class TestCart:
    """Tests for the shopping cart."""
    
    def test_view_cart(self, page):
        """Test viewing the shopping cart."""
        # Login and add item
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        page.click(".inventory_item:first-child button")
        
        # Go to cart
        page.click(".shopping_cart_link")
        
        # Verify cart page
        assert page.url == "https://www.saucedemo.com/cart.html"
        cart_items = page.locator(".cart_item")
        assert cart_items.count() == 1
    
    def test_remove_from_cart(self, page):
        """Test removing a product from the cart."""
        # Login, add item, go to cart
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        page.click(".inventory_item:first-child button")
        page.click(".shopping_cart_link")
        
        # Remove item
        page.click(".cart_item button")
        
        # Verify cart is empty
        cart_items = page.locator(".cart_item")
        assert cart_items.count() == 0


@pytest.mark.example
class TestCheckout:
    """Tests for the checkout process."""
    
    def test_checkout_information(self, page):
        """Test entering checkout information."""
        # Login, add item, go to cart
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        page.click(".inventory_item:first-child button")
        page.click(".shopping_cart_link")
        
        # Start checkout
        page.click("#checkout")
        
        # Fill in information
        page.fill("#first-name", "John")
        page.fill("#last-name", "Doe")
        page.fill("#postal-code", "12345")
        page.click("#continue")
        
        # Verify we're on overview page
        assert "checkout-step-two" in page.url
    
    def test_complete_purchase(self, page):
        """Test completing a purchase."""
        # Login, add item, go to cart
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        page.click(".inventory_item:first-child button")
        page.click(".shopping_cart_link")
        
        # Complete checkout
        page.click("#checkout")
        page.fill("#first-name", "John")
        page.fill("#last-name", "Doe")
        page.fill("#postal-code", "12345")
        page.click("#continue")
        page.click("#finish")
        
        # Verify order complete
        assert "checkout-complete" in page.url
        confirmation = page.locator(".complete-header")
        assert confirmation.is_visible()
        assert "Thank you for your order" in confirmation.text_content()
