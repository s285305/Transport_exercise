"""
Generalised Cost (GC) calculation for a Saluzzo → Torino Porta Susa trip.

Definition:
    GC = C_money + VOT * t_trip

Units convention:
    - Monetary values: euros [€]
    - Time: minutes for inputs, converted to hours internally where needed
    - Distances: kilometres [km]
"""

from dataclasses import dataclass


# -----------------------------
# Global inputs
# -----------------------------

VOT_EUR_PER_H = 20.0

# Trip distance and driving time (one-way)
DISTANCE_KM_ONEWAY = 62.0
CAR_TIME_MIN = 75.0

# Fiat Panda Cross 2021 (1.0 Mild Hybrid) fuel consumption and assumed fuel price
CAR_WLTP_L_PER_100KM = 5.6
FUEL_PRICE_EUR_PER_L = 1.70

# Annual car costs (inputs for cost-per-km)
ANNUAL_INSURANCE_EUR = 450.0
ANNUAL_BOLLO_EUR = 150.0
ANNUAL_REVISION_MAINT_EUR = 200.0
ANNUAL_GARAGE_PARKING_EUR = 0.0

ANNUAL_TYRES_EUR = 120.0
ANNUAL_OIL_FLUIDS_EUR = 60.0
ANNUAL_REPAIRS_MAINT_PARTS_EUR = 200.0

ANNUAL_KM = 15000.0

# Depreciation (annuity) parameters
PURCHASE_PRICE_P_EUR = 15000.0
RESIDUAL_VALUE_VR_EUR = 6000.0
LIFETIME_YEARS_N = 10
AMORTISATION_RATE_I = 0.05

# Public transport fares (one-way)
PT_FARE_SALUZZO_SAVIGLIANO_EUR = 3.20
PT_FARE_SAVIGLIANO_TORINO_PS_EUR = 6.40

# Public transport times (minutes)
PT_ACCESS_MIN = 5.0          # home → Saluzzo station
PT_WAIT1_MIN = 10.0          # waiting for train #1
PT_TRAIN1_MIN = 18.0         # Saluzzo → Savigliano
PT_TRANSFER_WAIT_MIN = 8.0   # interchange waiting in Savigliano
PT_TRAIN2_MIN = 48.0         # Savigliano → Torino Porta Susa
PT_EGRESS_MIN = 2.0          # station exit/egress
PT_WALK_MIN = 10.0           # final walking segment


# -----------------------------
# Utility functions
# -----------------------------

def minutes_to_hours(minutes: float) -> float:
    return minutes / 60.0


def time_cost_eur(minutes: float, vot_eur_per_h: float) -> float:
    return minutes_to_hours(minutes) * vot_eur_per_h


def annuity_depreciation_eur_per_year(P: float, VR: float, n: int, i: float) -> float:
    """
    Annual technical depreciation rate (annuity form):
        A = (P - VR) * [((1+i)^n * i) / ((1+i)^n - 1)] + (VR * i)
    """
    factor = ((1.0 + i) ** n * i) / (((1.0 + i) ** n) - 1.0)
    return (P - VR) * factor + (VR * i)


def fuel_cost_per_km_eur(l_per_100km: float, fuel_price_eur_per_l: float) -> float:
    return (l_per_100km * fuel_price_eur_per_l) / 100.0


# -----------------------------
# Data containers
# -----------------------------

@dataclass
class ModeResult:
    mode: str
    money_cost_eur: float
    time_min: float
    time_cost_eur: float
    generalised_cost_eur: float


@dataclass
class CarCostBreakdown:
    fixed_annual_eur: float
    variable_annual_eur: float
    depreciation_annual_eur: float
    annual_total_nonfuel_eur: float
    nonfuel_cost_per_km_eur: float
    fuel_cost_per_km_eur: float
    total_cost_per_km_eur: float


# -----------------------------
# Calculations
# -----------------------------

def compute_private_car() -> tuple[ModeResult, CarCostBreakdown]:
    fixed_annual = (
        ANNUAL_INSURANCE_EUR
        + ANNUAL_BOLLO_EUR
        + ANNUAL_REVISION_MAINT_EUR
        + ANNUAL_GARAGE_PARKING_EUR
    )

    variable_annual = (
        ANNUAL_TYRES_EUR
        + ANNUAL_OIL_FLUIDS_EUR
        + ANNUAL_REPAIRS_MAINT_PARTS_EUR
    )

    depreciation_annual = annuity_depreciation_eur_per_year(
        PURCHASE_PRICE_P_EUR,
        RESIDUAL_VALUE_VR_EUR,
        LIFETIME_YEARS_N,
        AMORTISATION_RATE_I,
    )

    annual_total_nonfuel = fixed_annual + variable_annual + depreciation_annual
    nonfuel_per_km = annual_total_nonfuel / ANNUAL_KM

    fuel_per_km = fuel_cost_per_km_eur(CAR_WLTP_L_PER_100KM, FUEL_PRICE_EUR_PER_L)
    total_per_km = nonfuel_per_km + fuel_per_km

    money_trip = DISTANCE_KM_ONEWAY * total_per_km
    time_trip_min = CAR_TIME_MIN
    time_trip_cost = time_cost_eur(time_trip_min, VOT_EUR_PER_H)
    gc = money_trip + time_trip_cost

    breakdown = CarCostBreakdown(
        fixed_annual_eur=fixed_annual,
        variable_annual_eur=variable_annual,
        depreciation_annual_eur=depreciation_annual,
        annual_total_nonfuel_eur=annual_total_nonfuel,
        nonfuel_cost_per_km_eur=nonfuel_per_km,
        fuel_cost_per_km_eur=fuel_per_km,
        total_cost_per_km_eur=total_per_km,
    )

    result = ModeResult(
        mode="Private car (Fiat Panda Cross 2021)",
        money_cost_eur=money_trip,
        time_min=time_trip_min,
        time_cost_eur=time_trip_cost,
        generalised_cost_eur=gc,
    )

    return result, breakdown


def compute_public_transport() -> ModeResult:
    money_trip = PT_FARE_SALUZZO_SAVIGLIANO_EUR + PT_FARE_SAVIGLIANO_TORINO_PS_EUR

    time_trip_min = (
        PT_ACCESS_MIN
        + PT_WAIT1_MIN
        + PT_TRAIN1_MIN
        + PT_TRANSFER_WAIT_MIN
        + PT_TRAIN2_MIN
        + PT_EGRESS_MIN
        + PT_WALK_MIN
    )

    time_trip_cost = time_cost_eur(time_trip_min, VOT_EUR_PER_H)
    gc = money_trip + time_trip_cost

    return ModeResult(
        mode="Public transport (train + walk)",
        money_cost_eur=money_trip,
        time_min=time_trip_min,
        time_cost_eur=time_trip_cost,
        generalised_cost_eur=gc,
    )


def print_results(car: ModeResult, pt: ModeResult, breakdown: CarCostBreakdown) -> None:
    def line(label: str, value: float) -> str:
        return f"{label:<28} {value:>10.2f}"

    print("=== Inputs ===")
    print(line("VOT [€/h]:", VOT_EUR_PER_H))
    print(line("Distance one-way [km]:", DISTANCE_KM_ONEWAY))
    print()

    print("=== Private car (one-way) ===")
    print(line("Money cost [€]:", car.money_cost_eur))
    print(line("Time [min]:", car.time_min))
    print(line("Time cost [€]:", car.time_cost_eur))
    print(line("Generalised cost [€]:", car.generalised_cost_eur))
    print()

    print("=== Public transport (one-way) ===")
    print(line("Money cost [€]:", pt.money_cost_eur))
    print(line("Time [min]:", pt.time_min))
    print(line("Time cost [€]:", pt.time_cost_eur))
    print(line("Generalised cost [€]:", pt.generalised_cost_eur))
    print()

    print("=== Car cost breakdown ===")
    print(line("Fixed annual [€]:", breakdown.fixed_annual_eur))
    print(line("Variable annual [€]:", breakdown.variable_annual_eur))
    print(line("Depreciation annual [€]:", breakdown.depreciation_annual_eur))
    print(line("Annual non-fuel total [€]:", breakdown.annual_total_nonfuel_eur))
    print(line("Non-fuel cost per km [€]:", breakdown.nonfuel_cost_per_km_eur))
    print(line("Fuel cost per km [€]:", breakdown.fuel_cost_per_km_eur))
    print(line("Total cost per km [€]:", breakdown.total_cost_per_km_eur))
    print()

    best = car if car.generalised_cost_eur < pt.generalised_cost_eur else pt
    print(f"Best option by GC: {best.mode} ({best.generalised_cost_eur:.2f} €)")


def main() -> None:
    car, breakdown = compute_private_car()
    pt = compute_public_transport()
    print_results(car, pt, breakdown)


if __name__ == "__main__":
    main()
