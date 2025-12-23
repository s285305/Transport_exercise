# Transport Exercise: Shared Mobility & Sustainable Transport Analysis

## Overview

This repository contains two integrated research projects addressing sustainable mobility and transport innovation:

### **Project 1: Shared Mobility Analysis in Turin**
Comprehensive empirical analysis of shared electric scooter (e-scooter) mobility services operating in Turin, Italy. Analyzes trip data from major micromobility operators (Lime, Voi, Bird) across five integrated research exercises, examining data quality, spatial patterns, public transport integration, vehicle management, and business model viability.

### **Project 2: Generalized Cost Analysis – Saluzzo to Politecnico di Torino**
Detailed transport mode comparison study evaluating travel cost-benefit trade-offs for a representative commute route (62 km). Compares private car (Fiat Panda Cross 2021) vs. public transport (regional train) using standardized generalized cost methodology incorporating both monetary and time-value costs.

---

**Course:** Transport Innovation for a Sustainable, Inclusive and Smart Mobility  
**Institution:** Politecnico di Torino, Department DIST  
**Instructor:** Prof. Cristina Pronello  
**Study Period:** January 2024 – December 2025  
**Primary Study Areas:** Turin (Torino), Italy & Saluzzo–Torino Corridor

---

## Repository Structure

```
Transport_exercise/
├── Project_1_E-Scooter_Mobility_Analysis/
│   ├── CONSEGNA ESERCIZIO S337250/
│   │   ├── ESERCIZIO 1/
│   │   │   ├── unione.py                 # Data standardization and cleaning
│   │   │   └── _pycache_/
│   │   ├── ESERCIZIO 2/
│   │   │   ├── ex2.py                    # Origin-destination matrix construction
│   │   │   ├── trip_destinations.py      # Destination analysis
│   │   │   └── trip_origins.py           # Origin analysis
│   │   ├── ESERCIZIO 3/
│   │   │   ├── gestione_percorso.py      # Public transport route management
│   │   │   └── studio_percorsi.py        # Route analysis and overlap detection
│   │   ├── ESERCIZIO 4/
│   │   │   ├── costs.py                  # Cost structure analysis
│   │   │   └── ex4.py                    # Parking duration calculations
│   │   ├── Immagini/                     # Generated visualizations and maps
│   │   ├── gtt_gtfs/                     # Turin public transport GTFS data
│   │   ├── zone_statistiche_csv/         # Census zone boundaries and metadata
│   │   └── calculations.py               # Generalized cost analysis utilities
│   ├── Analysis-of-Shared-Electric-Scooter-Mobility-Services-in-Turin-Italy.pdf
│   └── Exercise-on-shared-mobility.pdf
│
├── Project_2_Generalized_Cost_Analysis/
│   ├── saluzzo_politecnico_analysis.py   # Main analysis script
│   ├── vehicle_data.py                   # Vehicle specifications (Fiat Panda)
│   ├── public_transport_data.py          # Train route and tariff data
│   ├── cost_calculations.py              # Cost structure functions
│   ├── sensitivity_analysis.py           # VOT and fuel price sensitivity
│   ├── visualizations/                   # Charts and comparative graphs
│   ├── outputs/
│   │   ├── cost_summary.csv              # Summary tables
│   │   └── sensitivity_results.csv       # Sensitivity analysis results
│   └── Generalised-Cost-Analysis.pdf     # Detailed report
│
└── README.md (this file)
```

---

# PROJECT 1: SHARED MOBILITY ANALYSIS IN TURIN

## Project Structure

[Original Project 1 structure diagram maintained]

## Exercises Overview

### Exercise 1: Data Quality Assessment & Descriptive Analysis

**Objectives:**
- Assess data quality across multiple operators
- Analyze temporal and spatial mobility trends
- Evaluate vehicle fleet utilization patterns

**Key Files:**
- `unione.py` – Standardizes heterogeneous data formats from Lime, Voi, and Bird into unified schema

**Methodology:**
- Data normalization: Maps operator-specific column names to standardized fields
- Quality filtering: Removes records with temporal inconsistencies, unrealistic speeds, out-of-bounds coordinates, and duplicates
- Temporal analysis: Reports mobility trends across years, months, and weeks

