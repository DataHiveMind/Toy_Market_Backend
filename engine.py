import random

def calculate_base_utility(offer, customer):
    """
    Standard utility formula: value of the offer − total price + loyalty benefit − inconvenience cost[cite: 1].
    """
    return customer['valuation'] - offer['price'] + offer.get('loyalty_benefit', 0) - customer.get('inconvenience_cost', 0)

# ==========================================
# 15 DISTINCT BUYER ALGORITHMS
# ==========================================

def algo_bargain_hunter(offers, customer):
    """Bargain Hunters: Buyers with a low willingness to pay who prioritize low total prices[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Heavily penalize price in the utility calculation
            utility = customer['valuation'] - (offer['price'] * 1.5) + offer.get('loyalty_benefit', 0)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_collector(offers, customer):
    """Collectors: Buyers who value premium colors or finding a complete set[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Add significant utility bonus for premium traits
            if offer.get('is_premium') or offer.get('completes_set'):
                utility += 2.00 
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_convenience_shopper(offers, customer):
    """Convenience Shoppers: Buyers who inspect fewer sellers to minimize inconvenience cost[cite: 3]."""
    # Restrict search space to a maximum of 2 random sellers
    visible_offers = random.sample(offers, min(len(offers), 2)) 
    best_offer, max_utility = None, 0
    for offer in visible_offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_returning_customer(offers, customer):
    """Returning Customers: Buyers who value established relationships and loyalty benefits[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Apply a multiplier to loyalty benefits from established relationships
            if offer['seller_name'] in customer.get('history', []):
                utility += offer.get('loyalty_benefit', 0) * 2 
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_budget_constrained(offers, customer):
    """Budget-Constrained Buyers: Buyers with strict budgets who cannot afford premium items[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        # Strictly reject premium items and enforce a rigid budget cap
        if offer.get('is_premium') or offer['price'] > customer['budget'] or offer['stock'] <= 0:
            continue
        utility = calculate_base_utility(offer, customer)
        if utility > max_utility:
            max_utility, best_offer = utility, offer
    return best_offer

def algo_premium_seeker(offers, customer):
    """Premium Seekers: Buyers who place high explicit values on premium products[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Double their valuation if the product is premium
            valuation = customer['valuation'] * 2 if offer.get('is_premium') else customer['valuation']
            utility = valuation - offer['price'] + offer.get('loyalty_benefit', 0) - customer.get('inconvenience_cost', 0)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_basic_product_buyer(offers, customer):
    """Basic Product Buyers: Customers who prefer basic units over premium ones[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Penalize premium items
            if offer.get('is_premium'):
                utility -= 1.50
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_loyalty_driven(offers, customer):
    """Loyalty-Driven Buyers: Customers who strongly prioritize seller loyalty and history across days[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Isolate and aggressively weigh the loyalty/history factor
            utility = customer['valuation'] - offer['price'] + (offer.get('loyalty_benefit', 0) * 3)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_bundle_shopper(offers, customer):
    """Bundle Shoppers: Buyers focused on advertised bundles rather than individual units[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Exclusive massive bonus for bundled offers
            if offer.get('is_bundle'):
                utility += 3.00
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_ad_influenced(offers, customer):
    """Ad-Influenced Buyers: Customers highly susceptible to advertising[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Add the winning advertising auction value directly to utility
            utility += offer.get('ad_influence_score', 0)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_high_utility_maximizer(offers, customer):
    """High-Utility Maximizers: Buyers who strictly calculate and choose the offer with the highest positive utility[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            utility = calculate_base_utility(offer, customer)
            # Pure mathematical evaluation with zero biases
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_new_customer(offers, customer):
    """New Customers: First-time buyers in the market with zero seller history[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Strip all loyalty benefits from the calculation
            utility = customer['valuation'] - offer['price'] - customer.get('inconvenience_cost', 0)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_tie_breaker(offers, customer):
    """Tie-Breaker Buyers: Customers whose preferences often result in ties between sellers[cite: 3]."""
    best_offer = None
    max_utility = 0
    tied_offers = []
    
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Rounding utility to the nearest whole number to artificially induce ties
            utility = round(calculate_base_utility(offer, customer))
            if utility > max_utility:
                max_utility = utility
                tied_offers = [offer]
            elif utility == max_utility and utility > 0:
                tied_offers.append(offer)
                
    if tied_offers:
        # Resolve the tie randomly
        best_offer = random.choice(tied_offers)
    return best_offer

def algo_apathetic_shopper(offers, customer):
    """Apathetic Shoppers: Buyers with very low valuations, frequently choosing to buy nothing[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            # Halve the baseline valuation to make positive utility rare
            utility = (customer['valuation'] * 0.5) - offer['price'] + offer.get('loyalty_benefit', 0)
            if utility > max_utility and utility > 0:
                max_utility, best_offer = utility, offer
    return best_offer

def algo_quality_over_price(offers, customer):
    """Quality-Over-Price Buyers: Customers willing to ignore minor price differences for premium status[cite: 3]."""
    best_offer, max_utility = None, 0
    for offer in offers:
        if offer['price'] <= customer['budget'] and offer['stock'] > 0:
            effective_price = offer['price']
            # Ignore up to $0.50 of the price if the item is premium
            if offer.get('is_premium'):
                effective_price = max(0, effective_price - 0.50)
                
            utility = customer['valuation'] - effective_price + offer.get('loyalty_benefit', 0) - customer.get('inconvenience_cost', 0)
            if utility > max_utility:
                max_utility, best_offer = utility, offer
    return best_offer

# ==========================================
# MASTER SIMULATION ROUTER
# ==========================================

def process_customer_purchase(customer, live_inventory):
    """Routes the customer to their respective algorithm based on persona."""
    persona_map = {
        "Bargain Hunters": algo_bargain_hunter,
        "Collectors": algo_collector,
        "Convenience Shoppers": algo_convenience_shopper,
        "Returning Customers": algo_returning_customer,
        "Budget-Constrained Buyers": algo_budget_constrained,
        "Premium Seekers": algo_premium_seeker,
        "Basic Product Buyers": algo_basic_product_buyer,
        "Loyalty-Driven Buyers": algo_loyalty_driven,
        "Bundle Shoppers": algo_bundle_shopper,
        "Ad-Influenced Buyers": algo_ad_influenced,
        "High-Utility Maximizers": algo_high_utility_maximizer,
        "New Customers": algo_new_customer,
        "Tie-Breaker Buyers": algo_tie_breaker,
        "Apathetic Shoppers": algo_apathetic_shopper,
        "Quality-Over-Price Buyers": algo_quality_over_price
    }
    
    # Execute the specific algorithm mapped to this customer's persona
    algorithm_function = persona_map.get(customer['persona'], algo_high_utility_maximizer)
    return algorithm_function(live_inventory, customer)