
import random
import archetypes
from functools import reduce

class TableGenerator:
    def __init__(self):
        self.context = ""
        self.data = [] # List of dicts or list of lists
        self.headers = []
        self.row_labels = []
        self.title = ""
        
    def generate_financial_table(self):
        """
        Generates a table of Entities x Timeframes with Financial Data.
        e.g. Companies x Quarters (Revenue)
        """
        # 1. Choose Dimensions
        entity_type = random.choice(["Company", "Department", "City", "Product"])
        
        if entity_type == "Company":
            entities = random.sample(archetypes.COMPANIES, 5)
        elif entity_type == "Department":
            entities = random.sample(archetypes.DEPARTMENTS, 5)
        elif entity_type == "City":
            entities = random.sample(archetypes.CITIES, 5)
        else:
            entities = random.sample(archetypes.PRODUCTS, 5)
            
        time_mode = random.choice(["Quarterly", "Yearly", "Monthly"])
        if time_mode == "Quarterly":
            cols = archetypes.TIMEFRAMES_QUARTERLY
        elif time_mode == "Yearly":
            cols = archetypes.TIMEFRAMES_YEARLY
        else:
            cols = random.choice([archetypes.TIMEFRAMES_MONTHLY_H1, archetypes.TIMEFRAMES_MONTHLY_H2])
            
        metric = random.choice(archetypes.METRICS_FINANCIAL)
        
        # 2. Generate Data
        # Base range
        base_min = random.randint(10, 50)
        base_max = random.randint(100, 500)
        multiplier = random.choice([1, 10, 1000]) # $m vs $k etc
        
        self.data = []
        self.row_labels = entities
        self.headers = cols
        self.title = f"{metric} by {entity_type} ({cols[0]}-{cols[-1]})"
        
        # Grid: rows x cols
        grid_data = []
        
        for ent in entities:
            row_data = []
            # Give each entity a "base" performance
            entity_base = random.randint(base_min, base_max)
            
            for col in cols:
                # Fluctuation
                fluctuation = random.choice([0.9, 0.95, 1.0, 1.05, 1.1, 1.2])
                val = entity_base * fluctuation * multiplier
                # Round nicely
                if val > 100: val = int(round(val, -1))
                else: val = int(round(val))
                
                row_data.append(val)
            grid_data.append(row_data)
            
        self.grid = grid_data # Stored as list of lists matching row_labels
        
        # 3. Create Context String (Markdown)
        md = f"**{self.title}**\n\n"
        md += "| | " + " | ".join(cols) + " |\n"
        md += "|---|" + "|".join(["---"] * len(cols)) + " |\n"
        
        for i, ent in enumerate(entities):
            row_vals = [f"{x:,}" for x in grid_data[i]]
            md += f"| **{ent}** | " + " | ".join(row_vals) + " |\n"
            
        self.context = md
        
        # 4. Generate Questions based on this specific grid
        questions = []
        q_funcs = [
            self.gen_q_cell_lookup,
            self.gen_q_row_sum,
            self.gen_q_col_sum,
            self.gen_q_max_in_col,
            self.gen_q_growth,
            self.gen_q_ratio,
            self.gen_q_difference
        ]
        
        # Pick 3 unique questions type if possible
        selected_funcs = random.sample(q_funcs, 3)
        
        for func in selected_funcs:
            try:
                q = func()
                if q: questions.append(q)
            except Exception as e:
                print(f"Error generating question: {e}")
                continue
                
        return {
            "context": self.context,
            "questions": questions
        }

    # --- Question Generators ---
    
    def gen_q_cell_lookup(self):
        r_idx = random.randint(0, len(self.row_labels)-1)
        c_idx = random.randint(0, len(self.headers)-1)
        
        entity = self.row_labels[r_idx]
        col = self.headers[c_idx]
        val = self.grid[r_idx][c_idx]
        
        return {
            "question": f"What was the {self.title.split('(')[0]} for {entity} in {col}?",
            "answer": f"{val:,}",
            "solution": f"Look up {entity} and {col}. Value is {val:,}.",
            "options": None # Let app generate
        }

    def gen_q_row_sum(self):
        r_idx = random.randint(0, len(self.row_labels)-1)
        entity = self.row_labels[r_idx]
        row_vals = self.grid[r_idx]
        total = sum(row_vals)
        
        return {
            "question": f"What was the total {self.title.split('(')[0]} for {entity} across all periods?",
            "answer": f"{total:,}",
            "solution": f"Sum of {entity}'s row: {' + '.join(map(str, row_vals))} = {total:,}.",
             "options": None
        }

    def gen_q_col_sum(self):
        c_idx = random.randint(0, len(self.headers)-1)
        col = self.headers[c_idx]
        col_vals = [row[c_idx] for row in self.grid]
        total = sum(col_vals)
        
        return {
            "question": f"What was the total {self.title.split('(')[0]} in {col}?",
            "answer": f"{total:,}",
            "solution": f"Sum of {col} column: {' + '.join(map(str, col_vals))} = {total:,}.",
             "options": None
        }

    def gen_q_max_in_col(self):
        c_idx = random.randint(0, len(self.headers)-1)
        col = self.headers[c_idx]
        col_vals = [row[c_idx] for row in self.grid]
        max_val = max(col_vals)
        max_idx = col_vals.index(max_val)
        winner = self.row_labels[max_idx]
        
        return {
            "question": f"Which entity had the highest {self.title.split('(')[0]} in {col}?",
            "answer": winner,
            "solution": f"Identify the maximum value in {col}. Max is {max_val:,} by {winner}.",
            "options": self.row_labels # Explicit options
        }

    def gen_q_growth(self):
        r_idx = random.randint(0, len(self.row_labels)-1)
        entity = self.row_labels[r_idx]
        
        c_start = 0
        c_end = len(self.headers)-1
        
        val_start = self.grid[r_idx][c_start]
        val_end = self.grid[r_idx][c_end]
        
        if val_start == 0: return None
        
        growth = ((val_end - val_start) / val_start) * 100
        growth_str = f"{growth:.1f}%"
        
        return {
            "question": f"What was the percentage growth for {entity} from {self.headers[c_start]} to {self.headers[c_end]}?",
            "answer": growth_str,
            "solution": f"({val_end} - {val_start}) / {val_start} = {growth/100:.3f} = {growth:.1f}%",
             "options": None
        }

    def gen_q_ratio(self):
        # Ratio between two entities in same column
        c_idx = random.randint(0, len(self.headers)-1)
        col = self.headers[c_idx]
        
        idxs = random.sample(range(len(self.row_labels)), 2)
        r1, r2 = idxs[0], idxs[1]
        
        e1 = self.row_labels[r1]
        e2 = self.row_labels[r2]
        
        v1 = self.grid[r1][c_idx]
        v2 = self.grid[r2][c_idx]
        
        # simplify ratio? Just format as "v1 : v2" roughly
        # Or calculate decimal?
        # Let's try to make it simpler, round to nearest 10 or 100
        
        return {
            "question": f"What is the approximate ratio of {e1} to {e2} in {col}?",
            "answer": f"{v1}:{v2}", # Distractor generator handles ratios generally
            "solution": f"{e1} = {v1}, {e2} = {v2}. Ratio {v1}:{v2}.",
             "options": None
        }

    def gen_q_difference(self):
        # Difference between two cols for same entity
        r_idx = random.randint(0, len(self.row_labels)-1)
        entity = self.row_labels[r_idx]
        
        idxs = random.sample(range(len(self.headers)), 2)
        idxs.sort() # c1 before c2
        c1, c2 = idxs[0], idxs[1]
        
        v1 = self.grid[r_idx][c1]
        v2 = self.grid[r_idx][c2]
        diff = v2 - v1
        
        return {
            "question": f"What is the difference in {self.title.split('(')[0]} for {entity} between {self.headers[c2]} and {self.headers[c1]}?",
            "answer": f"{diff:,}",
            "solution": f"{v2} - {v1} = {diff}",
             "options": None
        }

