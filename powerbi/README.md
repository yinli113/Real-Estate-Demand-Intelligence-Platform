# Power BI — Real Estate Demand Intelligence

## Decision-support pages

1. **Interstate demand** — `gold_suburb_interest` + `gold_interstate_flow` (Sydney → Melbourne suburbs)
2. **Suburb conversion gaps** — `gold_conversion_gaps` (high views, low enquiries e.g. Richmond)
3. **Price range engagement** — `gold_price_engagement` (500k–700k vs 2M+)
4. **Property trends** — `gold_property_trends` (MoM growth with LAG)
5. **Regional preferences** — `gold_region_type_preference` (apartment vs house by visitor state)
6. **High-intent sessions** — `gold_repeat_interest` (repeat views ≥ 5)

## Key measures

```dax
Interstate View Share = DIVIDE(SUM(gold_suburb_interest[interstate_views]), SUM(gold_suburb_interest[total_views]))
Conversion Rate = DIVIDE(SUM(gold_conversion_gaps[enquiries]), SUM(gold_conversion_gaps[views]))
MoM Growth = DIVIDE([This Month Views] - [Previous Month Views], [Previous Month Views])
```

## Semantic model

Fact: `gold_suburb_interest`, `gold_conversion_gaps`, `gold_property_trends`
Supporting: `gold_price_engagement`, `gold_repeat_interest`, `gold_interstate_flow`
