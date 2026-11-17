# Data

The raw data files are not stored in this repository because of their size. Download each one into this `data/` folder using the filenames below, which the notebook expects.

| Expected filename | Dataset | Where to get it |
|---|---|---|
| `DOHMH_MenuStat__Historical_.csv` | MenuStat (Historical), NYC Department of Health and Mental Hygiene | [NYC Open Data](https://data.cityofnewyork.us/d/qgc5-ecnb): Export, then CSV |
| `FMAP.xlsx` | Food-at-Home Monthly Area Prices (F-MAP), sheet `Data` | [USDA ERS F-MAP page](https://www.ers.usda.gov/data-products/food-at-home-monthly-area-prices) |
| `table-8-recommended.xlsx` | Table 8, recommended densities and 2017–18 data, sheet `recommendation and 2017-18 data` | [USDA ERS Food Consumption, Nutrient Intakes, and Diet Quality](https://www.ers.usda.gov/data-products/food-consumption-nutrient-intakes-and-diet-quality) |

If a downloaded file has a different name or sheet name, rename it or update the matching `load_*` call in the notebook.
