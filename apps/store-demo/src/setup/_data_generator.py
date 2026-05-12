"""
Synthetic data generator (internal module used by load_data.py).

Generates Silver-layer JSON/Parquet files for the 7-Eleven Store
Intelligence demo: 10 stores, 200+ articles, 90 days of sales,
inventory, write-offs, purchases, budgets, and customer reviews.

Do not invoke directly. Run `python load_data.py` instead.
"""

import random
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

# Seed for reproducibility
random.seed(42)

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_STORES = 10
NUM_DAYS = 90  # 3 months of data
START_DATE = date.today() - timedelta(days=NUM_DAYS)

# Australian states
STATES = ['VIC', 'NSW', 'QLD', 'SA', 'WA']

# Store format types
FORMAT_TYPES = ['Standard', 'Express', 'Metro', 'Fuel']

# Categories and subcategories
CATEGORIES = {
    'Hot Beverages': {
        'subcategories': ['Coffee', 'Tea', 'Hot Chocolate'],
        'department': 'Beverages',
        'layout_group': 'Coffee Station',
        'is_food_service': True
    },
    'Cold Beverages': {
        'subcategories': ['Soft Drinks', 'Energy Drinks', 'Water', 'Juices', 'Iced Coffee'],
        'department': 'Beverages',
        'layout_group': 'Cold Drinks Wall',
        'is_food_service': False
    },
    'Hot Food': {
        'subcategories': ['Pies', 'Sausage Rolls', 'Hot Dogs', 'Travellers', 'Wedges'],
        'department': 'Food Service',
        'layout_group': 'Hot Food Bay',
        'is_food_service': True
    },
    'Fresh Food': {
        'subcategories': ['Sandwiches', 'Salads', 'Wraps', 'Sushi'],
        'department': 'Food Service',
        'layout_group': 'Fresh Food',
        'is_food_service': False
    },
    'Packaged Snacks': {
        'subcategories': ['Chips', 'Chocolate', 'Confectionery', 'Nuts'],
        'department': 'Grocery',
        'layout_group': 'Snack Aisle',
        'is_food_service': False
    },
    'Tobacco': {
        'subcategories': ['Cigarettes', 'Cigars', 'Rolling Tobacco'],
        'department': 'Tobacco',
        'layout_group': 'Counter',
        'is_food_service': False
    },
    'Grocery': {
        'subcategories': ['Bread', 'Milk', 'Eggs', 'Spreads'],
        'department': 'Grocery',
        'layout_group': 'Grocery Aisle',
        'is_food_service': False
    },
    'Ice Cream': {
        'subcategories': ['Tubs', 'Bars', 'Cones'],
        'department': 'Frozen',
        'layout_group': 'Freezer',
        'is_food_service': False
    }
}

# Vendors
VENDORS = [
    {'name': 'Coca-Cola Amatil', 'lead_time': 2, 'delivery_days': 'MON,WED,FRI'},
    {'name': 'PepsiCo', 'lead_time': 2, 'delivery_days': 'TUE,THU'},
    {'name': 'Red Bull Australia', 'lead_time': 3, 'delivery_days': 'MON,THU'},
    {'name': 'Patties Foods', 'lead_time': 1, 'delivery_days': 'DAILY'},
    {'name': 'Krispy Kreme', 'lead_time': 1, 'delivery_days': 'DAILY'},
    {'name': 'Metcash', 'lead_time': 2, 'delivery_days': 'MON,WED,FRI'},
    {'name': 'Lion Dairy', 'lead_time': 1, 'delivery_days': 'DAILY'},
    {'name': 'Nestle', 'lead_time': 3, 'delivery_days': 'TUE,FRI'},
    {'name': 'Mars Wrigley', 'lead_time': 3, 'delivery_days': 'MON,THU'},
    {'name': 'British American Tobacco', 'lead_time': 2, 'delivery_days': 'TUE,FRI'},
    {'name': 'Philip Morris', 'lead_time': 2, 'delivery_days': 'MON,THU'},
    {'name': 'Streets Ice Cream', 'lead_time': 2, 'delivery_days': 'MON,WED,FRI'},
]

