from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery"},
    {"id": 4, "name": "Notebook", "price": 99, "category": "Stationery"}
]

orders = []

class OrderCreate(BaseModel):
    customer_name: str
    item: str

@app.get('/products/search')
def search_products(keyword: str = Query(...)):
    result = [p for p in products if keyword.lower() in p['name'].lower()]
    if not result:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(result), "products": result}

@app.get('/products/sort')
def sort_products(sort_by: str = Query('price'), order: str = Query('asc')):
    if sort_by not in ['price', 'name']:
        return {"message": "error: sort_by must be 'price' or 'name'"}
    reverse = (order == 'desc')
    result = sorted(products, key=lambda p: p[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "products": result}

@app.get('/products/page')
def page_products(page: int = Query(1, ge=1), limit: int = Query(2, ge=1, le=20)):
    start = (page - 1) * limit
    paged = products[start: start + limit]
    return {
        "page": page, 
        "limit": limit, 
        "total_pages": -(-len(products) // limit), 
        "products": paged
    }

@app.post('/orders')
def create_order(order: OrderCreate):
    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "item": order.item
    }
    orders.append(new_order)
    return new_order

@app.get('/orders/search')
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not results:
        return {'message': f'No orders found for: {customer_name}'}
    return {'customer_name': customer_name, 'total_found': len(results), 'orders': results}

@app.get('/products/sort-by-category')
def sort_by_category():
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {'products': result, 'total': len(result)}

@app.get('/products/browse')
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=20),
):
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]

    if sort_by in ['price', 'name']:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order=='desc'))

    total  = len(result)
    start  = (page - 1) * limit
    paged  = result[start : start + limit]

    return {
        'keyword':     keyword, 'sort_by': sort_by, 'order': order,
        'page': page,  'limit': limit, 'total_found': total,
        'total_pages': -(- total // limit) if limit else 0,
        'products':    paged,
    }

@app.get('/orders/page')
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(orders),
        'total_pages': -(-len(orders) // limit) if limit else 0,
        'orders':      orders[start : start + limit],
    }

@app.get('/products/{product_id}')
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return {"message": "Not found"}
