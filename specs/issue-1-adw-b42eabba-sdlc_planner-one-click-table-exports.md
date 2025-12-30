# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `b42eabba`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and once click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables. one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality to the Natural Language SQL Interface application. Users will be able to:
1. Export any uploaded table directly to a CSV file with a single click
2. Export query results to a CSV file after running a query

Two new API endpoints will be created to handle these exports:
- `GET /api/export/table/{table_name}` - Exports an entire table as CSV
- `POST /api/export/results` - Exports query results as CSV

The UI will be updated to add download buttons:
- A download button to the left of the 'x' (remove) icon for each table in the "Available Tables" section
- A download button to the left of the 'Hide' button in the query results section

## User Story
As a data analyst
I want to export tables and query results to CSV files with a single click
So that I can use the data in external tools like Excel, Google Sheets, or other data analysis software

## Problem Statement
Currently, users can query data and view results in the web interface, but they have no way to export this data for use in external applications. This limits the utility of the application since users often need to analyze data in other tools or share results with colleagues.

## Solution Statement
Implement two export endpoints on the server that generate CSV files from table data and query results. Add download buttons to the UI that trigger these exports. The CSV files will be streamed to the user's browser as file downloads with appropriate headers and filenames.

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Main FastAPI server file where new export endpoints will be added
- `app/server/core/data_models.py` - Pydantic models for request/response types (may need new model for export request)
- `app/server/core/sql_security.py` - Security utilities for safe SQL execution (will be used to safely export tables)
- `app/server/core/sql_processor.py` - SQL execution utilities (reference for database patterns)
- `app/client/src/main.ts` - Main frontend TypeScript file where download buttons and handlers will be added
- `app/client/src/api/client.ts` - API client where new export methods will be added
- `app/client/src/style.css` - Styles for the download buttons
- `app/client/index.html` - HTML structure (reference only, buttons added dynamically)
- `app/client/src/types.d.ts` - TypeScript type definitions (may need new types for export)
- `.claude/commands/test_e2e.md` - E2E test runner documentation (for understanding E2E test structure)
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test (for understanding E2E test format)

### New Files
- `.claude/commands/e2e/test_table_export.md` - New E2E test file to validate export functionality

## Implementation Plan
### Phase 1: Foundation
1. Add new Pydantic model for export results request
2. Create CSV generation utility function that handles proper escaping and formatting
3. Add server-side endpoints for table export and results export

### Phase 2: Core Implementation
1. Implement `GET /api/export/table/{table_name}` endpoint
   - Validate table name exists
   - Query all data from the table
   - Generate CSV with proper headers
   - Return as streaming response with Content-Disposition header
2. Implement `POST /api/export/results` endpoint
   - Accept query results (columns and data) in request body
   - Generate CSV from provided data
   - Return as streaming response

### Phase 3: Integration
1. Update API client with export methods
2. Add download buttons to the UI
3. Style the download buttons to match existing design
4. Wire up click handlers to trigger downloads
5. Create E2E test for export functionality

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test File
- Create `.claude/commands/e2e/test_table_export.md` to define the E2E test for export functionality
- Define test steps that:
  1. Navigate to the application
  2. Load sample data (users table)
  3. Verify download button appears next to table remove button
  4. Click download button for table
  5. Verify file download is triggered
  6. Run a query
  7. Verify download button appears in results section
  8. Click download button for results
  9. Verify file download is triggered
- Include success criteria and screenshot requirements

### Task 2: Add Export Request Model
- Open `app/server/core/data_models.py`
- Add `ExportResultsRequest` model with:
  - `columns: List[str]` - Column names
  - `results: List[Dict[str, Any]]` - Row data

### Task 3: Implement Table Export Endpoint
- Open `app/server/server.py`
- Import `StreamingResponse` from `fastapi.responses`
- Import `io` and `csv` modules
- Create helper function `generate_csv_content(columns: List[str], rows: List[Dict[str, Any]]) -> str`
  - Use `csv.writer` with `io.StringIO` for proper CSV formatting
  - Handle special characters and escaping
- Add `GET /api/export/table/{table_name}` endpoint:
  - Validate table name using `validate_identifier`
  - Check table exists using `check_table_exists`
  - Query all data: `SELECT * FROM {table}`
  - Generate CSV content
  - Return `StreamingResponse` with:
    - `media_type="text/csv"`
    - `headers={"Content-Disposition": f"attachment; filename={table_name}.csv"}`