# Sample articles per category
ARTICLES_TEMPLATE = {
    'Hot Beverages': [
        ('7-Eleven Coffee Regular', 3.50, 4.50),
        ('7-Eleven Coffee Large', 4.00, 5.50),
        ('7-Eleven Latte Regular', 4.00, 5.50),
        ('7-Eleven Cappuccino Regular', 4.00, 5.50),
        ('Hot Chocolate Regular', 3.50, 4.50),
    ],
    'Cold Beverages': [
        ('Coca-Cola 600ml', 2.50, 4.80),
        ('Coca-Cola Zero 600ml', 2.50, 4.80),
        ('Pepsi Max 600ml', 2.40, 4.50),
        ('Red Bull 250ml', 2.80, 4.99),
        ('Red Bull Sugar Free 250ml', 2.80, 4.99),
        ('Monster Energy 500ml', 3.00, 5.50),
        ('V Energy 500ml', 2.80, 5.00),
        ('Mount Franklin Water 600ml', 1.00, 3.50),
        ('Pump Water 750ml', 1.20, 4.00),
        ('Farmers Union Iced Coffee 600ml', 2.50, 5.50),
        ('Dare Iced Coffee 500ml', 2.20, 4.80),
        ('Up & Go 500ml', 2.00, 4.50),
        ('Gatorade 600ml', 2.00, 4.50),
        ('Powerade 600ml', 2.00, 4.50),
        ('Orange Juice 500ml', 2.50, 5.00),
    ],
    'Hot Food': [
        ('Classic Meat Pie', 1.80, 4.50),
        ('Steak & Pepper Pie', 2.00, 5.00),
        ('Chicken & Vegetable Pie', 2.00, 5.00),
        ('Sausage Roll', 1.50, 3.50),
        ('Bacon & Cheese Traveller Pie', 2.20, 5.50),
        ('Spinach & Ricotta Roll', 1.80, 4.50),
        ('Hot Dog Classic', 1.50, 4.00),
        ('Hot Dog Cheese', 1.80, 4.50),
        ('Wedges Regular', 1.50, 4.00),
        ('Wedges Large', 2.00, 5.50),
        ('Dim Sim', 0.50, 1.50),
        ('Spring Roll', 0.80, 2.00),
    ],
    'Fresh Food': [
        ('Ham & Cheese Sandwich', 2.50, 6.00),
        ('Chicken Caesar Wrap', 3.00, 7.50),
        ('Salad Bowl - Garden', 3.50, 8.00),
        ('Sushi 6-Pack Salmon', 4.00, 9.00),
        ('Sushi 6-Pack Vegetarian', 3.50, 8.00),
        ('Egg & Lettuce Sandwich', 2.20, 5.50),
        ('BLT Sandwich', 3.00, 7.00),
    ],
    'Packaged Snacks': [
        ('Smiths Original 170g', 2.50, 5.50),
        ('Doritos Nacho Cheese 170g', 2.50, 5.50),
        ('Cadbury Dairy Milk 180g', 3.00, 6.00),
        ('Kit Kat Chunky', 1.50, 3.00),
        ('Mars Bar', 1.20, 2.80),
        ('Snickers', 1.20, 2.80),
        ('M&Ms Peanut 180g', 2.50, 5.50),
        ('Red Rock Deli 165g', 3.00, 6.50),
        ('Twisties Cheese 90g', 1.80, 4.00),
        ('Shapes BBQ 175g', 2.00, 4.50),
        ('Mixed Nuts 150g', 4.00, 8.00),
        ('Beef Jerky 50g', 3.50, 7.50),
    ],
    'Tobacco': [
        ('Winfield Blue 25s', 28.00, 38.00),
        ('Winfield Gold 25s', 28.00, 38.00),
        ('Peter Jackson 25s', 27.00, 36.50),
        ('Marlboro Red 25s', 30.00, 42.00),
        ('Marlboro Gold 25s', 30.00, 42.00),
        ('JPS Blue 25s', 25.00, 34.00),
    ],
    'Grocery': [
        ('White Bread Loaf', 2.00, 4.00),
        ('Full Cream Milk 2L', 2.50, 4.50),
        ('Full Cream Milk 1L', 1.50, 3.00),
        ('Free Range Eggs 6pk', 3.00, 6.00),
        ('Vegemite 220g', 4.00, 7.50),
        ('Nutella 400g', 5.00, 9.00),
    ],
    'Ice Cream': [
        ('Magnum Classic', 2.50, 5.50),
        ('Cornetto Classic', 2.00, 4.50),
        ('Gaytime', 2.00, 4.50),
        ('Paddle Pop Rainbow', 1.50, 3.50),
        ('Ben & Jerrys Pint', 8.00, 14.00),
        ('Connoisseur Tub 1L', 7.00, 12.00),
    ],
}

