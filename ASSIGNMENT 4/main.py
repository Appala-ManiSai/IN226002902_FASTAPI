from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Cart System API")

# Product Database
products = {
    1: {"name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"name": "Notebook", "price": 99, "in_stock": True},
    3: {"name": "USB Hub", "price": 899, "in_stock": False},
    4: {"name": "Pen Set", "price": 49, "in_stock": True},
}

cart = []
orders = []
order_id_counter = 1

def calculate_total(product, quantity):
    return product["price"] * quantity

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product = products[product_id]
    
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )
        
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}
            
    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}
        
    grand_total = sum(item["subtotal"] for item in cart)
    
    return {
        "items": cart,
        "item_count": len(cart), # number of unique products
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    global cart
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}
    raise HTTPException(status_code=404, detail="Item not in cart")

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

@app.post("/cart/checkout")
def checkout(details: CheckoutRequest):
    global cart, order_id_counter
    
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )
        
    orders_placed = len(cart)
    grand_total = sum(item["subtotal"] for item in cart)
    
    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": details.customer_name,
            "product": item["product_name"],
            "total_price": item["subtotal"],
            "delivery_address": details.delivery_address
        }
        orders.append(order)
        order_id_counter += 1
        
    cart.clear() # empty the cart
    return {
        "message": "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total": grand_total
    }

@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