**Key Findings:**
- **2,337,009 valid trips** retained after cleaning (84.3% of 2,774,313 initial records)
- **Seasonal variation:** ~300% difference between peak (July–November) and off-season months
- **Operator fleet efficiency:** Lime (563 trips/vehicle) >> Bird (278) >> Voi (142)
- **Peak demand hours:** 15:00–19:00 (afternoon commute) and 08:00 (morning)

---

### Exercise 2: Origin-Destination (OD) Matrix Analysis

**Objectives:**
- Construct spatial OD matrices using Turin's administrative zoning
- Identify demand concentration patterns
- Compare peak vs. non-peak travel behavior

**Key Files:**
- `ex2.py` – Constructs 94×94 OD matrix from GPS coordinates
- `trip_origins.py` – Analyzes trip generation by zone
- `trip_destinations.py` – Analyzes trip attraction by zone

**Methodology:**
- **Zoning system:** 94 census zones (zone_statistiche) from Turin's Geoportale
- **Spatial assignment:** Geometric join operations map coordinates to zones
- **Temporal disaggregation:** Separate OD matrices for peak (08:00–09:00, 15:00–19:00) and non-peak periods
- **Visualization:** Heatmaps and flow maps rendered in QGIS

**Key Findings:**
- **Concentrated demand:** City center and adjacent zones account for majority of trips
- **Distance decay:** Trip frequency decreases with distance from city center
- **Operator dominance:** Lime dominates central zones; Bird and Voi show distributed patterns
- **Temporal variation:** Peak periods show concentrated demand; non-peak periods show geographic dispersal

---

### Exercise 3: Public Transport Integration & Competition Assessment

**Objectives:**
- Overlay e-scooter flows with Turin's public transport network
- Assess competitive vs. complementary relationships
- Identify first-mile/last-mile integration opportunities

**Key Files:**
- `studio_percorsi.py` – Route overlap detection with transit network
- `gestione_percorso.py` – Public transport GTFS data management

**Methodology:**
- **Data source:** GTT (Gruppo Torinese Trasporti) GTFS dataset (bus and tram routes)
- **Overlap classification:**
  - *Competitive trips:* Routes within transit zone corridors
  - *Complementary trips:* One endpoint in transit zone; other outside
  - *Independent trips:* Routes outside transit accessibility zones
- **Seasonal analysis:** Winter vs. summer patterns
- **Representative days:** Selected monthly typical weekdays (Tuesday–Thursday)

**Key Findings:**
- **Spatial overlap:** 99% of e-scooter trip origins and destinations near transit zones
- **User demographics:** E-scooter users predominantly young males; transit users represent broader population → different travel purposes
- **Integration potential:** Substantial first-mile/last-mile opportunities in peripheral residential areas
- **Seasonal effects:** Summer tourism and favorable weather increase e-scooter competition with transit

---

### Exercise 4: Parking Duration & Vehicle Management

**Objectives:**
- Calculate average parking duration by zone
- Identify rebalancing opportunities
- Assess operational efficiency

**Key Files:**
- `ex4.py` – Parking duration calculation and zone-level aggregation
- `costs.py` – Cost structure analysis supporting business model

**Methodology:**
- **Parking duration calculation:** Elapsed time between trip end and next trip start for each vehicle
- **Zone aggregation:** Average parking duration per zone (n=1,940,092 parking events)
- **Temporal patterns:** Parking duration variation by hour of day and day of week

**Key Findings:**
- **Average parking duration:** 332 minutes (5.54 hours) across all zones
- **Spatial patterns:** Central zones show lower durations (high turnover); periphery shows longer durations (lower demand)
- **Rebalancing window:** Peak hours (15:00–17:00) provide highest vehicle turnover opportunities
- **Operational implication:** High variation necessitates zone-specific rebalancing strategies

---

### Exercise 5: Business Model & Profitability Analysis

**Objectives:**
- Calculate revenue streams for each operator
- Estimate fixed and variable costs
- Assess long-term financial viability

**Key Files:**
- `costs.py` – Revenue and cost calculations
- `calculations.py` – Generalized cost utility functions

**Methodology:**
- **Revenue calculation:** Trip counts × operator tariffs (sourced from company websites)
- **Variable costs:** Electricity consumption, maintenance, battery replacement
- **Fixed costs:** Vehicle depreciation, insurance, depot operations, staff
- **Annual costs:** Amortization calculations using standard engineering economics methods

**Key Findings:**

| Operator | Trips/Vehicle | Market Share | Net Margin | Status |
|----------|---------------|--------------|-----------|--------|
| **Lime** | 563 | 57.8% | +14.83% | Profitable |
| **Bird** | 278 | 33.5% | -17.18% | Marginally loss-making |
| **Voi** | 142 | 8.7% | -340.17% | Structurally unviable |

- **Lime dominates:** High utilization spreads fixed costs across many rides
- **Bird near break-even:** Modest tariff or cost adjustments could achieve profitability
- **Voi structural challenge:** Low trip volume cannot absorb fixed costs; requires operational restructuring

---

## Data Sources & Assets (Project 1)

### Trip Data
- **Operators:** Lime (Jan 2024–Apr 2025), Bird (Jan 2024–Nov 2025), Voi (Jan 2024–Oct 2025)
- **Records:** 2,337,009 valid trips (after cleaning)
- **Fields:** Trip ID, vehicle ID, start/end times, origin/destination coordinates, distance, duration, battery levels

### Spatial Data
- **Census zones:** `zone_statistiche_csv/` – 94 administrative zones with boundaries and socioeconomic metadata
- **Public transport:** `gtt_gtfs/` – GTFS dataset for Turin bus and tram network
- **Base map:** OpenStreetMap (used for QGIS visualizations)

### Generated Outputs
- **OD matrices:** Excel files with 94×94 matrices for all-day, peak, and non-peak periods
- **Maps:** Heatmaps (origins/destinations), flow maps (OD patterns), parking duration choropleth
- **Figures:** Temporal trend charts, operator comparisons, cost breakdowns

---

## Technology Stack (Project 1)

**Programming Language:** Python 3.x

**Key Libraries:**
- **Data processing:** Pandas, NumPy (handling large CSV files with chunking to avoid memory errors)
- **Spatial analysis:** GeoPandas, Shapely (geometric operations, zone assignments)
- **Visualization:** Matplotlib, Folium (interactive maps)
- **GIS integration:** QGIS (map rendering and layer management)
- **Time series:** Standard datetime operations for temporal disaggregation

**Tools:**
- **Git/GitHub:** Version control and collaboration
- **VS Code:** Development environment
- **QGIS:** Geospatial visualization and spatial analysis
- **Geoportale Piemonte:** Data source for census zones and GTFS

---

## How to Run (Project 1)

### Prerequisites
```bash
pip install pandas numpy geopandas shapely matplotlib folium
```

### Data Setup
1. Place operator CSV files in project directories
2. Ensure census zone shapefiles are in `zone_statistiche_csv/`
3. Confirm GTFS data is in `gtt_gtfs/`

### Execute Exercises

**Exercise 1 – Data Cleaning:**
```bash
python CONSEGNA\ ESERCIZIO\ S337250/ESERCIZIO\ 1/unione.py
# Outputs standardized, cleaned dataset
```

**Exercise 2 – OD Matrix Construction:**
```bash
python CONSEGNA\ ESERCIZIO\ S337250/ESERCIZIO\ 2/ex2.py
# Outputs OD matrices and zone assignment statistics
```

**Exercise 3 – Public Transport Overlap:**
```bash
python CONSEGNA\ ESERCIZIO\ S337250/ESERCIZIO\ 3/studio_percorsi.py
# Outputs overlap classification and spatial statistics
```

**Exercise 4 – Parking Duration:**
```bash
python CONSEGNA\ ESERCIZIO\ S337250/ESERCIZIO\ 4/ex4.py
# Outputs zone-level parking duration statistics and maps
```

**Exercise 5 – Business Model Analysis:**
```bash
python CONSEGNA\ ESERCIZIO\ S337250/ESERCIZIO\ 4/costs.py
# Outputs revenue, cost, and profitability calculations
```

### Memory Management
For large CSV files, scripts implement `chunksize` parameter in `pd.read_csv()` to prevent out-of-memory errors:
```python
df = pd.read_csv('large_file.csv', chunksize=100000)
for chunk in df:
    # Process chunk
```

---

## Key Insights & Recommendations (Project 1)

### Market Dynamics
- **Lime's dominance:** Superior fleet utilization (563 trips/vehicle) and profitability (14.83% margin) indicate operational excellence and customer preference
- **Multi-operator fragmentation:** Bird and Voi struggle with lower utilization; market consolidation or operational restructuring likely

### Urban Mobility Integration
- **First-mile/last-mile opportunity:** Significant potential to position e-scooters as complementary to public transit, particularly from residential areas to transit nodes
- **Congestion risk:** High concentration in city center suggests need for zone-specific parking policies and rebalancing strategies
- **Seasonal optimization:** Winter demand is 70% lower than summer; consider seasonal fleet sizing

### Operational Efficiency
- **Rebalancing window:** Peak afternoon hours (15:00–17:00) provide highest turnover; prioritize rebalancing during these windows
- **Peripheral zones:** Lower utilization in suburbs indicates either demand constraints or service availability issues; targeted marketing or zone expansion warranted

---

# PROJECT 2: GENERALIZED COST ANALYSIS – SALUZZO TO POLITECNICO DI TORINO

## Project Overview

This project conducts a comprehensive transport mode comparison for a representative regional commute route using standardized generalized cost methodology. The analysis evaluates the Saluzzo → Politecnico di Torino corridor (62 km) comparing two transport modes: private car (Fiat Panda Cross 2021) and regional public transport (train).

**Route:** Saluzzo (Cuneo Province) → Torino Porta Susa → Politecnico di Torino  
**Distance:** 62 km (one-way)  
**Analysis Date:** December 2025  
**Reference Value of Time:** €20/hour (standard for work/study trips in Italy)

---

## Methodology

### Generalized Cost Framework

The analysis employs the industry-standard **generalized cost (GC)** formula:

```
GC = C_money + VOT × t_trip

where:
  C_money = monetary cost of trip (€)
  VOT = Value of Time (€/hour)
  t_trip = total door-to-door travel time (hours)
```

This approach integrates both financial and temporal costs, allowing direct comparison of transport modes with different cost structures.

**Time Value Assumptions:**
- VOT = €20/hour (standard for commuting/study-related travel)
- Equivalent: €0.333/minute, €480/day (8 hours)

---

## Mode-Specific Analysis

### Mode 1: Private Car – Fiat Panda Cross 2021

#### Vehicle Specifications
| Parameter | Value | Unit |
|-----------|-------|------|
| Make/Model | Fiat Panda Cross | - |
| Year | 2021 | - |
| Engine | 1.0L Mild Hybrid | - |
| Power | 70 hp / 52 kW | - |
| Fuel type | Petrol | - |
| WLTP Consumption | 5.6 | L/100 km |
| **Effective consumption** | **17.86** | **km/L** |

#### Cost Structure

**Fixed Annual Costs:**
| Cost Item | Amount | Notes |
|-----------|--------|-------|
| RCA Insurance | €450 | Young driver in Italy |
| Property Tax (Bollo) | €150 | Vehicle ≤1000cc |
| Revision/Maintenance | €200 | Regular check-ups |
| Garage/Parking | €0 | On-street parking available |
| **Total Fixed** | **€800** | **per year** |

**Annual Depreciation (10-year vehicle lifetime):**
- Purchase price: €15,000
- Residual value (10 years): €6,000 (40% residual)
- Amortization rate: 5%
- **Calculated annual depreciation: €1,465.50**

**Variable Annual Costs:**
| Cost Item | Amount | Notes |
|-----------|--------|-------|
| Tyre replacement | €120 | ~€600 every 5 years |
| Engine oil & fluids | €60 | Regular changes |
| Repairs & maintenance parts | €200 | Wear items, minor repairs |
| **Total Variable** | **€380** | **per year** |

**Total Annual Costs:** €800 + €1,465.50 + €380 = **€2,645.50/year**

**Cost Per Kilometre:**
- Average annual mileage: 15,000 km
- Cost per km: €2,645.50 ÷ 15,000 = **€0.1764/km**
- Fuel cost: 5.6 L/100 km × €1.70/L = **€0.0952/km**
- **Total cost per km: €0.2716/km**

#### Trip-Specific Cost (Saluzzo → Politecnico)

| Component | Calculation | Result |
|-----------|-------------|--------|
| Distance | 62 km | - |
| Monetary cost | 62 km × €0.2716/km | **€16.83** |
| Travel time | 62 km @ ~53 km/h avg | **1 h 15 min (1.25 h)** |
| Time cost | 1.25 h × €20/h | **€25.00** |
| **Generalized Cost** | €16.83 + €25.00 | **€41.83** |

