# Tableau Templates Directory

## Overview
This directory contains the base Tableau workbook template used for generation.

## Required Template
You need to create `base_blank.twb` manually in Tableau Desktop:

### Steps to Create Template:
1. Open Tableau Desktop
2. Connect to any simple CSV dataset (e.g., Sample - Superstore)
3. Create a blank worksheet (don't add any fields)
4. **Save As**: File → Save As
   - **IMPORTANT**: Save as `.twb` format (NOT `.twbx`)
   - Save location: `templates/base_blank.twb`

This template will be used as the foundation for all generated workbooks.

## Template Structure
The base template should contain:
- Basic workbook structure
- Datasource connection placeholder
- Minimal XML that can be safely modified

## Notes
- Do NOT commit actual workbook files to git (see .gitignore)
- Template must be `.twb` format (XML-based), not `.twbx` (packaged)
- Keep template minimal to reduce file size