class StockTableGenerator:
    def __init__(self):
        self.context = ""
    
    def generate(self):
        stocks = random.sample(archetypes.STOCK_NAMES, 6)
        
        # Columns: Share, Interim Div (p), Final Div (p), Price (£), Low (£), High (£)
        headers = ["Share", "Interim Dividend (p)", "Final Dividend (p)", "Price (£)", "Low (£)", "High (£)"]
        
        data = []
        for stock in stocks:
            # Price between 5 and 20
            price = random.uniform(5.0, 20.0)
            
            # Low/High around price
            low = price * random.uniform(0.90, 0.98)
            high = price * random.uniform(1.02, 1.10)
            
            # Dividends (p) -> usually 1-5% yield total
            yield_target = random.uniform(0.02, 0.06)
            total_div_gbp = price * yield_target
            total_div_p = total_div_gbp * 100
            
            interim = total_div_p * random.uniform(0.3, 0.5)
            final = total_div_p - interim
            
            # Rounding
            # Dividends to nearest 1 or 5?
            interim = int(round(interim / 5) * 5)
            final = int(round(final / 5) * 5)
            if interim == 0: interim = 5
            if final == 0: final = 5
            
            data.append({
                "name": stock,
                "interim": interim,
                "final": final,
                "price": round(price, 2),
                "low": round(low, 2),
                "high": round(high, 2)
            })
            
        # Context Markdown
        md = "**Share Price and Dividend**\n\n"
        md += "| " + " | ".join(headers) + " |\n"
        md += "|---" * len(headers) + "|\n"
        
        for d in data:
            md += f"| **{d['name']}** | {d['interim']} | {d['final']} | {d['price']:.2f} | {d['low']:.2f} | {d['high']:.2f} |\n"
            
        self.data = data
        self.context = md
        
        questions = []
        
        # Q1: Yield Calculation
        # "For which share is the total yearly dividend valued at over X% of today's share price?"
        # Find one that is high yield
        target_stock = max(data, key=lambda x: (x['interim'] + x['final']) / (x['price']*100))
        actual_yield = ((target_stock['interim'] + target_stock['final']) / (target_stock['price']*100)) * 100
        threshold = int(actual_yield) 
        if threshold < actual_yield: threshold = float(f"{actual_yield - 0.5:.1f}")
        
        questions.append({
            "question": f"For which share is the total yearly dividend valued at over {threshold}% of today's share price?",
            "answer": target_stock['name'],
            "solution": f"Total Div = Interim + Final. Yield = (Total Div / 100) / Price. {target_stock['name']} yield is {actual_yield:.2f}%.",
            "options": [d['name'] for d in data]
        })
        
        # Q2: Cost to buy
        s1, s2 = random.sample(data, 2)
        q1 = random.randint(100, 500)
        q2 = random.randint(100, 500)
        cost = (q1 * s1['price']) + (q2 * s2['price'])
        # Round to nearest 100
        cost_rounded = int(round(cost, -2))
        
        questions.append({
            "question": f"What is the total cost of buying {q1} {s1['name']} shares and {q2} {s2['name']} shares (to the nearest £100)?",
            "answer": f"{cost_rounded:,}",
            "solution": f"({q1} * {s1['price']}) + ({q2} * {s2['price']}) = {cost:.2f}. Round to {cost_rounded:,}.",
            "options": None
        })
        
        # Q3: Fluctuation Range
        # "Which share had the largest difference between High and Low?"
        target_fluct = max(data, key=lambda x: x['high'] - x['low'])
        diff = target_fluct['high'] - target_fluct['low']
        
        questions.append({
            "question": "Which share had the largest difference between its High and Low price?",
            "answer": target_fluct['name'],
            "solution": f"{target_fluct['name']} diff is {diff:.2f}.",
            "options": [d['name'] for d in data]
        })
        
        return {"context": self.context, "questions": questions}

