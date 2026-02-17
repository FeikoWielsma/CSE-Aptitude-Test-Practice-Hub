
# Archetypes for Endless Mode Data Generation

COMPANIES = [
    "Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Ind", "Wayne Ent", 
    "Cyberdyne", "Massive Dynamic", "Hooli", "Pied Piper", "Soylent Corp", 
    "Tyrell Corp", "Veidt Ent", "Yoyodyne", "Virtucon", "MomCorp"
]

DEPARTMENTS = [
    "Sales", "Marketing", "R&D", "HR", "IT", "Operations", "Finance", "Legal", 
    "Support", "Logistics"
]

PRODUCTS = [
    "Widget A", "Widget B", "Gadget X", "Gadget Y", "Device Pro", "Device Mini", 
    "SuperTool", "MegaTool", "UltraPhone", "SmartWatch"
]

CITIES = [
    "New York", "London", "Tokyo", "Paris", "Berlin", "Sydney", "Toronto", 
    "Singapore", "Dubai", "Mumbai", "Shanghai", "Sao Paulo"
]

METRICS_FINANCIAL = [
    "Revenue ($m)", "Profit ($m)", "Cost ($m)", "Tax ($m)", "EBITDA ($m)", 
    "Op. Income ($m)", "Net Income ($m)"
]

METRICS_UNITS = [
    "Units Sold", "Customers", "Employees", "New Hires", "Complaints", 
    "Returns", "Website Visits (k)", "Downloads (k)"
]

TIMEFRAMES_QUARTERLY = ["Q1", "Q2", "Q3", "Q4"]
TIMEFRAMES_MONTHLY_H1 = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
TIMEFRAMES_MONTHLY_H2 = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TIMEFRAMES_YEARLY = ["2020", "2021", "2022", "2023", "2024"]

STOCK_NAMES = [
    "Acorn", "EDP", "Jasone", "Kilic", "Soares", "Safron", "Troika", "Omega", 
    "Zeta", "Apex", "Vertex", "Pinnacle", "Summit", "Zenith", "Nadir"
]

CURRENCIES = [
    {"code": "USD", "symbol": "$", "rate_range": (1.2, 1.4)}, 
    {"code": "EUR", "symbol": "€", "rate_range": (1.1, 1.2)},
    {"code": "JPY", "symbol": "¥", "rate_range": (130, 160)},
    {"code": "AUD", "symbol": "A$", "rate_range": (1.8, 2.0)},
    {"code": "CAD", "symbol": "C$", "rate_range": (1.6, 1.8)}
]

REGIONS = ["North", "South", "East", "West", "Midlands", "North-East", "North-West", "South-East", "South-West"]
PACKAGES = ["Platinum", "Gold", "Silver", "Bronze", "Basic", "Premium", "Ultimate", "Starter"]
ATTRACTIONS = ["Theme Park", "Water Park", "Safari Park", "Zoo", "Aquarium", "Adventure Land", "Dino World"]
AGE_GROUPS = ["Children (<16)", "Adults", "Seniors (>60)"]

# --- Additional Sectors ---

HOSPITALS = [
    "General Hospital", "St. Mary's", "City Medical", "County General", "Hope Clinic", 
    "Mercy Health", "Unity Care", "Prime Health"
]
WARDS = ["Cardiology", "ER", "Pediatrics", "Oncology", "Neurology", "Orthopedics", "Maternity"]

RETAILERS = [
    "SuperMart", "MegaBuy", "QuickShop", "FreshGrocer", "ValueKing", "HyperStore", "DailyNeeds"
]

ENERGY_PROVIDERS = [
    "PowerGen", "EcoEnergy", "GridCorp", "BrightSpark", "Solaris", "AtomCo", "HydroFlow"
]

ENERGY_SOURCES = ["Coal", "Gas", "Nuclear", "Wind", "Solar", "Hydro", "Biomass"]

UNIVERSITIES = [
    "Oxford Brookes", "Cambridge Tech", "London Uni", "Manchester Met", "Leeds Arts", "Bristol Sci"
]
FACULTIES = ["Engineering", "Arts", "Science", "Law", "Medicine", "Business", "Humanities"]

# --- Quant / Risk / Banking Archetypes ---

BANKS = [
    "Rabobank", "AIIB", "HSBC", "JPMorgan", "ICBC", "Barclays", "Deutsche Bank", "Mizuho"
]

INFRA_PROJECTS = [
    "HSR Railway (Asia)", "Solar Farm (Gobi)", "Hydro Dam (Mekong)", "Port Expansion (Gwadar)", 
    "Metro System (Delhi)", "Wind Park (North Sea)", "Bridge (Pearl River)"
]

RISK_METRICS = [
    "Probability of Default (%)", "Loss Given Default (%)", "Exposure at Default ($m)", 
    "Value at Risk (99%)", "Capital Adequacy Ratio (%)", "Liquidity Coverage Ratio (%)"
]

MODEL_TYPES = [
    "Credit Risk Model", "Market Risk Model", "Liquidity Model", "Pricing Model", "Fraud Detection"
]
VALIDATION_METRICS = [
    "MAE (Mean Abs Error)", "RMSE", "R-Squared", "Backtest Exceptions", "Stability Index (PSI)"
]

# Update Metrics Maps
METRICS_HEALTH = ["Patients Admitted", "Avg Wait Time (mins)", "Doctors on Duty", "Operations Performed"]
METRICS_RETAIL = ["Daily Footfall", "Avg Basket Size (£)", "Transactions", "Loyalty Signups"]
METRICS_ENERGY = ["Output (GWh)", "CO2 Emissions (Gt)", "Revenue ($m)", "Capacity (MW)"]
METRICS_EDU = ["Students Enrolled", "Graduates", "Research Grants (£k)", "Publications"]

HOSPITALS = [
    "General Hospital", "St. Mary's", "City Medical", "County General", "Hope Clinic", 
    "Mercy Health", "Unity Care", "Prime Health"
]
WARDS = ["Cardiology", "ER", "Pediatrics", "Oncology", "Neurology", "Orthopedics", "Maternity"]

RETAILERS = [
    "SuperMart", "MegaBuy", "QuickShop", "FreshGrocer", "ValueKing", "HyperStore", "DailyNeeds"
]

ENERGY_PROVIDERS = [
    "PowerGen", "EcoEnergy", "GridCorp", "BrightSpark", "Solaris", "AtomCo", "HydroFlow"
]

ENERGY_SOURCES = ["Coal", "Gas", "Nuclear", "Wind", "Solar", "Hydro", "Biomass"]

UNIVERSITIES = [
    "Oxford Brookes", "Cambridge Tech", "London Uni", "Manchester Met", "Leeds Arts", "Bristol Sci"
]
FACULTIES = ["Engineering", "Arts", "Science", "Law", "Medicine", "Business", "Humanities"]

# Update Metrics to include these contexts
METRICS_HEALTH = ["Patients Admitted", "Avg Wait Time (mins)", "Doctors on Duty", "Operations Performed"]
METRICS_RETAIL = ["Daily Footfall", "Avg Basket Size (£)", "Transactions", "Loyalty Signups"]
METRICS_ENERGY = ["Output (GWh)", "CO2 Emissions (Gt)", "Revenue ($m)", "Capacity (MW)"]
METRICS_EDU = ["Students Enrolled", "Graduates", "Research Grants (£k)", "Publications"]
