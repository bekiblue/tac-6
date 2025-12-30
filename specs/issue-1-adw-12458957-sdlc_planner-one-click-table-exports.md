# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `12458957`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and once click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables. one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality to the Natural Language SQL Interface application. Users will be able to export entire database tables as CSV files and also export query results as CSV files. Two new API endpoints will be created on the server side to handle these export operations. The UI will be updated to add download buttons in strategic locations: next to the remove (x) button for tables and next to the Hide button for query results.

## User Story
As a data analyst using the Natural Language SQL Interface
I want to export tables and query results as CSV files with a single click
So that I can easily download and share data for further analysis in spreadsheet applications

## Problem Statement
Currently, users can query data and view results in the application, but there is no way to export or download this data. Users who need to share query results or work with the data in other applications (like Excel or Google Sheets) have no direct way to extract the data from the interface.

## Solution Statement
Implement two new backend API endpoints (`GET /api/export/table/{table_name}` and `POST /api/export/results`) that generate CSV files for download. Add download buttons to the UI: one next to each table's remove button in the Available Tables section, and one next to the Hide button in the Query Results section. The buttons will use appropriate download icons and trigger file downloads when clicked.

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Main FastAPI server file where new export endpoints will be added
- `app/server/core/data_models.py` - Pydantic models for request/response types; may need new models for export
- `app/server/core/sql_processor.py` - SQL execution functions used to retrieve data for export
- `app/server/core/sql_security.py` - Security utilities for safe table name validation
- `app/client/src/main.ts` - Main client application logic; needs download button handlers
- `app/client/src/api/client.ts` - API client for making requests to backend
- `app/client/src/types.d.ts` - TypeScript type definitions
- `app/client/src/style.css` - Styling for the new download buttons
- `app/client/index.html` - HTML structure (buttons will be added via JavaScript)
- `app/server/tests/` - Directory for server unit tests
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file for reference

### New Files
- `app/server/core/csv_exporter.py` - New module for CSV generation logic
- `app/server/tests/core/test_csv_exporter.py` - Unit tests for CSV exporter
- `.claude/commands/e2e/test_table_export.md` - E2E test for table and results export feature

## Implementation Plan
### Phase 1: Foundation
1. Create the CSV exporter module (`csv_exporter.py`) with functions to convert database table data and query results to CSV format
2. Add any necessary Pydantic models for export requests/responses
3. Write unit tests for the CSV exporter module

### Phase 2: Core Implementation
1. Implement `GET /api/export/table/{table_name}` endpoint to export entire tables as CSV
2. Implement `POST /api/export/results` endpoint to export query results as CSV
3. Add API client methods for calling the export endpoints
4. Add download button UI elements and handlers in the frontend

### Phase 3: Integration
1. Wire up the download buttons to trigger API calls and file downloads
2. Add appropriate loading states and error handling
3. Style the download buttons to match the existing UI
4. Create E2E test to validate the complete export workflow

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format
- Create `.claude/commands/e2e/test_table_export.md` with:
  - User story for exporting tables and query results
  - Test steps to upload sample data, verify download button appears, click to export table
  - Test steps to run a query, verify download button appears in results, click to export results
  - Success criteria for verifying CSV downloads work correctly

### Step 2: Create CSV Exporter Module
- Create `app/server/core/csv_exporter.py` with:
  - `export_table_to_csv(table_name: str) -> str` function that retrieves all rows from a table and returns CSV string
  - `export_results_to_csv(results: List[Dict], columns: List[str]) -> str` function that converts query results to CSV string
  - Use Python's built-in `csv` module with `io.StringIO` for in-memory CSV generation
  - Ensure proper escaping of special characters in CSV output

### Step 3: Add Data Models for Export
- Update `app/server/core/data_models.py` to add:
  - `ExportResultsRequest` model with `results: List[Dict[str, Any]]` and `columns: List[str]` fields
- The export endpoints will return StreamingResponse with CSV content, so no response model needed