class CurrencyTableGenerator:
    def __init__(self):
        self.context = ""
        
    def generate(self):
        cities = random.sample(archetypes.CITIES, 5)
        base_currency = "GBP" # All sales in GBP in table
        
        # Pick 2 target currencies
        targets = random.sample(archetypes.CURRENCIES, 2)
        
        # Generate Exchange Rates
        rates = {}
        for t in targets:
            rates[t['code']] = round(random.uniform(*t['rate_range']), 2)
            
        rate_md = "**Exchange Rates (to £1)**\n\n"
        rate_md += "| Currency | Rate |\n|---|---|\n"
        for code, rate in rates.items():
            rate_md += f"| {code} | {rate:.2f} |\n"
            
        # Generate Sales Data
        sales_data = []
        months = ["Jan", "Feb", "Mar"]
        
        sales_md = "**Sales by City (£000's)**\n\n"
        sales_md += "| City | Jan | Feb | Mar |\n|---|---|---|---|\n"
        
        for city in cities:
            row = {
                "city": city,
                "vals": [random.randint(100, 500) for _ in range(3)]
            }
            sales_data.append(row)
            sales_md += f"| **{city}** | {row['vals'][0]} | {row['vals'][1]} | {row['vals'][2]} |\n"
            
        self.context = sales_md + "\n\n" + rate_md
        
        questions = []
        
        # Q1: Convert Total Sales for City
        # "What were the total sales for X in [Currency]?"
        target_city = random.choice(sales_data)
        target_curr = random.choice(targets)
        
        total_gbp = sum(target_city['vals'])
        total_converted = total_gbp * rates[target_curr['code']]
        total_rounded = int(round(total_converted))
        
        questions.append({
            "question": f"What were the total sales (Jan-Mar) for {target_city['city']} in {target_curr['code']} (to nearest {target_curr['code']}000)?",
            "answer": f"{total_rounded:,}",
            "solution": f"Total GBP: {total_gbp}. Rate: {rates[target_curr['code']]}. Converted: {total_converted:.2f}. Round: {total_rounded}.",
            "options": None
        })
        
        # Q2: Difference in Month
        c1, c2 = random.sample(sales_data, 2)
        m_idx = random.randint(0, 2)
        month = months[m_idx]
        
        diff_gbp = abs(c1['vals'][m_idx] - c2['vals'][m_idx])
        
        questions.append({
            "question": f"What was the difference in sales between {c1['city']} and {c2['city']} in {month} (£000's)?",
            "answer": f"{diff_gbp}",
            "solution": f"|{c1['vals'][m_idx]} - {c2['vals'][m_idx]}| = {diff_gbp}",
            "options": None
        })

        # Q3: Highest revenue in Currency
        # "Which city had the highest sales in Jan in [Currency]?"
        # (Same as highest in GBP, but adds flavor)
        m_idx = random.randint(0, 2)
        month = months[m_idx]
        target_curr = random.choice(targets)
        
        winner = max(sales_data, key=lambda x: x['vals'][m_idx])
        val_gbp = winner['vals'][m_idx]
        val_conv = float(val_gbp) * rates[target_curr['code']]
        
        questions.append({
            "question": f"Which city had the highest sales in {month}, and what was the value in {target_curr['code']} (k)?",
            "answer": f"{winner['city']} ({int(val_conv):,})",
            "solution": f"Highest GBP was {winner['city']} ({val_gbp}). Converted: {val_conv:.1f}.",
            "options": [c['city'] for c in sales_data] # Just cities as options, or complex strings? Just cities is easier for matching.
            # Wait, app checks string match. If answer is "City (Val)", option provided must match.
            # Let's just ask for City Name.
        })
        # Fix Q3 answer to be simple for validation if we provide options
        questions[-1]['question'] = f"Which city had the highest sales in {month}?"
        questions[-1]['answer'] = winner['city']
        
        # Fix Q3 answer to be simple for validation if we provide options
        questions[-1]['question'] = f"Which city had the highest sales in {month}?"
        questions[-1]['answer'] = winner['city']
        
        return {"context": self.context, "questions": questions}