---

### Mode 2: Public Transport – Regional Train

#### Route Description
**Path:** Saluzzo → Savigliano → Torino Porta Susa → Politecnico (walking)

#### Ticket Costs
| Leg | Operator | Cost | Notes |
|-----|----------|------|-------|
| Saluzzo → Savigliano | Trenitalia Regional | €3.20 | 18 km, ~18 min |
| Savigliano → Torino Porta Susa | Trenitalia Regional | €6.40 | 47 km, ~48 min |
| **Total ticket cost** | - | **€9.60** | - |

#### Door-to-Door Time Breakdown
| Segment | Duration | Notes |
|---------|----------|-------|
| Access to station | 5 min | Walking from home |
| Wait for train #1 | 10 min | Average inter-train time |
| Saluzzo → Savigliano | 18 min | On-train travel |
| Transfer wait | 8 min | Platform + connection time |
| Savigliano → Torino Porta Susa | 48 min | On-train travel |
| Exit + egress | 2 min | Platform departure |
| Walk to Politecnico | 10 min | ~800–1000m from Porta Susa |
| **Total travel time** | **101 min (1.683 h)** | **Door-to-door** |

#### Trip Cost (Saluzzo → Politecnico)

| Component | Calculation | Result |
|-----------|-------------|--------|
| Ticket cost | 2 legs | **€9.60** |
| Travel time | 101 minutes | **1 h 41 min (1.683 h)** |
| Time cost | 1.683 h × €20/h | **€33.66** |
| **Generalized Cost** | €9.60 + €33.66 | **€43.26** |

---

## Comparative Analysis

### Summary Comparison

| Metric | Private Car (Panda) | Public Transport (Train) | Difference |
|--------|-----------------|-------------------|-----------|
| **Monetary Cost** | €16.83 | €9.60 | +€7.23 (car higher) |
| **Travel Time** | 1 h 15 min | 1 h 41 min | −26 min (car faster) |
| **Time Cost** | €25.00 | €33.66 | −€8.66 (car cheaper) |
| **Generalized Cost** | €41.83 | €43.26 | **−€1.94 (car cheaper)** |
| **GC Advantage** | Private car by 4.5% | - | - |

### Key Findings

1. **Private car is marginally more economical** (€1.94 cheaper per trip)
   - Car GC: €41.83 vs. Train GC: €43.26
   - Advantage: 4.5% cost saving with private car
   - Break-even: Minimal margin suggests both modes are cost-competitive

2. **Time advantage strongly favors car** (26-minute saving)
   - Car door-to-door: 1 h 15 min
   - Train door-to-door: 1 h 41 min
   - Time saving justifies slightly higher monetary cost
   - Annual time savings (40 trips/month): ~173 hours/year

3. **Cost-benefit trade-off:**
   - Car: Lower total time but higher direct costs
   - Train: Lower monetary cost but longer overall journey
   - Choice depends on time value and schedule flexibility

---

## Sensitivity Analysis

### Sensitivity to Value of Time

How generalized cost changes with different VOT assumptions:

| VOT (€/h) | GC Car (€) | GC Train (€) | Cheaper Option |
|-----------|-----------|-------------|----------------|
| €10 | €28.82 | €27.63 | **Train** |
| €15 | €35.07 | €35.44 | **Car** (marginal) |
| €20 | €41.83 | €43.26 | **Car** |
| €25 | €47.57 | €51.09 | **Car** |
| €30 | €53.82 | €58.91 | **Car** |

**Interpretation:**
- At VOT ≥ €15/hour, car becomes optimal
- Train only competitive at low VOT (€10/hour or below)
- Low VOT typical for leisure trips; work/study trips use higher VOT
- Commuters with high time valuation should prefer car

---

### Sensitivity to Fuel Price

Impact of fuel price variations on car GC (VOT held at €20/h):

| Fuel Price (€/L) | Fuel Cost/Trip (€) | Total Money Cost (€) | GC Car (€) |
|------------------|------------------|------------------|-----------|
| €1.30 | €4.33 | €13.56 | €38.56 |
| €1.55 | €5.35 | €14.78 | €39.78 |
| €1.70 | €5.87 | €16.32 | €41.83 |
| €1.90 | €6.54 | €17.00 | €42.00 |
| €2.10 | €7.24 | €17.70 | €42.70 |