### Step 4: Write Unit Tests for CSV Exporter
- Create `app/server/tests/core/test_csv_exporter.py` with tests for:
  - Exporting an empty table returns CSV with only headers
  - Exporting a table with data returns properly formatted CSV
  - Exporting results with special characters (commas, quotes, newlines) handles escaping correctly
  - Exporting results with null values handles them appropriately

### Step 5: Implement Table Export Endpoint
- Add to `app/server/server.py`:
  - `GET /api/export/table/{table_name}` endpoint
  - Validate table name using `validate_identifier` from sql_security
  - Check table exists using `check_table_exists`
  - Call `export_table_to_csv` to generate CSV
  - Return `StreamingResponse` with `media_type="text/csv"` and `Content-Disposition` header for download

### Step 6: Implement Results Export Endpoint
- Add to `app/server/server.py`:
  - `POST /api/export/results` endpoint accepting `ExportResultsRequest`
  - Call `export_results_to_csv` to generate CSV
  - Return `StreamingResponse` with `media_type="text/csv"` and `Content-Disposition` header for download

### Step 7: Add TypeScript Types
- Update `app/client/src/types.d.ts` to add:
  - `ExportResultsRequest` interface matching the backend model

### Step 8: Add API Client Methods
- Update `app/client/src/api/client.ts` to add:
  - `exportTable(tableName: string): Promise<Blob>` method that fetches CSV and returns as Blob
  - `exportResults(results: Record<string, any>[], columns: string[]): Promise<Blob>` method
  - Helper function `triggerDownload(blob: Blob, filename: string)` to create download link and trigger click

### Step 9: Add Download Button Styles
- Update `app/client/src/style.css` to add:
  - `.download-table-button` class styled similar to `.remove-table-button` but with appropriate color
  - Hover state styles for the download button
  - Position styles to place button to the left of the remove button

### Step 10: Add Table Download Button to UI
- Update `app/client/src/main.ts` in the `displayTables` function:
  - Create download button element with download icon (use Unicode character or SVG)
  - Add `download-table-button` class
  - Add click handler that calls `api.exportTable(table.name)` and triggers download
  - Insert button to the left of the remove button in the table header

### Step 11: Add Results Download Button to UI
- Update `app/client/src/main.ts` in the `displayResults` function:
  - Store query results in a variable accessible to the download handler
  - Create download button element with download icon
  - Add button to the left of the toggle (Hide) button in results header
  - Add click handler that calls `api.exportResults(results, columns)` and triggers download

### Step 12: Run Validation Commands
- Execute all validation commands to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test `export_table_to_csv` with various table schemas and data types
- Test `export_results_to_csv` with different result sets
- Test CSV escaping for special characters (commas, quotes, newlines, unicode)
- Test handling of null/undefined values in data
- Test export endpoint returns correct Content-Type and Content-Disposition headers

### Edge Cases
- Exporting an empty table (should return CSV with headers only)
- Exporting table with very large number of rows
- Exporting results with columns containing special CSV characters
- Exporting results with null values
- Exporting table that doesn't exist (should return 404)
- Exporting table with invalid name (should return 400)
- Attempting to export when no query results are available

## Acceptance Criteria
- Download button appears to the left of the 'x' icon for each table in Available Tables section
- Download button appears to the left of the 'Hide' button in Query Results section
- Clicking table download button downloads a CSV file named `{table_name}.csv`
- Clicking results download button downloads a CSV file named `query_results.csv`
- Downloaded CSV files open correctly in spreadsheet applications
- CSV files contain all data with proper formatting and escaping
- Download buttons use appropriate download icon
- All existing functionality continues to work (no regressions)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_export.md` to validate this functionality works

## Notes
- The download icon can use the Unicode download symbol (e.g., downward arrow) or an inline SVG for better cross-platform compatibility
- Consider using the standard download arrow icon that is commonly recognized
- The CSV export uses Python's built-in `csv` module which handles proper escaping automatically
- StreamingResponse is used for efficient memory usage with large datasets
- File names are sanitized to prevent issues with special characters
- Future enhancement could add support for other export formats (JSON, Excel) using the same pattern