class SubscriptionTableGenerator:
    def __init__(self):
        self.context = ""

    def generate(self):
        regions = random.sample(archetypes.REGIONS, 5)
        # Packages: Pick 3
        packages = random.sample(archetypes.PACKAGES, 3)
        
        # Sort packages by "value" roughly implies name? No, just assign prices.
        # Let's map package to price to simulate realism
        price_map = {
            "Platinum": 50, "Gold": 40, "Silver": 30, "Bronze": 20, 
            "Basic": 15, "Premium": 45, "Ultimate": 60, "Starter": 10
        }
        
        # Assign prices and contracts
        pkg_prices = {p: price_map.get(p, 25) for p in packages}
        
        contract_map = {
            "Platinum": 24, "Gold": 12, "Silver": 12, "Bronze": 6, 
            "Basic": 1, "Premium": 12, "Ultimate": 24, "Starter": 1
        }
        pkg_contracts = {p: contract_map.get(p, 12) for p in packages}
        
        # Determine columns: Just the packages? Or Months? 
        # Real question has packages as columns
        headers = packages
        
        data = []
        md = "**Sales of Packages by Region**\n\n"
        md += "| Region | " + " | ".join(headers) + " |\n"
        md += "|---|" + "---|" * len(headers) + "\n"
        
        for r in regions:
            row_vals = {}
            row_str = f"| **{r}** |"
            for p in packages:
                # Random count of sales
                count = random.randint(100, 5000)
                row_vals[p] = count
                row_str += f" {count:,} |"
            md += row_str + "\n"
            data.append({"region": r, "sales": row_vals})
            
        # Add Price Row
        md += "| **Monthly Cost (£)** |"
        for p in packages:
            md += f" {pkg_prices[p]} |"
        md += "\n"

        # Add Contract Length Row
        md += "| **Contract Length (months)** |"
        for p in packages:
            md += f" {pkg_contracts[p]} |"
        md += "\n"
            
        self.context = md
        self.data = data
        self.pkg_prices = pkg_prices
        
        questions = []
        
        # Q1: Total Revenue for a specific package in a region
        # "What is the total revenue from [Package] in [Region]?"
        target_row = random.choice(data)
        target_pkg = random.choice(packages)
        count = target_row['sales'][target_pkg]
        price = pkg_prices[target_pkg]
        rev = count * price
        
        questions.append({
            "question": f"Total revenue from {target_pkg} packages in {target_row['region']} (based on monthly cost)?",
            "answer": f"{rev:,}",
            "solution": f"Sales: {count:,} * Price: £{price} = £{rev:,}",
            "options": None
        })
        
        # Q2: Aggregated Comparison
        # "Which region had the highest total number of [Pkg A] + [Pkg B] sold?"
        subset_pkgs = random.sample(packages, 2)
        
        winner = max(data, key=lambda x: sum(x['sales'][p] for p in subset_pkgs))
        total_sales = sum(winner['sales'][p] for p in subset_pkgs)
        
        questions.append({
            "question": f"Which region had the highest combined sales of {subset_pkgs[0]} and {subset_pkgs[1]}?",
            "answer": winner['region'],
            "solution": f"Sum {subset_pkgs[0]} + {subset_pkgs[1]} for each. {winner['region']} had {total_sales:,}.",
            "options": regions 
        })
        
        # Q3: Contract Value
        # "What is the total contract value of sales for [Pkg] in [Region]?"
        target_row = random.choice(data)
        target_pkg = random.choice(packages)
        months = pkg_contracts[target_pkg]
        count = target_row['sales'][target_pkg]
        price = pkg_prices[target_pkg]
        total_val = count * price * months
        
        questions.append({
            "question": f"What is the total contract value generated by {target_pkg} sales in {target_row['region']}?",
            "answer": f"{total_val:,}",
            "solution": f"{count:,} sales * £{price} * {months} months = £{total_val:,}",
            "options": None
        })
        
        return {"context": self.context, "questions": questions}