# Write-off reason codes
REASON_CODES = ['WASTE', 'DAMAGE', 'STORE_USE', 'EXPIRED', 'THEFT', 'OTHER']

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_store_clusters():
    """Generate store clusters by state."""
    clusters = []
    cluster_id = 1
    for state in STATES:
        for region in ['Metro', 'Regional']:
            clusters.append({
                'cluster_id': cluster_id,
                'cluster_code': f'{state}_{region[:3].upper()}',
                'cluster_name': f'{state} {region}',
                'state': state,
                'region': region,
                'store_count': random.randint(50, 150)
            })
            cluster_id += 1
    return clusters


def generate_stores(clusters):
    """Generate stores."""
    stores = []
    cities = {
        'VIC': ['Melbourne CBD', 'South Yarra', 'Richmond', 'St Kilda', 'Brunswick'],
        'NSW': ['Sydney CBD', 'Bondi', 'Parramatta', 'Manly', 'Surry Hills'],
        'QLD': ['Brisbane CBD', 'Gold Coast', 'Surfers Paradise', 'Fortitude Valley'],
        'SA': ['Adelaide CBD', 'Glenelg', 'Norwood'],
        'WA': ['Perth CBD', 'Fremantle', 'Subiaco'],
    }

    store_id = 1
    for i in range(NUM_STORES):
        state = STATES[i % len(STATES)]
        city = random.choice(cities[state])
        cluster = random.choice([c for c in clusters if c['state'] == state])

        stores.append({
            'store_id': store_id,
            'store_code': f'7E{store_id:04d}',
            'store_name': f'7-Eleven {city}',
            'address': f'{random.randint(1, 500)} {random.choice(["High", "Main", "King", "Queen", "George"])} Street',
            'city': city,
            'state': state,
            'postcode': str(random.randint(2000, 6000)),
            'cluster_id': cluster['cluster_id'],
            'territory': f'{state} {cluster["region"]}',
            'format_type': random.choice(FORMAT_TYPES),
            'open_date': (date.today() - timedelta(days=random.randint(365, 3650))).isoformat(),
            'is_active': True
        })
        store_id += 1
    return stores


def generate_categories():
    """Generate categories."""
    categories = []
    cat_id = 1
    for cat_name, cat_info in CATEGORIES.items():
        for subcat in cat_info['subcategories']:
            categories.append({
                'category_id': cat_id,
                'category_code': f'CAT{cat_id:03d}',
                'category_name': cat_name,
                'subcategory': subcat,
                'department': cat_info['department'],
                'layout_group': cat_info['layout_group'],
                'is_food_service': cat_info['is_food_service'],
                'is_active': True
            })
            cat_id += 1
    return categories


def generate_vendors():
    """Generate vendors."""
    vendors = []
    for i, v in enumerate(VENDORS, 1):
        vendors.append({
            'vendor_id': i,
            'vendor_code': f'VEN{i:03d}',
            'vendor_name': v['name'],
            'contact_email': f"orders@{v['name'].lower().replace(' ', '')}.com.au",
            'contact_phone': f'+61 3 {random.randint(9000, 9999)} {random.randint(1000, 9999)}',
            'lead_time_days': v['lead_time'],
            'delivery_days': v['delivery_days'],
            'is_active': True
        })
    return vendors


def generate_articles(categories, vendors):
    """Generate articles."""
    articles = []
    article_id = 1

    for cat_name, items in ARTICLES_TEMPLATE.items():
        # Find matching category
        matching_cats = [c for c in categories if c['category_name'] == cat_name]

        for item_name, cost, price in items:
            cat = random.choice(matching_cats)
            vendor = random.choice(vendors)

            margin = (price - cost) / price * 100
            purchase_margin = (price - cost) / cost * 100

            articles.append({
                'article_id': article_id,
                'article_code': f'SKU{article_id:05d}',
                'article_name': item_name,
                'ean': f'93{random.randint(10000000000, 99999999999)}',
                'category_id': cat['category_id'],
                'vendor_id': vendor['vendor_id'],
                'unit_cost': round(cost, 4),
                'unit_price': round(price, 2),
                'margin_pct': round(margin, 2),
                'purchase_margin_pct': round(purchase_margin, 2),
                'pack_qty': random.choice([1, 6, 12, 24]),
                'case_size': random.choice([6, 12, 24, 48]),
                'min_order_qty': random.choice([1, 2, 6]),
                'max_order_qty': random.choice([48, 96, 144]),
                'shelf_life_days': random.choice([1, 3, 7, 14, 30, 90, 365]) if cat['is_food_service'] else random.choice([90, 180, 365]),
                'is_food_service': cat['is_food_service'],
                'is_active': True
            })
            article_id += 1

    return articles


