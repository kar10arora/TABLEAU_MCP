"""
Tableau XML workbook generator.
Safely manipulates .twb files using template injection.
"""

from lxml import etree
from typing import Dict, List, Optional
import os
from src.core.uuid_utils import generate_tableau_uuid


class TableauXMLCompiler:
    """Compiles Tableau workbooks from JSON blueprints."""
    
    def __init__(self, template_path: str):
        """
        Initialize compiler with template.
        
        Args:
            template_path: Path to base .twb template file
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        self.template_path = template_path
        self.parser = etree.XMLParser(remove_blank_text=False, recover=True)
    
    def compile_workbook(self, 
                        blueprint: Dict, 
                        output_path: str,
                        dataset_path: str = None) -> Dict:
        """
        Generate complete .twb workbook from blueprint.
        
        Args:
            blueprint: JSON blueprint with sheets configuration
            output_path: Where to save generated .twb file
            dataset_path: Path to dataset (for datasource update)
            
        Returns:
            dict: {"success": bool, "workbook_path": str, "sheets_created": int}
        """
        # Load template
        tree = etree.parse(self.template_path, self.parser)
        root = tree.getroot()
        
        # Extract datasource ID
        datasource_elem = root.find(".//datasources/datasource")
        if datasource_elem is None:
            raise ValueError("Template missing datasource element")
        
        ds_id = datasource_elem.get("name")
        
        # Update dataset path if provided
        if dataset_path:
            self._update_datasource_path(root, dataset_path)
        
        # Get parent containers
        worksheets_parent = root.find(".//worksheets")
        windows_parent = root.find(".//windows")
        
        if worksheets_parent is None or windows_parent is None:
            raise ValueError("Template missing worksheets or windows container")
        
        # Clear existing sheets
        worksheets_parent.clear()
        windows_parent.clear()
        windows_parent.set("source-height", "30")
        
        # Generate sheets from blueprint
        sheets_created = 0
        for index, sheet in enumerate(blueprint.get("sheets", [])):
            try:
                # Generate UUIDs
                sheet_uuid = generate_tableau_uuid()
                window_uuid = generate_tableau_uuid()
                
                # Build worksheet XML
                worksheet_xml = self._build_worksheet(
                    name=sheet["name"],
                    ds_id=ds_id,
                    cols=sheet.get("column_field", ""),
                    rows=sheet.get("row_field", ""),
                    mark_type=sheet.get("mark_type", "Automatic"),
                    uuid=sheet_uuid
                )
                
                # Build window XML
                window_xml = self._build_window(
                    name=sheet["name"],
                    uuid=window_uuid,
                    maximized=(index == 0)  # Maximize first sheet
                )
                
                # Inject into tree
                worksheets_parent.append(etree.fromstring(worksheet_xml, self.parser))
                windows_parent.append(etree.fromstring(window_xml, self.parser))
                
                sheets_created += 1
                
            except Exception as e:
                print(f"Warning: Failed to create sheet '{sheet.get('name')}': {str(e)}")
                continue
        
        # Write final workbook
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return {
            "success": True,
            "workbook_path": output_path,
            "sheets_created": sheets_created
        }
    
    def _build_worksheet(self, name: str, ds_id: str, cols: str, rows: str, 
                        mark_type: str, uuid: str) -> str:
        """Build worksheet XML block safely."""
        
        # Construct field references
        cols_ref = f"[{ds_id}].[{cols}]" if cols else ""
        rows_ref = f"[{ds_id}].[{rows}]" if rows else ""
        
        worksheet_xml = f"""
        <worksheet name='{name}'>
          <table>
            <view>
              <datasources>
                <datasource name='{ds_id}' />
              </datasources>
              <datasource-dependencies datasource='{ds_id}'>
                <column datatype='string' name='[{cols}]' role='dimension' type='nominal' />
                <column datatype='real' name='[{rows}]' role='measure' type='quantitative' />
              </datasource-dependencies>
              <aggregation value='true' />
            </view>
            <style />
            <panes>
              <pane selection-relaxation-option='selection-relaxation-allow'>
                <view>
                  <breakdown value='auto' />
                </view>
                <mark class='{mark_type}' />
              </pane>
            </panes>
            <rows>{rows_ref}</rows>
            <cols>{cols_ref}</cols>
          </table>
          <simple-id uuid='{uuid}' />
        </worksheet>
        """
        return worksheet_xml
    
    def _build_window(self, name: str, uuid: str, maximized: bool = False) -> str:
        """Build window XML block safely."""
        
        maximized_attr = "maximized='true'" if maximized else ""
        
        window_xml = f"""
        <window class='worksheet' {maximized_attr} name='{name}'>
          <cards>
            <edge name='left'>
              <strip size='160'>
                <card type='pages' />
                <card type='filters' />
                <card type='marks' />
              </strip>
            </edge>
            <edge name='top'>
              <strip size='2147483647'>
                <card type='columns' />
              </strip>
              <strip size='2147483647'>
                <card type='rows' />
              </strip>
              <strip size='31'>
                <card type='title' />
              </strip>
            </edge>
          </cards>
          <simple-id uuid='{uuid}' />
        </window>
        """
        return window_xml
    
    def _update_datasource_path(self, root, dataset_path: str):
        """Update datasource connection to point to new dataset."""
        connection_elem = root.find(".//connection[@class='textscan']")
        if connection_elem is not None:
            connection_elem.set("directory", os.path.dirname(os.path.abspath(dataset_path)))
            connection_elem.set("filename", os.path.basename(dataset_path))
