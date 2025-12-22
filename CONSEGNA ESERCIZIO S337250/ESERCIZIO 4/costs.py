import pandas as pd
import numpy as np

# =========================
# 1. LOAD TRIPS
# =========================
TRIPS_FILE = "Corse_Torino_TUTTI.csv"  
df = pd.read_csv(TRIPS_FILE)

# Keep only Lime, Bird, Voi
target_ops = ["LIME", "BIRD", "VOID"]
df = df[df["OPERATORE"].isin(target_ops)].copy()

# =========================
# 2. REVENUE (TARIFFS)
# =========================
tariffs = {
    "BIRD": {"unlock": 1.0, "per_min": 0.20},
    "LIME": {"unlock": 1.0, "per_min": 0.19},
    "VOID":  {"unlock": 1.0, "per_min": 0.19},
}

tariff_df = (
    pd.DataFrame(tariffs)
    .T.rename(columns={"unlock": "unlock_eur", "per_min": "per_min_eur"})
)

df = df.merge(
    tariff_df,
    left_on="OPERATORE",
    right_index=True,
    how="left"
)

df["revenue_eur"] = df["unlock_eur"] + df["per_min_eur"] * df["DURATA_MIN"]

revenue_by_op = (
    df.groupby("OPERATORE")
      .agg(
          trips=("OPERATORE", "size"),
          total_duration_min=("DURATA_MIN", "sum"),
          total_revenue_eur=("revenue_eur", "sum"),
          total_km = ('DISTANZA_KM', 'sum')
      )
)

# =========================
# 3. COST ASSUMPTIONS
# =========================
# ENERGY COST:
energy_cost_per_km = 0.00308


# Assume a commercial scooter price ~600 € as mid-range value.[web:2]
purchase_price_eur = 600.0

# Simple amortization: spread purchase over 2 years and 5,000 km per scooter
amortization_cost_per_km = purchase_price_eur / 5000.0  # 0.06 €/km

maintennce_cost_per_km= 100/5000

# VARIABLE COST PER KM (energy + maintenance proxy)
variable_cost_per_km = energy_cost_per_km + amortization_cost_per_km + maintennce_cost_per_km


# INSURANCE:
# Lime liability certificate shows that Lime (company) pays the premium
# for a general third‑party liability policy.[file:14]
# The document states 2,000,000 € limit per claim and 14,000,000 € annual cap
# but not the actual premium.[file:14]
# Assume an annual insurance cost per operator (you can refine these):
fixed_cost_annual_eur = {
        "LIME":   1500000.0,    # Real industry costs
        "BIRD":   1500000.0,
        "VOID":    1200000.0,    
    }


period_years = 2

# =========================
# 4. BUILD COST TABLE
# =========================
# Variable cost per operator = cost_per_min * total minutes
revenue_by_op["var_cost_per_km_eur"] = variable_cost_per_km
revenue_by_op["variable_cost_eur"] = (
    revenue_by_op["var_cost_per_km_eur"] * revenue_by_op["total_km"]
)

# Fixed insurance cost per operator for the period
revenue_by_op["fixed_cost_eur"] = revenue_by_op.index.map(
    lambda op: fixed_cost_annual_eur.get(op, 0.0) * period_years
)


revenue_by_op["fixed_cost_other_eur"] = 0

revenue_by_op["total_fixed_cost_eur"] = (
    revenue_by_op["fixed_cost_eur"]
    + revenue_by_op["fixed_cost_other_eur"]
)

# Total cost and profit
revenue_by_op["total_cost_eur"] = (
    revenue_by_op["variable_cost_eur"] + revenue_by_op["total_fixed_cost_eur"]
)
revenue_by_op["profit_eur"] = (
    revenue_by_op["total_revenue_eur"] - revenue_by_op["total_cost_eur"]
)
revenue_by_op["profit_margin_pct"] = (
    revenue_by_op["profit_eur"] / revenue_by_op["total_revenue_eur"] * 100
)

# =========================
# 5. SHOW RESULTS
# =========================
pd.set_option("display.float_format", "{:,.2f}".format)
print(revenue_by_op)

# Optional export
revenue_by_op.to_csv("Lime_Bird_Voi_profitability.csv")