def generate_store_layouts(stores, articles, categories):
    """Generate store layouts (which articles are in each store)."""
    layouts = []

    for store in stores:
        # Each store carries ~80% of articles
        store_articles = random.sample(articles, int(len(articles) * 0.8))

        for article in store_articles:
            cat = next(c for c in categories if c['category_id'] == article['category_id'])
            layouts.append({
                'store_id': store['store_id'],
                'article_id': article['article_id'],
                'layout_location': cat['layout_group'],
                'shelf_position': f'Shelf-{random.randint(1, 5)}-{random.choice(["A", "B", "C", "D"])}',
                'facing_count': random.randint(1, 4),
                'is_tailored_in': True,
                'effective_date': START_DATE.isoformat()
            })

    return layouts


def generate_team_members(stores):
    """Generate team members."""
    members = []
    member_id = 1

    first_names = ['James', 'Sarah', 'Michael', 'Emma', 'David', 'Olivia', 'Daniel', 'Sophia', 'William', 'Ava', 'Liam', 'Mia', 'Noah', 'Isabella', 'Ethan']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson']
    roles = ['Store Manager', 'Assistant Manager', 'Team Leader', 'Team Member', 'Team Member', 'Team Member']

    for store in stores:
        num_staff = random.randint(8, 15)
        for i in range(num_staff):
            members.append({
                'member_id': member_id,
                'member_code': f'EMP{member_id:05d}',
                'store_id': store['store_id'],
                'member_name': f'{random.choice(first_names)} {random.choice(last_names)}',
                'role': roles[min(i, len(roles)-1)],
                'hire_date': (date.today() - timedelta(days=random.randint(30, 1825))).isoformat(),
                'is_active': True
            })
            member_id += 1

    return members


def generate_sales_transactions(stores, layouts, articles, categories):
    """Generate sales transactions for the date range."""
    transactions = []
    txn_id = 1

    # Build lookup for store layouts
    store_articles = {}
    for layout in layouts:
        key = layout['store_id']
        if key not in store_articles:
            store_articles[key] = []
        store_articles[key].append(layout['article_id'])

    # Article lookup
    article_dict = {a['article_id']: a for a in articles}

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        day_of_week = current_date.isoweekday()  # 1=Monday, 7=Sunday
        is_weekend = day_of_week in [6, 7]

        for store in stores:
            store_id = store['store_id']
            available_articles = store_articles.get(store_id, [])

            # Generate hourly transactions
            for hour in range(5, 24):  # 5am to 11pm
                # More transactions during peak hours
                if hour in [7, 8, 12, 13, 17, 18]:
                    num_txns = random.randint(15, 40)
                elif is_weekend and hour in [10, 11, 14, 15]:
                    num_txns = random.randint(10, 30)
                else:
                    num_txns = random.randint(3, 15)

                for _ in range(num_txns):
                    # Pick random articles for this transaction
                    num_items = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                    txn_articles = random.sample(available_articles, min(num_items, len(available_articles)))

                    for art_id in txn_articles:
                        article = article_dict[art_id]
                        units = random.choices([1, 2, 3], weights=[70, 25, 5])[0]

                        revenue = round(article['unit_price'] * units, 2)
                        cost = round(article['unit_cost'] * units, 2)
                        gp = round(revenue - cost, 2)

                        transactions.append({
                            'txn_id': txn_id,
                            'store_id': store_id,
                            'article_id': art_id,
                            'txn_date': current_date.isoformat(),
                            'txn_hour': hour,
                            'txn_minute': random.randint(0, 59),
                            'txn_timestamp': f'{current_date.isoformat()} {hour:02d}:{random.randint(0,59):02d}:00',
                            'day_of_week': day_of_week,
                            'is_weekend': is_weekend,
                            'units_sold': units,
                            'revenue': revenue,
                            'cost': cost,
                            'gross_profit': gp,
                            'txn_type': 'SALE'
                        })
                        txn_id += 1

    return transactions


