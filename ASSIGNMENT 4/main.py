from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
# Product Database
products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 50},
    3: {"name": "USB Hub", "price": 299, "stock": 0},  # out of stock
    4: {"name": "Pen Set", "price": 49, "stock": 100}
}

cart = []
orders = []
order_id_counter = 1

# Checkout Request 
class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# Add Item to Cart
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if product["stock"] == 0:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # check if already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # new cart item
    subtotal = quantity * product["price"]

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }

# View Cart
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }
    
# Remove Item from Cart
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item is out of stock")

# Checkout
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_id_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }

# View Orders
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }
