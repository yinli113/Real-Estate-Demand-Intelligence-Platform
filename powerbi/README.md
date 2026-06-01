# Power BI — Real Estate Demand Intelligence

# TL;DR

A 4-page report that tells a story: **Page 1 hooks** the agency leadership with the big picture (where is demand, what converts, what's trending), then three **drill-through pages** explain the *why* by Suburb, by Time, and by Property/Buyer. All visuals sit on the Gold **star schema** (`fact_property_view` + `dim_*`), so filters and drill-through "just work".

---

## 0. Before you build — the semantic model

Import these Gold tables and wire the relationships (all **one-to-many**, single direction, from dimension → fact):

| From (dimension) | Key | To (fact) | Key |
|---|---|---|---|
| `dim_date` | `date_key` | `fact_property_view` | `date_key` |
| `dim_time` | `time_key` | `fact_property_view` | `time_key` |
| `dim_property` | `property_key` | `fact_property_view` | `property_key` |
| `dim_suburb` | `suburb_key` | `fact_property_view` | `suburb_key` |
| `dim_visitor_geo` | `visitor_geo_key` | `fact_property_view` | `visitor_geo_key` |
| `dim_price_band` | `price_band_key` | `fact_property_view` | `price_band_key` |
| `dim_device` | `device_key` | `fact_property_view` | `device_key` |

Tips:
- Mark `dim_date` as the official **Date table** (Table tools → Mark as date table → `date`). This unlocks time-intelligence DAX.
- Set **Data category** on geo columns so maps render: `dim_suburb[suburb_latitude]` = Latitude, `dim_suburb[suburb_longitude]` = Longitude; same for `dim_visitor_geo`. Set `dim_suburb[suburb]` = City/Place, `dim_visitor_geo[visitor_city]` = City, `dim_visitor_geo[visitor_state]` = State or Province.
- The `gold_*` mart tables are pre-aggregated answers. You don't strictly need them once the star schema is in place, but they're handy for quick single-visual tiles. **Build the report on the star schema** for full slice/drill flexibility.

> **`enquiry_flag` data type:** the DAX below assumes it's a **Boolean** (`TRUE`/`FALSE`). If Power BI imported it as **Text** ("true"/"false"), replace `= TRUE()` with `= "true"` in the measures.

---

## 1. Measures — paste these first

Create one blank table called **`_Measures`** (Home → Enter data → name it `_Measures`, load, delete the dummy column) and put every measure there. This keeps them tidy and out of the data tables.

### Core volume & engagement
```dax
Total Views = COUNTROWS ( fact_property_view )

Unique Sessions = DISTINCTCOUNT ( fact_property_view[session_id] )

Total Enquiries =
CALCULATE ( [Total Views], fact_property_view[enquiry_flag] = TRUE () )

Total Favourites =
CALCULATE ( [Total Views], fact_property_view[favorite_flag] = TRUE () )

Avg View Duration (sec) = AVERAGE ( fact_property_view[view_duration_sec] )

Total View Duration (min) =
DIVIDE ( SUM ( fact_property_view[view_duration_sec] ), 60 )

Conversion Rate = DIVIDE ( [Total Enquiries], [Total Views] )

Enquiry Rate Label = FORMAT ( [Conversion Rate], "0.0%" )
```

### Engagement score (used to rank "most engaged")
"Engaged" = people actually spending time and acting, not just clicking. This blends duration with enquiries so a suburb with deep, action-taking interest beats one with lots of shallow clicks.
```dax
Engagement Score =
VAR DurationMinutes = DIVIDE ( SUM ( fact_property_view[view_duration_sec] ), 60 )
VAR EnquiryWeight = [Total Enquiries] * 5
VAR FavouriteWeight = [Total Favourites] * 3
RETURN DurationMinutes + EnquiryWeight + FavouriteWeight
```

### Price
```dax
Avg Engaged Price =
CALCULATE (
    AVERAGE ( fact_property_view[price] ),
    fact_property_view[enquiry_flag] = TRUE ()
)

Avg Viewed Price = AVERAGE ( fact_property_view[price] )
```

### Geo demand split
```dax
Interstate Views =
CALCULATE ( [Total Views], fact_property_view[is_interstate_view] = TRUE () )

Overseas Views =
CALCULATE ( [Total Views], fact_property_view[is_overseas_view] = TRUE () )

Interstate View Share = DIVIDE ( [Interstate Views], [Total Views] )

Overseas View Share = DIVIDE ( [Overseas Views], [Total Views] )
```

### Trend / time-intelligence (needs `dim_date` marked as date table)
```dax
Views Last 30 Days =
CALCULATE (
    [Total Views],
    DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -30, DAY )
)

Views Prev Month =
CALCULATE ( [Total Views], DATEADD ( dim_date[date], -1, MONTH ) )

MoM View Growth % =
VAR Prev = [Views Prev Month]
RETURN DIVIDE ( [Total Views] - Prev, Prev )
```

### Dynamic "Top N" labels for the hero cards (Page 1)
These return the **name** of the top performer so you can drop them straight into a Card visual.
```dax
Most Visited Suburb =
CALCULATE (
    SELECTEDVALUE ( dim_suburb[suburb] ),
    TOPN ( 1, VALUES ( dim_suburb[suburb] ), [Total Views], DESC )
)

Most Engaged Suburb =
CALCULATE (
    SELECTEDVALUE ( dim_suburb[suburb] ),
    TOPN ( 1, VALUES ( dim_suburb[suburb] ), [Engagement Score], DESC )
)

Most Visited Property =
CALCULATE (
    SELECTEDVALUE ( dim_property[property_id] ),
    TOPN ( 1, VALUES ( dim_property[property_id] ), [Total Views], DESC )
)

Most Engaged Property =
CALCULATE (
    SELECTEDVALUE ( dim_property[property_id] ),
    TOPN ( 1, VALUES ( dim_property[property_id] ), [Engagement Score], DESC )
)
```

---

## 2. Page 1 — Executive Overview (the hook)

**Page name:** `Overview`
**Purpose:** in 5 seconds the agency principal sees where demand is, what's hot, and whether interest is rising. No detail yet — just the headline.

**Layout (top → bottom):**

| Zone | Visual type | Fields / Measures | Notes |
|---|---|---|---|
| KPI strip (5 cards) | **Card** ×5 | `[Most Visited Suburb]`, `[Most Engaged Suburb]`, `[Most Visited Property]`, `[Most Engaged Property]`, `[Avg Engaged Price]` | Row of cards across the top. Format Avg Engaged Price as currency. |
| Secondary KPIs | **Card** ×3 (smaller) | `[Total Views]`, `[Conversion Rate]`, `[Interstate View Share]` | Gives context to the hero cards. |
| Left map | **Map** (bubble) | Location = `dim_suburb[suburb_latitude]` + `[suburb_longitude]`; Bubble size = `[Total Views]`; Tooltip = `[Engagement Score]`, `[Conversion Rate]` | "Where are the listings people look at?" |
| Right map | **Map** (bubble) | Location = `dim_visitor_geo[visitor_latitude]` + `[visitor_longitude]`; Bubble size = `[Total Views]`; Legend = `dim_visitor_geo[visitor_state]` | "Where do the buyers come from?" — the interstate/overseas story. |
| Bottom trend | **Line chart** | Axis = `dim_date[date]`; Lines (Y) = `[Total Views]` and `[Avg View Duration (sec)]` (secondary axis) | Shows the demand trend + how deeply people engage over time. |
| Right of trend | **Line/area** | Axis = `dim_date[date]`; Y = `[Total Enquiries]` | Conversion trend next to view trend. |

**Slicers (top-right of page):** `dim_date[date]` (Between/relative date), `dim_property[property_type]`, `dim_visitor_geo[visitor_state]`. Add these to a **Sync slicers** group so they carry across all pages.

**Drill-through OUT of this page:**
- Right-click a bubble on the **suburb map** → *Drill through → Suburb Detail*.
- Right-click a point on the **trend line** → *Drill through → Time & Timing*.
- Right-click a **property card / any property visual** → *Drill through → Property & Buyer*.

---

## 3. Page 2 — Suburb Detail (drill-through)

**Page name:** `Suburb Detail`
**Drill-through filter field:** drag `dim_suburb[suburb]` into the **Drill through** well. (Power BI auto-adds the back button.)
**Purpose:** "We landed on Richmond — why does it get huge views but few enquiries?"

| Visual type | Fields / Measures | Answers |
|---|---|---|
| **Card** ×3 | `[Total Views]`, `[Conversion Rate]`, `[Avg Engaged Price]` | Headline for the chosen suburb. |
| **Clustered bar** | Axis = `dim_property[property_type]`; Value = `[Total Views]` | Which property types people want here (Q2). |
| **Clustered column** | Axis = `dim_price_band[price_range]`; Values = `[Total Views]`, `[Conversion Rate]` (line) | Which price bands engage / convert (Q3). |
| **Donut** | Legend = `dim_visitor_geo[visitor_state]`; Value = `[Total Views]` | Local vs interstate demand for this suburb (Q1/Q10). |
| **KPI / Gauge** | `[Conversion Rate]` vs target | The "conversion gap" flag (Q4) — low = investigate pricing/photos. |
| **Table** | Rows = `dim_property[property_id]`, `dim_property[bedrooms]`; Values = `[Total Views]`, `[Total Enquiries]`, `[Avg Viewed Price]` | The actual listings driving the numbers. |

**Pro tip — the conversion-gap callout:** add a card with this and colour it red when low:
```dax
Conversion Gap Flag =
IF (
    [Total Views] >= 500 && [Conversion Rate] < 0.02,
    "⚠ High interest, low conversion — review price/photos",
    "OK"
)
```

---

## 4. Page 3 — Time & Timing (drill-through)

**Page name:** `Time & Timing`
**Drill-through filter field:** `dim_date[date]` (or `dim_date[month_name]` for a broader landing).
**Purpose:** "When should we schedule promotions / open homes?" (Q6, Q8).

| Visual type | Fields / Measures | Answers |
|---|---|---|
| **Line chart** | Axis = `dim_date[date]`; Y = `[Total Views]`, `[MoM View Growth %]` | Trend + momentum (Q6 — uses LAG logic, now in DAX). |
| **Column chart** | Axis = `dim_time[hour]`; Value = `[Total Views]`; Legend = `dim_property[property_type]` | Hour-of-day demand — apartments at 8pm vs houses at 11am (Q8). |
| **Matrix / heatmap** | Rows = `dim_date[day_of_week]`; Columns = `dim_time[time_period]`; Values = `[Total Views]` (conditional-format background) | Best day × part-of-day to advertise. |
| **Card** | `[Views Last 30 Days]`, `[MoM View Growth %]` | Recent momentum headline. |
| **Bar (trending suburbs)** | Axis = `dim_suburb[suburb]`; Value = `[MoM View Growth %]`; Top-N filter = 10 | Suburbs heating up — "advertise before competitors react". |

---

## 5. Page 4 — Property & Buyer (drill-through)

**Page name:** `Property & Buyer`
**Drill-through filter field:** `dim_property[property_id]` (and works from `property_type` too).
**Purpose:** Match the right creative to the right buyer (Q5, Q7, Q9).

| Visual type | Fields / Measures | Answers |
|---|---|---|
| **Card** ×3 | `[Total Views]`, `[Total Enquiries]`, `[Avg Engaged Price]` | Property headline. |
| **Stacked bar** | Axis = `dim_visitor_geo[visitor_state]`; Legend = `dim_property[property_type]`; Value = `[Total Views]` | Which regions prefer apartments vs houses (Q7). |
| **Map** | Location = `dim_visitor_geo[visitor_latitude]`/`[visitor_longitude]`; Size = `[Total Views]`; filter `dim_property[is_luxury] = TRUE` | Where luxury demand comes from — overseas premium buyers (Q5). |
| **Table** | Rows = `fact_property_view[session_id]`, `dim_suburb[suburb]`; Value = `[Total Views]`; filter `[Total Views] >= 5` | High-intent repeat sessions (Q9) — recommend similar listings. |
| **Donut** | Legend = `dim_device[device_type]`; Value = `[Total Views]` | Mobile vs desktop — informs ad format. |

---

## 6. Drill-through map (how the pages connect)

```
                ┌─────────────────────────────┐
                │   Page 1: Overview (hook)    │
                │  cards • 2 maps • trend line │
                └───────┬───────┬───────┬──────┘
        right-click     │       │       │     right-click
        suburb map      │       │       │     property visual
                        ▼       ▼       ▼
        ┌───────────────┐ ┌───────────┐ ┌────────────────────┐
        │ Page 2:       │ │ Page 3:   │ │ Page 4:            │
        │ Suburb Detail │ │ Time &    │ │ Property & Buyer   │
        │ (by suburb)   │ │ Timing    │ │ (by property/type) │
        └───────────────┘ └───────────┘ └────────────────────┘
```
Each drill-through page auto-gets a **back button** (top-left) so the audience returns to the hook. Keep the synced slicers visible on every page so context (date range, state) follows the user.

---

## 7. Design / storytelling tips (from a reporting standpoint)
- **One message per page.** Page 1 = "demand is here and rising"; the rest answer "why / when / who".
- **Top-left is prime real estate** — put the single most important number (Total Views or the trend) there; eyes start top-left.
- **Colour with meaning, sparingly.** Use one accent colour for "good/high" and red only for the conversion-gap warning, so red always means "act here".
- **Consistent number formatting** — % to 1 decimal, currency with no cents, big counts with thousands separators.
- **Tooltips do the explaining** — add `[Conversion Rate]` and `[Avg Engaged Price]` to map/chart tooltips so detail is on-hover, not cluttering the canvas.
- **Title each visual as a sentence/question** ("Where do our buyers come from?") instead of a field name — it guides a non-technical audience through the story.