def generate_inventory(stores, layouts, articles, transactions):
    """Generate current inventory snapshot."""
    inventory = []

    # Calculate sales by store/article
    sales_by_store_article = {}
    for txn in transactions:
        key = (txn['store_id'], txn['article_id'])
        if key not in sales_by_store_article:
            sales_by_store_article[key] = {'units': 0, 'last_date': None, 'first_date': None}
        sales_by_store_article[key]['units'] += txn['units_sold']
        txn_date = txn['txn_date']
        if sales_by_store_article[key]['last_date'] is None or txn_date > sales_by_store_article[key]['last_date']:
            sales_by_store_article[key]['last_date'] = txn_date

    article_dict = {a['article_id']: a for a in articles}
    today = date.today()

    for layout in layouts:
        store_id = layout['store_id']
        article_id = layout['article_id']
        article = article_dict[article_id]

        key = (store_id, article_id)
        sales_info = sales_by_store_article.get(key, {'units': 0, 'last_date': None})

        # Calculate stock on hand
        avg_daily_sales = sales_info['units'] / NUM_DAYS if NUM_DAYS > 0 else 0

        # Random stock level based on sales velocity
        if avg_daily_sales > 5:
            soh_qty = random.randint(10, 50)
        elif avg_daily_sales > 1:
            soh_qty = random.randint(5, 30)
        else:
            soh_qty = random.randint(0, 20)

        # Some items out of stock
        if random.random() < 0.05:
            soh_qty = 0

        # Some items dead stock (no recent sales)
        last_sale = sales_info['last_date']
        if last_sale:
            days_since = (today - date.fromisoformat(last_sale)).days
        else:
            days_since = random.randint(30, 60)
            last_sale = (today - timedelta(days=days_since)).isoformat()

        inventory.append({
            'store_id': store_id,
            'article_id': article_id,
            'snapshot_date': today.isoformat(),
            'soh_qty': soh_qty,
            'soh_value': round(soh_qty * article['unit_cost'], 2),
            'last_receipt_date': (today - timedelta(days=random.randint(1, 14))).isoformat(),
            'last_sale_date': last_sale,
            'days_since_last_sale': days_since,
            'first_oos_date': (today - timedelta(days=random.randint(1, 7))).isoformat() if soh_qty == 0 else None
        })

    return inventory


def generate_writeoffs(stores, layouts, articles, team_members):
    """Generate write-off records."""
    writeoffs = []
    writeoff_id = 1

    article_dict = {a['article_id']: a for a in articles}

    # Group team members by store
    members_by_store = {}
    for m in team_members:
        if m['store_id'] not in members_by_store:
            members_by_store[m['store_id']] = []
        members_by_store[m['store_id']].append(m)

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)

        for store in stores:
            store_id = store['store_id']
            store_layouts = [l for l in layouts if l['store_id'] == store_id]
            store_members = members_by_store.get(store_id, [])

            # Generate 5-15 write-offs per store per day
            num_writeoffs = random.randint(5, 15)

            for _ in range(num_writeoffs):
                layout = random.choice(store_layouts)
                article = article_dict[layout['article_id']]
                member = random.choice(store_members) if store_members else None

                # Determine reason based on article type
                if article['is_food_service']:
                    reason = random.choices(
                        ['WASTE', 'EXPIRED', 'STORE_USE', 'DAMAGE'],
                        weights=[40, 30, 20, 10]
                    )[0]
                else:
                    reason = random.choices(
                        ['DAMAGE', 'EXPIRED', 'THEFT', 'STORE_USE', 'OTHER'],
                        weights=[30, 25, 20, 15, 10]
                    )[0]

                # Store Use typically for milk
                if 'Milk' in article['article_name']:
                    reason = 'STORE_USE' if random.random() < 0.7 else reason

                qty = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                hour = random.randint(6, 22)

                writeoffs.append({
                    'writeoff_id': writeoff_id,
                    'store_id': store_id,
                    'article_id': article['article_id'],
                    'writeoff_date': current_date.isoformat(),
                    'writeoff_time': f'{hour:02d}:{random.randint(0,59):02d}:00',
                    'writeoff_hour': hour,
                    'quantity': qty,
                    'value': round(qty * article['unit_cost'], 2),
                    'reason_code': reason,
                    'reason_desc': f'{reason} - {article["article_name"]}',
                    'team_member_id': member['member_id'] if member else None,
                    'team_member_name': member['member_name'] if member else 'Unknown'
                })
                writeoff_id += 1

    return writeoffs


