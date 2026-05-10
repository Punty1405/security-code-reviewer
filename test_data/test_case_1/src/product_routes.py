from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/api/products')
def search_products():
    category = request.args.get('category', 'electronics')
    limit = request.args.get('limit', '10')
    offset = request.args.get('offset', '0')
    
    conn = sqlite3.connect('store.db')
    # Vulnerability: Integers are often concatenated directly because developers
    # assume they aren't 'strings' and thus aren't dangerous.
    query = f"SELECT * FROM products WHERE category = ? LIMIT {limit} OFFSET {offset}"
    
    cursor = conn.execute(query, (category,))
    products = cursor.fetchall()
    return {"data": products}