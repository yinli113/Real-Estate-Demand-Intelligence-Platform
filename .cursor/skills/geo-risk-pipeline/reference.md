# Real Estate Demand Intelligence — Reference

## Gold tables → business questions

| Table | Question |
|-------|----------|
| gold_suburb_interest | Which suburbs get interstate/overseas views? |
| gold_property_type_by_suburb | Top property type per suburb? |
| gold_price_engagement | Which price ranges convert best? |
| gold_conversion_gaps | High views, low enquiries (e.g. Richmond)? |
| gold_property_trends | MoM suburb growth (LAG)? |
| gold_region_type_preference | NSW vs VIC: apartment vs house? |
| gold_repeat_interest | Sessions with 5+ views (purchase intent)? |
| gold_interstate_flow | visitor_state → listing_state flows |

## Sample files
- listings.csv (160 properties)
- property_views_500.csv (optional quick smoke test)
- property_views_5k.csv (default Fabric demo)
- property_views_5k.csv (test)

## Fabric lakehouses
lh_realestate_dev | lh_realestate_test | lh_realestate_prod


## Live IPstack controls

- `MOCK_IPSTACK=True`: read fixture JSON, safest for demos.
- `MOCK_IPSTACK=False`: call live API.
- `MAX_IPSTACK_CALLS=5`: cap live calls while testing.
- `FORCE_REFRESH_IPSTACK=False`: skip IPs already in `silver_ip_dim`.