def generate_purchases(stores, layouts, articles, vendors):
    """Generate purchase/receipt records."""
    purchases = []
    purchase_id = 1

    article_dict = {a['article_id']: a for a in articles}
    vendor_dict = {v['vendor_id']: v for v in vendors}

    for day_offset in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        day_name = current_date.strftime('%a').upper()[:3]

        for store in stores:
            store_id = store['store_id']
            store_layouts = [l for l in layouts if l['store_id'] == store_id]

            # Check which vendors deliver today
            for layout in store_layouts:
                article = article_dict[layout['article_id']]
                vendor = vendor_dict.get(article['vendor_id'])

                if vendor and day_name in vendor['delivery_days']:
                    # 30% chance of delivery for each article
                    if random.random() < 0.3:
                        qty = random.choice([6, 12, 24, 48])
                        purchases.append({
                            'purchase_id': purchase_id,
                            'store_id': store_id,
                            'article_id': article['article_id'],
                            'vendor_id': vendor['vendor_id'],
                            'receipt_date': current_date.isoformat(),
                            'receipt_timestamp': f'{current_date.isoformat()} {random.randint(6,10):02d}:00:00',
                            'qty_ordered': qty,
                            'qty_received': qty,
                            'unit_cost': article['unit_cost'],
                            'total_cost': round(qty * article['unit_cost'], 2),
                            'po_number': f'PO{purchase_id:08d}'
                        })
                        purchase_id += 1

    return purchases


def generate_budgets(stores, categories):
    """Generate budget records."""
    budgets = []
    budget_id = 1

    # Monthly budgets for the period
    current_month = START_DATE.replace(day=1)
    end_month = date.today().replace(day=1)

    while current_month <= end_month:
        # Calculate month end
        if current_month.month == 12:
            month_end = current_month.replace(year=current_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_month.replace(month=current_month.month + 1, day=1) - timedelta(days=1)

        for store in stores:
            # Store-level monthly budget
            base_sales = random.uniform(300000, 500000)
            budgets.append({
                'budget_id': budget_id,
                'store_id': store['store_id'],
                'category_id': None,
                'period_type': 'MONTHLY',
                'period_start': current_month.isoformat(),
                'period_end': month_end.isoformat(),
                'budget_sales': round(base_sales, 2),
                'budget_gp': round(base_sales * 0.32, 2),
                'budget_units': round(base_sales / 5, 0)
            })
            budget_id += 1

            # Category-level budgets
            for cat in categories:
                cat_pct = random.uniform(0.05, 0.25)
                cat_sales = base_sales * cat_pct
                budgets.append({
                    'budget_id': budget_id,
                    'store_id': store['store_id'],
                    'category_id': cat['category_id'],
                    'period_type': 'MONTHLY',
                    'period_start': current_month.isoformat(),
                    'period_end': month_end.isoformat(),
                    'budget_sales': round(cat_sales, 2),
                    'budget_gp': round(cat_sales * random.uniform(0.25, 0.40), 2),
                    'budget_units': round(cat_sales / random.uniform(3, 8), 0)
                })
                budget_id += 1

        # Move to next month
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)

    return budgets