**Interpretation:**
- 20% fuel price increase (€1.70 → €2.10) raises car GC to €42.70
- Car remains competitive even at elevated fuel prices
- Train relatively insensitive to fuel costs (stable at €43.26)

---

## Alternative Modes Evaluation

### Car Sharing
**Status:** Not available on Saluzzo → Torino route  
**Rationale:** Car sharing operates primarily in urban areas; regional routes lack infrastructure

### Bicycle / Bike Sharing
**Status:** Not feasible  
**Rationale:**
- Distance (62 km) prohibitive for daily cycling
- Estimated cycling time: 3–4 hours (unsustainable)
- Limited cycle path infrastructure
- Daily 124 km round-trip physically unrealistic

### E-Scooter / Micro-mobility
**Status:** Not feasible  
**Rationale:**
- Distance exceeds practical range (typical 30–50 km)
- Average speed ~25 km/h would require 2.5+ hours
- Limited charging infrastructure
- Italian law restricts e-scooter use to urban areas (highway prohibited)

---

## Recommendations & Decision Framework

### Choose Private Car if:
- ✓ Value of time is significant (work/study trips)
- ✓ Schedule flexibility desired; dislike timetable constraints
- ✓ Prefer comfort and door-to-door convenience
- ✓ Plan multiple trips per month (30+ trips/month justify fixed costs)
- ✓ Fuel prices remain stable or decline

### Choose Public Transport if:
- ✓ Value time at <€15/hour or view commute as relaxation time
- ✓ Want to reduce carbon footprint (trains: ~8 kg CO₂/trip vs. cars: ~31 kg CO₂/trip)
- ✓ Experience high fuel price volatility
- ✓ Prefer to avoid driving stress/fatigue
- ✓ Can productively use extra 26 minutes (work, study, leisure)

---

## Annual Cost Comparison (40 trips/month)

| Factor | Private Car | Public Transport |
|--------|------------|-----------------|
| **Annual trip cost** | ~€1,060 | ~€1,728 |
| **Carbon footprint/trip** | ~31 kg CO₂ | ~8 kg CO₂ |
| **Schedule flexibility** | High | Medium |
| **Convenience** | Excellent (door-to-door) | Good (time-dependent) |
| **Stress/Fatigue** | Moderate driving stress | Low (relaxing) |

**Annual savings with car:** €668/year (39% reduction) for regular commuting

---

## Hybrid Approach (Recommended)

For maximum flexibility and cost-efficiency:

1. **Daily commute (Mon–Fri):** Public transport
   - Rationale: Utilize travel time for work/study
   - Cost: €9.60 × 40 trips = €384/month

2. **Occasional return trips:** Private car for time-sensitive travel
   - Rationale: Leverage 26-minute time advantage when needed

3. **Strategic benefit:** 
   - Reduces annual parking permit costs
   - Minimizes cumulative fuel consumption
   - Balances cost-efficiency with flexibility

**Estimated annual savings:** €400–600 vs. car-only commuting

---

## Data Sources & Methodology References

### Vehicle Data (Fiat Panda Cross 2021)
- **Source:** Official Fiat technical specifications (2021 model)
- **Consumption:** WLTP certified (realistic combined driving)
- **Market value:** Verified through Italian automotive market data

### Public Transport Data
- **Source:** Trenitalia regional fare schedule (Regione Piemonte, December 2025)
- **Route:** Official timetables (Torino–Savigliano–Saluzzo line)
- **Walking time:** User-verified campus distance (Porta Susa → Politecnico)

### Assumptions Documented
1. No tolls (regional roads selected; no motorway access required)
2. Parking available without charge (on-street)
3. VOT: €20/hour (standard for commuting)
4. Distance: 62 km verified via Google Maps route planning
5. Traffic: Moderate urban/suburban; averaged in time estimates

---

## Technology Stack (Project 2)

**Programming Language:** Python 3.x

**Core Libraries:**
- **NumPy/Pandas:** Numerical calculations and sensitivity tables
- **Matplotlib:** Cost comparison charts and sensitivity graphs
- **DataFrame operations:** Cost breakdowns and scenario analysis

**Tools:**
- **Spreadsheet export:** CSV format for scenario modeling
- **Git/GitHub:** Version control and documentation
- **VS Code:** Development environment

---

## How to Run (Project 2)

