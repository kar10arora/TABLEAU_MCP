
Generate a Tableau workbook using /Users/kartik.arora/Desktop/sales_data.csv with:

Sales by Product Category in ascending order (bar chart)
Sales Average by Payment Method & Region(bar chart)
20:24

Loaded tools, used tableau-mcp integration
Loaded tools, used tableau-mcp integration

Finding tools
Request

{
  "query": "tableau workbook generate"
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
  "user_request": "Create a dashboard with two bar charts:
1. Sales by Product Category sorted in ascending order of Sales (horizontal or vertical bar chart)
2. Average Sales by Payment Method and Region (grouped bar chart)
"
}
Response

{
  "success": true,
  "workbook_path": "/Users/kartik.arora/.tableau-mcp/workbooks/generated_workbook.twb",
  "sheets_created": 2,
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
        "name": "Average Sales by Payment Method and Region",
        "column_field": [
          "Payment_Method",
          "Region"
        ],
        "row_field": "Sales_Amount",
        "mark_type": "Bar"
      }
    ]
  }
}
Done
Your Tableau workbook has been generated successfully! Here's a summary of what was created:

📊 Workbook saved to: /Users/kartik.arora/.tableau-mcp/workbooks/generated_workbook.twb

Sheets created (2):

Sales by Product Category — Bar chart showing total Sales Amount per Product Category, sorted in ascending order.
Average Sales by Payment Method & Region — Grouped bar chart showing the average Sales Amount broken down by both Payment Method and Region.
To open it, just double-click the .twb file and it will launch in Tableau Desktop. Make sure Tableau can find your CSV at /Users/kartik.arora/Desktop/sales_data.csv — since .twb files reference the data source by path, keeping the CSV in place ensures it loads cleanly.






Claude is AI and can make mistakes. Please double-check responses.