def generate_customer_reviews(stores):
    """Generate customer reviews for sentiment analysis demo.

    Creates realistic reviews with varying sentiment per store:
    - High performers: mostly positive reviews
    - Average performers: mixed reviews
    - Underperformers: more negative reviews
    """
    reviews = []
    review_id = 1

    # Store performance profiles (1=underperformer, 2=average, 3=high performer)
    store_profiles = {
        1: 3, 2: 2, 3: 1, 4: 3, 5: 2,
        6: 3, 7: 1, 8: 2, 9: 3, 10: 1
    }

    review_sources = ['Google', 'Yelp', 'Survey', 'Facebook']

    # Review templates by sentiment
    positive_reviews = [
        "Great store! Staff was very friendly and helpful. The store was clean and well-organized.",
        "Love this location. Always fresh coffee and the hot food is actually good.",
        "Quick stop for gas and snacks. Employees are always nice.",
        "Best 7-Eleven in the area. Clean bathrooms and the staff remembers my order!",
        "My go-to store! Fast service and they always have what I need in stock.",
        "Excellent customer service. The manager always greets customers with a smile.",
        "Clean store, friendly staff, great selection of snacks. What more could you want?",
        "The new self-checkout is fast and easy to use. Very satisfied!",
        "Amazing staff! They remembered my name after just a few visits.",
        "Always a pleasure to shop here. Friendly faces and great products.",
    ]

    neutral_reviews = [
        "Decent store but sometimes out of stock on popular items.",
        "Average 7-Eleven. Nothing special but gets the job done.",
        "Store is okay. Would like to see more variety in the snack selection.",
        "Good location but prices seem higher than other stores.",
        "Pretty standard 7-Eleven. Nothing to complain about but nothing special either.",
        "Convenient location. Staff could be more attentive during busy hours.",
        "Gets the job done. Would appreciate longer hours on weekends.",
        "Fair prices and decent selection. Staff is polite.",
        "Normal convenience store. Good for quick stops.",
        "Satisfactory experience overall. Checkout lines can get long at peak times.",
    ]

    negative_reviews = [
        "Terrible experience. Store was dirty and the cashier was rude.",
        "This location has gone downhill. Shelves are often empty.",
        "Long wait times and unfriendly staff. The only reason I go is proximity.",
        "Very disappointed with the service quality. Staff needs better training.",
        "Expired products on shelves. Reported to staff but they didn't seem to care.",
        "Store needs cleaning. Floors are sticky and shelves are dusty.",
        "Slow service and limited selection. Not my first choice.",
        "Had issues with the credit card machine multiple times.",
        "The coffee is always old and bitter. Need to refresh it more often.",
        "Service has gotten worse over the past few months.",
    ]

    customer_names = [
        "John M.", "Sarah K.", "Mike T.", "Lisa R.", "David L.", "Amy W.",
        "Mark S.", "Robert J.", "Jennifer H.", "Chris P.", "Nancy D.", "Kevin L.",
        "Rachel M.", "Steve H.", "Maria G.", "Brian T.", "Diane C.", "Paul R.",
        "Sandra W.", "Eric M.", "Melissa P.", "Greg S.", "Angela K.", "Jeff B.",
        "Tiffany N.", "Ryan D.", "Cathy L.", "Dennis F.", "Monica R.", "Tyler H.",
        "Sharon T.", "Andrew J.", "Karen W.", "Michael S.", "Laura P.", "James C.",
        "Nicole M.", "Scott R.", "Amanda B.", "Anonymous"
    ]

    # Generate 5 reviews per store over the past 30 days
    for store in stores:
        store_id = store['store_id']
        profile = store_profiles.get(store_id, 2)  # Default to average

        # Determine review distribution based on performance profile
        if profile == 3:  # High performer
            weights = [0.7, 0.2, 0.1]  # 70% positive, 20% neutral, 10% negative
        elif profile == 2:  # Average performer
            weights = [0.3, 0.4, 0.3]  # 30% positive, 40% neutral, 30% negative
        else:  # Underperformer
            weights = [0.1, 0.2, 0.7]  # 10% positive, 20% neutral, 70% negative

        for i in range(5):
            # Pick sentiment based on weights
            sentiment = random.choices(['positive', 'neutral', 'negative'], weights=weights)[0]

            if sentiment == 'positive':
                review_text = random.choice(positive_reviews)
                rating = random.choice([4, 5])
            elif sentiment == 'neutral':
                review_text = random.choice(neutral_reviews)
                rating = random.choice([3, 3, 4])
            else:
                review_text = random.choice(negative_reviews)
                rating = random.choice([1, 2, 2])

            # Random date in last 30 days
            review_date = date.today() - timedelta(days=random.randint(1, 30))

            reviews.append({
                'review_id': review_id,
                'store_id': store_id,
                'store_code': store['store_code'],
                'review_date': review_date.isoformat(),
                'review_source': random.choice(review_sources),
                'rating': rating,
                'review_text': review_text,
                'customer_name': random.choice(customer_names)
            })
            review_id += 1

    return reviews


