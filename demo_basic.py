#!/usr/bin/env python3
"""
Basic demo of Tableau workbook generation WITHOUT LLM.
Uses a hardcoded blueprint to test the core pipeline.
"""

import os
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler

def main():
    print("=" * 60)
    print("Tableau MCP Server - Basic Demo (No LLM)")
    print("=" * 60)
    
    # Step 1: Profile dataset
    print("\n📊 Step 1: Profiling dataset...")
    dataset_path = "examples/sample_datasets/sales_sample.csv"
    
    profiler = SchemaProfiler()
    schema = profiler.profile_dataset(dataset_path)
    
    print(f"✅ Dataset profiled successfully!")
    print(f"   - Dimensions: {', '.join([d['name'] for d in schema['dimensions']])}")
    print(f"   - Measures: {', '.join([m['name'] for m in schema['measures']])}")
    
    # Step 2: Create blueprint (hardcoded instead of LLM)
    print("\n🎨 Step 2: Creating blueprint...")
    blueprint = {
        "sheets": [
            {
                "name": "Sales by Region",
                "column_field": "region",
                "row_field": "sales",
                "mark_type": "Bar"
            },
            {
                "name": "Sales by Category",
                "column_field": "category",
                "row_field": "sales",
                "mark_type": "Bar"
            }
        ]
    }
    print(f"✅ Blueprint created with {len(blueprint['sheets'])} sheets")
    
    # Step 3: Generate workbook
    print("\n🔧 Step 3: Generating Tableau workbook...")
    template_path = "templates/base_template.twb"
    output_dir = "examples/generated_workbooks"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "demo_basic.twb")
    
    compiler = TableauXMLCompiler(template_path)
    result = compiler.compile_workbook(
        blueprint=blueprint,
        output_path=output_path,
        dataset_path=dataset_path
    )
    
    if result["success"]:
        print(f"✅ Workbook generated successfully!")
        print(f"   - Location: {result['workbook_path']}")
        print(f"   - Sheets created: {result['sheets_created']}")
        print(f"\n🎉 Success! Open the workbook in Tableau Desktop to view.")
    else:
        print(f"❌ Failed to generate workbook")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
