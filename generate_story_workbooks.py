#!/usr/bin/env python3
"""
Generate sample Tableau workbooks for Story 2.2 (Sorting) and Story 2.3 (Filtering).
Outputs to examples/generated_workbooks/
"""

import os
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler

DATASET   = "examples/sample_datasets/sales_sample.csv"
TEMPLATE  = "templates/base_template.twb"
OUT_DIR   = "examples/generated_workbooks"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    profiler = SchemaProfiler()
    schema   = profiler.profile_dataset(DATASET)
    compiler = TableauXMLCompiler(TEMPLATE)

    print("=" * 60)
    print("Generating Story 2.2 – Sorting & Ordering")
    print("=" * 60)

    blueprint_22 = {
        "sheets": [
            {
                "name": "Top Products by Sales (DESC)",
                "column_field": "product",
                "row_field": "sales",
                "mark_type": "Bar",
                "sort": {
                    "field": "sales",
                    "direction": "DESC",
                    "type": "field"
                }
            },
            {
                "name": "Lowest Profit by Region (ASC)",
                "column_field": "region",
                "row_field": "profit",
                "mark_type": "Bar",
                "sort": {
                    "field": "profit",
                    "direction": "ASC",
                    "type": "field"
                }
            },
            {
                "name": "Categories A-Z",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar",
                "sort": {
                    "field": "category",
                    "direction": "ASC",
                    "type": "alphabetical"
                }
            },
        ]
    }

    out_22 = os.path.join(OUT_DIR, "story_2_2_sorting.twb")
    result = compiler.compile_workbook(
        blueprint=blueprint_22,
        output_path=out_22,
        dataset_path=DATASET,
        schema=schema,
    )
    if result["success"]:
        print(f"✅  {out_22}  ({result['sheets_created']} sheets)")
    else:
        print(f"❌  Failed to generate story_2_2_sorting.twb")

    print()
    print("=" * 60)
    print("Generating Story 2.3 – Basic Filtering")
    print("=" * 60)

    blueprint_23 = {
        "sheets": [
            {
                "name": "USA Sales Only",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar",
                "filters": [
                    {"field": "region", "operator": "=", "values": ["USA"]}
                ]
            },
            {
                "name": "USA and Canada Sales",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar",
                "filters": [
                    {"field": "region", "operator": "=", "values": ["USA", "Canada"]}
                ]
            },
            {
                "name": "USA – Top Products (Filter + Sort)",
                "column_field": "product",
                "row_field": "sales",
                "mark_type": "Bar",
                "filters": [
                    {"field": "region", "operator": "=", "values": ["USA"]}
                ],
                "sort": {
                    "field": "sales",
                    "direction": "DESC",
                    "type": "field"
                }
            },
        ]
    }

    out_23 = os.path.join(OUT_DIR, "story_2_3_filtering.twb")
    result = compiler.compile_workbook(
        blueprint=blueprint_23,
        output_path=out_23,
        dataset_path=DATASET,
        schema=schema,
    )
    if result["success"]:
        print(f"✅  {out_23}  ({result['sheets_created']} sheets)")
    else:
        print(f"❌  Failed to generate story_2_3_filtering.twb")

    print()
    print("Open these files in Tableau Desktop to validate visually.")


if __name__ == "__main__":
    main()