def save_to_json(data, filename, data_dir):
    """Save data to JSON Lines file (one JSON object per line for fast Databricks loading)."""
    import os
    filepath = os.path.join(data_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        for record in data:
            f.write(json.dumps(record, default=str) + '\n')
    print(f"  Saved {len(data):,} records to {filename}")


def save_to_parquet(data, filename, data_dir):
    """Save data to Parquet file (fastest format for Databricks loading)."""
    import os
    try:
        import pandas as pd
    except ImportError:
        return False

    filepath = os.path.join(data_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df = pd.DataFrame(data)
    df.to_parquet(filepath, index=False)
    print(f"  Saved {len(data):,} records to {filename}")
    return True


# Mapping used by both generation and loading
TABLE_FILES = [
    ('silver_store_clusters',     'silver_store_clusters.json'),
    ('silver_stores',             'silver_stores.json'),
    ('silver_categories',         'silver_categories.json'),
    ('silver_vendors',            'silver_vendors.json'),
    ('silver_articles',           'silver_articles.json'),
    ('silver_store_layouts',      'silver_store_layouts.json'),
    ('silver_team_members',       'silver_team_members.json'),
    ('silver_sales_transactions', 'silver_sales_transactions.json'),
    ('silver_inventory',          'silver_inventory.json'),
    ('silver_write_offs',         'silver_write_offs.json'),
    ('silver_purchases',          'silver_purchases.json'),
    ('silver_budgets',            'silver_budgets.json'),
    ('silver_customer_reviews',   'silver_customer_reviews.json'),
]


def generate_all(data_dir, fmt='json'):
    """Generate all silver-layer data and write it to data_dir.

    Args:
        data_dir: Directory to write files into. Created if missing.
        fmt: 'json' (default) or 'parquet'.
    """
    print(f"Generating {NUM_DAYS} days of data from {START_DATE} to {date.today()}")
    print(f"Number of stores: {NUM_STORES}")
    print()

    print("Generating dimension data...")
    clusters = generate_store_clusters()
    stores = generate_stores(clusters)
    categories = generate_categories()
    vendors = generate_vendors()
    articles = generate_articles(categories, vendors)
    layouts = generate_store_layouts(stores, articles, categories)
    team_members = generate_team_members(stores)

    print(f"  {len(clusters)} clusters, {len(stores)} stores, {len(categories)} categories, "
          f"{len(vendors)} vendors, {len(articles)} articles, {len(layouts)} layouts, "
          f"{len(team_members)} team members")
    print()

    print("Generating fact data (this may take a minute)...")
    transactions = generate_sales_transactions(stores, layouts, articles, categories)
    inventory = generate_inventory(stores, layouts, articles, transactions)
    writeoffs = generate_writeoffs(stores, layouts, articles, team_members)
    purchases = generate_purchases(stores, layouts, articles, vendors)
    budgets = generate_budgets(stores, categories)
    reviews = generate_customer_reviews(stores)
    print(f"  {len(transactions):,} transactions, {len(inventory):,} inventory rows, "
          f"{len(writeoffs):,} write-offs, {len(purchases):,} purchases, "
          f"{len(budgets):,} budgets, {len(reviews):,} reviews")
    print()

    data_by_table = {
        'silver_store_clusters':     clusters,
        'silver_stores':             stores,
        'silver_categories':         categories,
        'silver_vendors':            vendors,
        'silver_articles':           articles,
        'silver_store_layouts':      layouts,
        'silver_team_members':       team_members,
        'silver_sales_transactions': transactions,
        'silver_inventory':          inventory,
        'silver_write_offs':         writeoffs,
        'silver_purchases':          purchases,
        'silver_budgets':            budgets,
        'silver_customer_reviews':   reviews,
    }

    print(f"Writing {fmt.upper()} files to {data_dir}/...")
    for table, rows in data_by_table.items():
        if fmt == 'parquet':
            ok = save_to_parquet(rows, f"{table}.parquet", data_dir)
            if not ok:
                # Fall back to JSON if pandas unavailable
                save_to_json(rows, f"{table}.json", data_dir)
        else:
            save_to_json(rows, f"{table}.json", data_dir)
    print()


if __name__ == '__main__':
    print("This is an internal module. Run `python load_data.py` instead.")
