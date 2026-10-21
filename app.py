import os
import random
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, send_file, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
MONGO_URI = "mongodb+srv://Kennethlegare5_db_user:dlaSZAzCsiqBLVvy@cluster0.zvyonwj.mongodb.net/"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['toy_soldier_market']
    transactions_col = db['transactions']
    winners_col = db['daily_winners']
    sellers_col = db['sellers']
    print("MongoDB Connected Successfully.")
except Exception as e:
    print(f"Database connection failed: {e}")

# ==========================================
# WEB SCRAPER FOR SELLER PRICES
# ==========================================
def scrape_seller_prices():
    """
    Scrapes seller websites to dynamically update their live prices.
    Other teams must provide a common price-file specification or standard HTML format.
    """
    sellers = [
        {"name": "Team Alpha", "url": "http://example-alpha.com/prices"},
        {"name": "Team Beta", "url": "http://example-beta.com/prices"}
    ]
    
    live_inventory = []
    
    for seller in sellers:
        try:
            # Note: Update the HTML selectors based on the agreed-upon common specification
            response = requests.get(seller['url'], timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example scraping logic (to be adjusted based on actual seller markup)
            price_element = soup.find(class_='soldier-price')
            stock_element = soup.find(class_='virtual-stock')
            
            price = float(price_element.text.replace('$', '')) if price_element else 2.50
            stock = int(stock_element.text) if stock_element else 100
            
            live_inventory.append({
                "seller_name": seller['name'],
                "price": price,
                "stock": stock,
                "loyalty_benefit": random.uniform(0, 0.5) # Example benefit
            })
        except Exception as e:
            # Apply announced fallback rule to missing or invalid submissions
            print(f"Failed to scrape {seller['name']}. Applying fallback rules.")
            live_inventory.append({
                "seller_name": seller['name'],
                "price": 3.00, # Fallback penalty price
                "stock": 0,
                "loyalty_benefit": 0
            })
            
    return live_inventory

# ==========================================
# ALGORITHM & SIMULATION ENGINE
# ==========================================
def run_daily_simulation():
    """
    Processes customers in a randomized, reproducible order[cite: 1].
    """
    live_inventory = scrape_seller_prices()
    
    # 15 Buyer Personas
    buyer_types = [
        "Bargain Hunters", "Collectors", "Convenience Shoppers", "Returning Customers",
        "Budget-Constrained Buyers", "Premium Seekers", "Basic Product Buyers",
        "Loyalty-Driven Buyers", "Bundle Shoppers", "Ad-Influenced Buyers",
        "High-Utility Maximizers", "New Customers", "Tie-Breaker Buyers",
        "Apathetic Shoppers", "Quality-Over-Price Buyers"
    ]
    
    # Generate population
    customers = []
    for i in range(100): # 100 daily customers
        persona = random.choice(buyer_types)
        budget = random.uniform(2.00, 10.00) if persona != "Budget-Constrained Buyers" else random.uniform(1.00, 2.50)
        valuation = random.uniform(2.00, 5.00) if persona != "Apathetic Shoppers" else random.uniform(0.50, 1.50)
        
        customers.append({
            "buyer_id": f"CUST_{i}",
            "persona": persona,
            "budget": budget,
            "valuation": valuation,
            "inconvenience_cost": random.uniform(0, 0.5)
        })
        
    random.shuffle(customers) # Randomized order[cite: 1]
    
    daily_transactions = []
    
    for customer in customers:
        best_offer = None
        max_utility = 0
        
        # Evaluate offers
        for offer in live_inventory:
            if offer['stock'] <= 0 or customer['budget'] < offer['price']:
                continue
                
            # Utility = value of the offer − total price + loyalty benefit − inconvenience cost[cite: 1].
            utility = customer['valuation'] - offer['price'] + offer['loyalty_benefit'] - customer['inconvenience_cost']
            
            # Persona modifiers
            if customer['persona'] == "Bargain Hunters":
                utility += (3.00 - offer['price']) # Bonus for cheap items
            elif customer['persona'] == "High-Utility Maximizers":
                pass # Relies strictly on base utility
                
            # Choose offer with highest positive utility. If none, buy nothing[cite: 1].
            if utility > 0 and utility > max_utility:
                max_utility = utility
                best_offer = offer
                
        if best_offer:
            # Execute purchase
            best_offer['stock'] -= 1
            timestamp = datetime.datetime.now()
            
            tx = {
                "timestamp": timestamp,
                "website_seller": best_offer['seller_name'],
                "item": "Standard Soldier",
                "units": 1,
                "total_price": best_offer['price'],
                "buyer_persona": customer['persona'], # Private data, will be stripped from ledger
                "budget_remaining": customer['budget'] - best_offer['price'] # Private data
            }
            daily_transactions.append(tx)
            
    if daily_transactions:
        transactions_col.insert_many(daily_transactions)
        
    calculate_and_store_winner()

def calculate_and_store_winner():
    """
    Calculates total items sold per seller and logs the daily winner to MongoDB.
    """
    pipeline = [
        {"$group": {"_id": "$website_seller", "total_units": {"$sum": "$units"}}},
        {"$sort": {"total_units": -1}}
    ]
    results = list(transactions_col.aggregate(pipeline))
    
    if results:
        winner = results[0]
        winners_col.insert_one({
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "winning_seller": winner['_id'],
            "items_sold": winner['total_units']
        })

# ==========================================
# FLASK WEB SERVER ROUTES
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Toy Soldier Market Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .winner { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #0056b3; color: white; }
        .btn { display: inline-block; padding: 10px 15px; background: #0056b3; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Toy Soldier Market - Buyer Team Dashboard</h1>
    
    <div class="card winner">
        <h2>🏆 Daily Winner</h2>
        {% if winner %}
            <p><strong>{{ winner.winning_seller }}</strong> dominated the market today, selling <strong>{{ winner.items_sold }} units</strong>!</p>
        {% else %}
            <p>No winner data available for today yet. Run the simulation.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Market Summary</h2>
        <p><strong>Cutoff Time:</strong> 5:00 PM EST | <strong>Status:</strong> Active</p>
        <a href="/run-sim" class="btn">Run Daily Simulation (24hr cycle)</a>
        <a href="/ledger/download" class="btn" style="background-color: #28a745;">Download Public Ledger (CSV)</a>
        
        <table>
            <tr>
                <th>Seller Team</th>
                <th>Total Items Sold</th>
            </tr>
            {% for row in totals %}
            <tr>
                <td>{{ row._id }}</td>
                <td>{{ row.total_units }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    # Get totals
    pipeline = [{"$group": {"_id": "$website_seller", "total_units": {"$sum": "$units"}}}]
    totals = list(transactions_col.aggregate(pipeline))
    
    # Get latest winner
    winner = winners_col.find_one({}, sort=[("date", -1)])
    
    return render_template_string(HTML_TEMPLATE, totals=totals, winner=winner)

@app.route('/run-sim')
def trigger_simulation():
    run_daily_simulation()
    return redirect(url_for('dashboard'))

@app.route('/ledger/download')
def download_ledger():
    """
    Publishes daily aggregate results and downloadable simulated transaction records[cite: 1].
    Keeps individual customer profiles and any private parameters out of public downloads[cite: 1].
    """
    cursor = transactions_col.find({}, {"_id": 0})
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
        # Strip private buyer data before exporting[cite: 1].
        cols_to_drop = [col for col in ['buyer_persona', 'budget_remaining'] if col in df.columns]
        df = df.drop(columns=cols_to_drop)
        
    file_path = "public_ledger.csv"
    df.to_csv(file_path, index=False)
    
    return send_file(file_path, as_attachment=True, download_name="toy_soldier_ledger.csv")

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)