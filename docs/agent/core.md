# 'core/context.py' Documentation

## File Purpose
'context.py' centralizes and standardizes all business data for AUTO. It ensures every analytical function works with **clean, validated, and enriched datasets** in memory. This is the single source of truth for sales, marketing, inventory, and unit economics data.

---

## Responsibilities
- Load all business CSV data into memory once.
- Validate each dataset against a required schema.
- Parse date columns for consistent datetime operations.
- Enrich sales data with unit-leve costs for profit calculations.
- Precompute daily aggregates for quick baseline and trend queries.
- Provide a single 'DataContext' objec holding all processed data.

---

## Core Classes and Functions

**'DataContext'**
- Holds all in-memory datasets:
  - 'sales', 'marketing', 'inventory', 'unit' -> raw CSV data.
  - 'sales_enriched' -> sales data with unit costs added.
  - 'daily' -> precomputed daily revenue and units totals.
- Enables deterministic and fast access to business data for all AUTO analytics.

**'_read_csv(path)'**
- Reads a CSV file from disk if it exists.
- Returns an empty DataFrame if the file is missing or empty.

**'_validate(df, name)'**
- Checks that the DataFrame contains all required columns for its dataset type.
- Raises an error if any column is missing to prevent downstream calculations errors.

**'load_context(data_dir="data")'**
- Main loader functions returning a 'DataContext' instance.
- Steps performed:
  1. Reads all CSV files ('sales', 'marketing', 'inventory', 'unit_economics').
  2. Validates each CSV against required schema.
  3. Parses all date columns to 'datetime'.
  4. Computes 'unit_cost' = 'cogs + packaging_cost + logistics_cost'.
  5. Enriches 'sales' with 'unit_cost' for profit calculations ('sales_enriched').
  6. Precomputes daily totals ('daily') for fast baseline queries.

---

## Design Decisions
- All data loaded once into memory to ensure deterministic calculations.
- Sales enrichment and daily aggregates precomputed to speed up analysis.
- Validation ensures that missing or malformed CSVs are caught early.
- Date parsing done once to avoid inconsistent datetime handling in analytics functions.

---

## What this file does NOT do
- Does not compute profit, margin, or other metrics (done in 'analytics/').
- Does not perform reasoning or recommendations (done in 'decisions/').
- Does not interact with the LLM or any external system.
- Purely deterministic and data-focused.