class AttractionTableGenerator:
    def __init__(self):
        self.context = ""
        
    def generate(self):
        # 2 Locations
        locs = random.sample(archetypes.ATTRACTIONS, 2)
        # 3 Age Groups
        groups = archetypes.AGE_GROUPS
        
        # Generate Fees
        fees = {} # {(loc, group): price}
        visitors = {} # {(loc, group): count}
        
        md = "**Average Daily Visitors**\n\n"
        # Header: | | Location 1 | Location 1 | Location 2 | Location 2 |
        # Subhead: | | Fee | Visitors | Fee | Visitors |
        
        md += "| | " + f"**{locs[0]}** | **{locs[0]}** | **{locs[1]}** | **{locs[1]}** |\n"
        md += "|---|---|---|---|---|\n"
        md += "| | **Entrance Fee** | **Visitors** | **Entrance Fee** | **Visitors** |\n"
        
        base_prices = {
            "Adults": random.randint(10, 25),
            "Children": random.randint(5, 15),
            "Seniors": random.randint(5, 15)
        }
        
        for g in groups:
            row_str = f"| **{g}** |"
            for loc in locs:
                # Vary price slightly per location
                price = base_prices[g.split()[0]] + random.choice([-1, 0, 1, 2])
                price_str = f"£{price:.2f}"
                fees[(loc, g)] = price
                
                vis_count = random.randint(500, 5000)
                visitors[(loc, g)] = vis_count
                
                row_str += f" {price_str} | {vis_count:,} |"
            md += row_str + "\n"
            
        md += "\n**Concessions**\n"
        md += "* 10% discount for online bookings\n"
        md += "* 20% discount for school trips\n"
        
        self.context = md
        self.fees = fees
        self.visitors = visitors
        self.locs = locs
        self.groups = groups
        
        questions = []
        
        # Q1: Visitor Difference
        # "How many more Adults visited Loc A vs Loc B?"
        target_g = random.choice(groups)
        v1 = visitors[(locs[0], target_g)]
        v2 = visitors[(locs[1], target_g)]
        diff = abs(v1-v2)
        
        questions.append({
            "question": f"What is the difference in {target_g} visitors between {locs[0]} and {locs[1]}?",
            "answer": f"{diff:,}",
            "solution": f"|{v1} - {v2}| = {diff:,}",
            "options": None
        })
        
        # Q2: Revenue with Price Hike
        # "If {Loc} raised fees by 10%, what is the additional revenue from {Group}?"
        loc = random.choice(locs)
        g = random.choice(groups)
        count = visitors[(loc, g)]
        fee = fees[(loc, g)]
        curr_rev = count * fee
        hike = 0.10
        add_rev = curr_rev * hike
        
        questions.append({
            "question": f"If {loc} raised entrance fees by 10%, what would be the additional daily revenue from {g} (to nearest £)?",
            "answer": f"{int(round(add_rev)):,}",
            "solution": f"Current Rev: {count} * £{fee} = £{curr_rev:,.2f}. 10% = £{add_rev:,.2f}.",
            "options": None
        })
        
        # Q3: Ratio of Fees (with manual discount logic question)
        # "What is ratio of Adult fee at Loc A to Child fee at Loc B?"
        f1 = fees[(locs[0], "Adults")]
        f2 = fees[(locs[1], "Children (<16)")]
        
        # Simplify ratio?
        # Just ask for value difference? Or explicit ratio
        # Let's simple ask for sum of fees
        
        questions.append({
            "question": f"How much would it cost for 1 Adult at {locs[0]} and 1 Child at {locs[1]} (no discounts)?",
            "answer": f"£{f1+f2:.2f}",
            "solution": f"£{f1} + £{f2} = £{f1+f2:.2f}",
            "options": None
        })
        
        return {"context": self.context, "questions": questions}

def generate_endless_set():
    # Randomly pick a generator strategy
    strategy = random.choice([
        TableGenerator().generate_financial_table, # The original one
        StockTableGenerator().generate,
        CurrencyTableGenerator().generate,
        SubscriptionTableGenerator().generate,
        AttractionTableGenerator().generate
    ])
    
    return strategy()