### Prerequisites
```bash
pip install pandas numpy matplotlib
```

### Basic Analysis
```bash
python Project_2_Generalized_Cost_Analysis/saluzzo_politecnico_analysis.py
# Outputs: cost comparison, summary tables, GC results
```

### Sensitivity Analysis
```bash
python Project_2_Generalized_Cost_Analysis/sensitivity_analysis.py
# Outputs: VOT sensitivity tables, fuel price sensitivity
# Generates visualizations in visualizations/ directory
```

### Vehicle Cost Breakdown
```bash
python Project_2_Generalized_Cost_Analysis/cost_calculations.py
# Outputs: Annual costs, per-km costs, depreciation schedule
```

---

## Key Reports & Documentation

### Project 1 (E-Scooter Analysis)
1. **Exercise-on-shared-mobility.pdf** – Exercise specifications and requirements
2. **Analysis-of-Shared-Electric-Scooter-Mobility-Services-in-Turin-Italy.pdf** – Comprehensive analysis report with findings across all five exercises

### Project 2 (Generalized Cost Analysis)
3. **Generalised-Cost-Analysis.pdf** – Detailed methodology and findings for Saluzzo–Politecnico comparison

---

## Methodological Considerations

### Data Limitations & Assumptions

**Project 1 (E-Scooter):**
- Operator data variation in quality and completeness
- Lime data ends April 2025 (affects Q2 2025 analysis)
- Business model costs based on industry benchmarks
- User demographics require survey validation

**Project 2 (Generalized Cost):**
- Cost estimates use 2025 price levels
- VOT (€20/h) reflects Italian labor market averages
- Vehicle depreciation assumes typical ownership pattern
- Train schedule represents current timetable (may vary seasonally)

### Analytical Choices
- **Zone-level OD (Project 1):** Balances granularity vs. computational tractability
- **Representative days (Project 1):** Typical weekday selection minimizes weekend anomalies
- **Single VOT assumption (Project 2):** Sensitivity analysis demonstrates impact of variations

### Reproducibility
- All calculations deterministic and documented
- Code uses explicit parameters and documented assumptions
- Results reproducible given identical input data

---

## Future Extensions

### Project 1 (E-Scooter Analysis)
1. Demand forecasting using ARIMA/Prophet for seasonal prediction
2. Network optimization for fleet positioning and rebalancing
3. Integration with demographic data for user behavior modeling
4. Lifecycle carbon footprint assessment

### Project 2 (Generalized Cost Analysis)
1. Multi-scenario analysis (pricing changes, service improvements)
2. Dynamic routing algorithms incorporating real-time traffic
3. Carbon cost integration (external cost of emissions)
4. Expansion to alternative routes (motorway vs. regional roads)
5. Integration with PT fare card systems (monthly passes)

---

## Contact & References

**GitHub Repository:** https://github.com/s285305/Transport_exercise.git

**Course Instructor:**  
Prof. Cristina Pronello  
Politecnico di Torino  
DIST - Dipartimento Interateneo di Scienze, Progetto e Politiche del Territorio  
cristina.pronello@polito.it

### Key References

**Project 1 (Shared Mobility):**
- Papas et al. (2023). Comprehensive comparison of e-scooter sharing mobility: Evidence from 30 European cities. *Journal of Transport Geography*, 99, 103288.
- Tilahun et al. (2022). The use of shared mobility services in trips to public transit. *Transportation Research Record*, 2652(1), 47–56.
- Mouratidis, K. (2022). Bike-sharing, car-sharing, e-scooters, and Uber: Who are the shared mobility users? *Sustainable Cities and Society*, 86, 104161.
- Huo et al. (2021). Influence of the built environment on e-scooter sharing ridership. *Journal of Transport Geography*, 93, 103084.

**Project 2 (Generalized Cost Analysis):**
- Pronello, C. (2022). Innovative models to fund local public transport. Transport Research Conference, September 14, 2022.
- Transport Analysis Guidance (TAG). Generalized transport costs. UK Department for Transport, 2023.
- Ortúzar, J. de D., & Willumsen, L. G. (2011). *Modelling transport* (4th ed.). Wiley.

---

## License

Educational use for Politecnico di Torino course. Operator data subject to respective terms of service. Proprietary analysis methodology documented in course materials.

**Last Updated:** December 2025  
**Repository Owner:** s285305 (Politecnico di Torino)
