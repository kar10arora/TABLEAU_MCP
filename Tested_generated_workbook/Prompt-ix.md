
Generate a Tableau workbook using /Users/kartik.arora/Desktop/sales_data.csv with:

Sales by Product Category in ascending order (bar chart)
Sales by Sale Date in descending order
Discount by Region
Sales by Payment Method in ascending order
Quantity Sold by Sales Channel
Discount by Region And Sales Rep
20:35

Loaded tools, used tableau-mcp integration
Loaded tools, used tableau-mcp integration

Finding tools
Request

{
  "query": "generate tableau workbook"
}
Response

Loaded 4 tools:
  tableau-mcp (2):
  tableau-mcp:generate_tableau_workbook:
    dataset_path: string - Path to CSV dataset
    user_request: string - Natural language description of desired dashboard
    output_path?: string - Where to save .twb file (optional)
  tableau-mcp:inspect_dataset_schema:
    file_path: string - Path to CSV dataset file
  Google Drive (1):
  Google Drive:get_file_metadata:
    fileId: string - Required. The ID of the file to retrieve.
    excludeContentSnippets?: boolean - If true, the content snippet will be excluded from the response.
  Claude in Chrome (1):
  Claude in Chrome:gif_creator:
    action: string [start_recording|stop_recording|export|clear] - Action to perform: 'start_recording' (begin capturing), 'stop_recording' (stop capturing but keep frames), 'export' (...
    tabId: number - Tab ID to identify which tab group this operation applies to
    download?: boolean - Always set this to true for the 'export' action only. This causes the gif to be downloaded in the browser.
    filename?: string - Optional filename for exported GIF (default: 'recording-[timestamp].gif'). For 'export' action only.
    options?: object {showClickIndicators, showDragPaths, showActionLabels, showProgressBar, showWatermark, quality} - Optional GIF enhancement options for 'export' action. Properties: showClickIndicators (bool), showDragPaths (bool), s...
These tools are now available for you to call directly.

<functions>
<function>{"description": "Generate complete Tableau workbook from natural language request.", "name": "tableau-mcp:generate_tableau_workbook", "parameters": {"additionalProperties": false, "properties": {"dataset_path": {"description": "Path to CSV dataset", "type": "string"}, "output_path": {"default": null, "description": "Where to save .twb file (optional)", "type": "string"}, "user_request": {"description": "Natural language description of desired dashboard", "type": "string"}}, "required": ["dataset_path", "user_request"], "type": "object"}}</function>
<function>{"description": "Analyze dataset and return schema metadata.", "name": "tableau-mcp:inspect_dataset_schema", "parameters": {"additionalProperties": false, "properties": {"file_path": {"description": "Path to CSV dataset file", "type": "string"}}, "required": ["file_path"], "type": "object"}}</function>
<function>{"description": "Call this tool to find general metadata about a user's Drive file. If the file is not found, try using other tools like `search_files` to find the file the user is requesting.", "name": "Google Drive:get_file_metadata", "parameters": {"description": "Request to get the file.", "properties": {"excludeContentSnippets": {"description": "If true, the content snippet will be excluded from the response.", "type": "boolean"}, "fileId": {"description": "Required. The ID of the file to retrieve.", "type": "string"}}, "required": ["fileId"], "type": "object"}}</function>
<function>{"description": "Manage GIF recording and export for browser automation sessions. Control when to start/stop recording browser actions (clicks, scrolls, navigation), then export as an animated GIF with visual overlays (click indicators, action labels, progress bar, watermark). All operations are scoped to the tab's group. When starting recording, take a screenshot immediately after to capture the initial state as the first frame. When stopping recording, take a screenshot immediately before to capture the final state as the last frame. For export, either provide 'coordinate' to drag/drop upload to a page element, or set 'download: true' to download the GIF.", "name": "Claude in Chrome:gif_creator", "parameters": {"properties": {"action": {"description": "Action to perform: 'start_recording' (begin capturing), 'stop_recording' (stop capturing but keep frames), 'export' (generate and export GIF), 'clear' (discard frames)", "enum": ["start_recording", "stop_recording", "export", "clear"], "type": "string"}, "download": {"description": "Always set this to true for the 'export' action only. This causes the gif to be downloaded in the browser.", "type": "boolean"}, "filename": {"description": "Optional filename for exported GIF (default: 'recording-[timestamp].gif'). For 'export' action only.", "type": "string"}, "options": {"description": "Optional GIF enhancement options for 'export' action. Properties: showClickIndicators (bool), showDragPaths (bool), showActionLabels (bool), showProgressBar (bool), showWatermark (bool), quality (number 1-30). All default to true except quality (default: 10).", "properties": {"quality": {"description": "GIF compression quality, 1-30 (lower = better quality, slower encoding). Default: 10", "type": "number"}, "showActionLabels": {"description": "Show black labels describing actions (default: true)", "type": "boolean"}, "showClickIndicators": {"description": "Show orange circles at click locations (default: true)", "type": "boolean"}, "showDragPaths": {"description": "Show red arrows for drag actions (default: true)", "type": "boolean"}, "showProgressBar": {"description": "Show orange progress bar at bottom (default: true)", "type": "boolean"}, "showWatermark": {"description": "Show Claude logo watermark (default: true)", "type": "boolean"}}, "type": "object"}, "tabId": {"description": "Tab ID to identify which tab group this operation applies to", "type": "number"}}, "required": ["action", "tabId"], "type": "object"}}</function>
</functions>
T


Generate tableau workbook
Request

{
  "dataset_path": "/Users/kartik.arora/Desktop/sales_data.csv",
  "user_request": "Create a dashboard with the following 6 sheets:
1. Sales by Product Category - horizontal bar chart sorted in ascending order by Sales
2. Sales by Sale Date - line chart sorted in descending order by Sale Date
3. Discount by Region - bar chart showing total Discount per Region
4. Sales by Payment Method - bar chart sorted in ascending order by Sales
5. Quantity Sold by Sales Channel - bar chart showing Quantity Sold per Sales Channel
6. Discount by Region and Sales Rep - heatmap or stacked bar showing Discount broken down by both Region and Sales Rep"
}
Response

{
  "success": true,
  "workbook_path": "/Users/kartik.arora/.tableau-mcp/workbooks/generated_workbook.twb",
  "sheets_created": 6,
  "blueprint_used": {
    "sheets": [
      {
        "name": "Sales by Product Category",
        "column_field": "Product_Category",
        "row_field": "Sales_Amount",
        "mark_type": "Bar",
        "sort": {
          "field": "Sales_Amount",
          "direction": "ASC",
          "type": "field"
        }
      },
      {
        "name": "Sales by Sale Date",
        "column_field": "Sale_Date",
        "row_field": "Sales_Amount",
        "mark_type": "Line",
        "sort": {
          "field": "Sale_Date",
          "direction": "DESC",
          "type": "alphabetical"
        }
      },
      {
        "name": "Discount by Region",
        "column_field": "Region",
        "row_field": "Discount",
        "mark_type": "Bar"
      },
      {
        "name": "Sales by Payment Method",
        "column_field": "Payment_Method",
        "row_field": "Sales_Amount",
        "mark_type": "Bar",
        "sort": {
          "field": "Sales_Amount",
          "direction": "ASC",
          "type": "field"
        }
      },
      {
        "name": "Quantity Sold by Sales Channel",
        "column_field": "Sales_Channel",
        "row_field": "Quantity_Sold",
        "mark_type": "Bar"
      },
      {
        "name": "Discount by Region and Sales Rep",
        "column_field": "Region",
        "row_field": "Discount",
        "mark_type": "Bar",
        "encodings": {
          "color": {
            "field": "Sales_Rep",
            "type": "dimension"
          }
        }
      }
    ]
  }
}
Done
Your Tableau workbook has been successfully generated! Here's a summary of what was built:

Workbook saved to: /Users/kartik.arora/.tableau-mcp/workbooks/generated_workbook.twb

6 sheets created:

#	Sheet	Chart Type	Details
1	Sales by Product Category	Bar chart	Sorted ascending by Sales Amount
2	Sales by Sale Date	Line chart	Sorted descending by Sale Date
3	Discount by Region	Bar chart	Total Discount per Region
4	Sales by Payment Method	Bar chart	Sorted ascending by Sales Amount
5	Quantity Sold by Sales Channel	Bar chart	Quantity per Sales Channel
6	Discount by Region & Sales Rep	Stacked bar chart	Discount by Region, color-coded by Sales Rep
To open the workbook, launch Tableau Desktop and open the .twb file from the path above. Since it's a .twb (not .twbx), make sure Tableau can still access the original CSV at /Users/kartik.arora/Desktop/sales_data.csv.







Claude is AI and can make mistakes. Please double-check responses.