### Task 4: Implement Results Export Endpoint
- Open `app/server/server.py`
- Add `POST /api/export/results` endpoint:
  - Accept `ExportResultsRequest` body
  - Generate CSV from columns and results
  - Return `StreamingResponse` with:
    - `media_type="text/csv"`
    - `headers={"Content-Disposition": "attachment; filename=query_results.csv"}`

### Task 5: Add API Client Export Methods
- Open `app/client/src/api/client.ts`
- Add `exportTable(tableName: string)` method:
  - Make GET request to `/export/table/{tableName}`
  - Trigger browser download using blob and anchor technique
- Add `exportResults(columns: string[], results: Record<string, any>[])` method:
  - Make POST request to `/export/results`
  - Trigger browser download

### Task 6: Add Download Button Styles
- Open `app/client/src/style.css`
- Add `.download-table-button` class:
  - Similar styling to `.remove-table-button`
  - Use appropriate icon styling
  - Hover effect with primary color instead of error color
- Add `.download-results-button` class:
  - Position to left of Hide button
  - Match toggle button styling

### Task 7: Add Table Download Button to UI
- Open `app/client/src/main.ts`
- In `displayTables` function, before creating `removeButton`:
  - Create download button element
  - Set class to `download-table-button`
  - Set innerHTML to download icon (use SVG or Unicode ⬇ or similar)
  - Set title to "Download as CSV"
  - Add click handler that calls `downloadTable(table.name)`
  - Insert button to the left of removeButton in `tableHeader`

### Task 8: Add Results Download Button to UI
- Open `app/client/src/main.ts`
- In `displayResults` function, modify results header:
  - Create download button for results
  - Set class to `download-results-button`
  - Set innerHTML to download icon
  - Set title to "Download results as CSV"
  - Add click handler that calls `downloadResults(response.columns, response.results)`
  - Insert button to the left of toggle button

### Task 9: Implement Download Helper Functions
- Open `app/client/src/main.ts`
- Add `downloadTable(tableName: string)` async function:
  - Call API endpoint
  - Handle the blob response
  - Create temporary anchor element
  - Trigger download
- Add `downloadResults(columns: string[], results: Record<string, any>[])` async function:
  - Call API endpoint with data
  - Handle the blob response
  - Create temporary anchor element
  - Trigger download

### Task 10: Run Validation Commands
- Run server tests: `cd app/server && uv run pytest`
- Run TypeScript type check: `cd app/client && bun tsc --noEmit`
- Run frontend build: `cd app/client && bun run build`
- Execute E2E test: Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_export.md`

## Testing Strategy
### Unit Tests
- Test `generate_csv_content` helper with various data types (strings with commas, quotes, newlines)
- Test table export endpoint returns correct CSV format
- Test results export endpoint returns correct CSV format
- Test table export with non-existent table returns 404
- Test table export with invalid table name returns 400

### Edge Cases
- Table with no rows (should return CSV with only headers)
- Table with special characters in data (commas, quotes, newlines)
- Very large table export (streaming should handle this)
- Results with null values
- Unicode characters in data

## Acceptance Criteria
- [ ] Download button appears to the left of the 'x' icon for each table in Available Tables
- [ ] Download button appears to the left of the 'Hide' button for query results
- [ ] Clicking table download button downloads a CSV file named `{table_name}.csv`
- [ ] Clicking results download button downloads a CSV file named `query_results.csv`
- [ ] CSV files are properly formatted with correct headers and escaped values
- [ ] Download buttons have appropriate styling and hover effects
- [ ] Download buttons use a recognizable download icon
- [ ] All existing tests continue to pass
- [ ] TypeScript compiles without errors
- [ ] Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_export.md` to validate export functionality works end-to-end

## Notes
- The download icon should be a recognizable symbol (down arrow, or similar). Consider using Unicode character like ⬇️ or 📥, or an SVG icon for consistency
- For large tables, the streaming response approach ensures memory efficiency
- CSV format was chosen over other formats (JSON, Excel) for maximum compatibility
- The client-side download uses the blob + anchor technique which works across all modern browsers
- Future enhancement: Add format selection (CSV, JSON, Excel) in a dropdown
