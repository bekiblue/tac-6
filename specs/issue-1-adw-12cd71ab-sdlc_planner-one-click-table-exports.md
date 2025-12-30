# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `12cd71ab`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and once click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables. one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality to the Natural Language SQL Interface application. Users will be able to export both database tables and query results as CSV files directly from the UI. Two new API endpoints will be created to support these exports, and download buttons will be added to the UI in strategic locations for easy access.

## User Story
As a data analyst
I want to export tables and query results as CSV files with one click
So that I can easily download and share data for further analysis in spreadsheets or other tools

## Problem Statement
Currently, users can query their data and view results in the application, but there is no way to export this data for use outside the application. Users who want to share results or perform additional analysis in tools like Excel must manually copy data, which is error-prone and time-consuming.

## Solution Statement
Add two new API endpoints (`/api/export/table/{table_name}` and `/api/export/results`) that return data as downloadable CSV files. Add download buttons in the UI:
1. A download button to the left of the 'x' (remove) button for each table in the "Available Tables" section
2. A download button to the left of the 'Hide' button in the query results section

Both buttons will use an appropriate download icon and trigger browser downloads of the corresponding CSV data.

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `app/server/server.py` - Main FastAPI server where new export endpoints will be added (lines 270-306 show existing delete endpoint pattern)
- `app/server/core/data_models.py` - Pydantic models for request/response types
- `app/server/core/sql_processor.py` - SQL execution utilities for fetching table data
- `app/server/core/sql_security.py` - SQL security module for safe query execution

### Frontend Files
- `app/client/src/main.ts` - Main frontend application with UI logic (lines 253-323 show table display, lines 184-219 show results display)
- `app/client/src/api/client.ts` - API client for making backend requests
- `app/client/src/types.d.ts` - TypeScript type definitions
- `app/client/src/style.css` - CSS styles including button styles (lines 316-335 show existing remove button styles)
- `app/client/index.html` - HTML template showing UI structure (lines 32-39 show results section, lines 42-47 show tables section)

### Test Files
- `app/server/tests/` - Backend test files (follow existing patterns)

### Documentation Files
- `.claude/commands/test_e2e.md` - E2E test runner documentation
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file format

### New Files
- `app/server/tests/test_export.py` - Unit tests for export endpoints
- `.claude/commands/e2e/test_table_export.md` - E2E test file for export functionality

## Implementation Plan
### Phase 1: Foundation
1. Create Pydantic response model for export endpoints in `data_models.py`
2. Add unit test file structure for export functionality

### Phase 2: Core Implementation
1. Create `/api/export/table/{table_name}` endpoint that:
   - Validates the table name using existing security module
   - Fetches all data from the specified table
   - Returns data as a downloadable CSV file with proper headers
2. Create `/api/export/results` endpoint that:
   - Accepts query results data (columns and results from previous query)
   - Converts the data to CSV format
   - Returns as a downloadable CSV file
3. Add CSS styles for the download buttons
4. Add download button to table items in the UI (left of 'x' button)
5. Add download button to results section (left of 'Hide' button)
6. Implement client-side download handlers

### Phase 3: Integration
1. Wire up frontend buttons to trigger API calls
2. Handle browser download of CSV files
3. Add loading states and error handling
4. Write comprehensive unit tests
5. Create and execute E2E tests

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_table_export.md` with test steps for:
  - Uploading sample data
  - Verifying download button appears next to table 'x' button
  - Clicking download button and verifying CSV download
  - Running a query and verifying download button in results
  - Clicking results download button and verifying CSV download
  - Taking screenshots at each major step

### Step 2: Add Backend Export Endpoints
- Add `TableExportResponse` model to `app/server/core/data_models.py` (not strictly required as we return StreamingResponse, but good for documentation)
- Add `/api/export/table/{table_name}` endpoint to `app/server/server.py`:
  - Use `validate_identifier` from `sql_security` to validate table name
  - Use `check_table_exists` to verify table exists
  - Execute `SELECT * FROM {table}` using `execute_query_safely`
  - Convert results to CSV format using Python's `csv` module
  - Return as `StreamingResponse` with `Content-Disposition: attachment` header
- Add `/api/export/results` POST endpoint to `app/server/server.py`:
  - Accept JSON body with `columns: List[str]` and `results: List[Dict[str, Any]]`
  - Convert to CSV format
  - Return as `StreamingResponse` with `Content-Disposition: attachment` header

### Step 3: Add Backend Unit Tests
- Create `app/server/tests/test_export.py` with tests for:
  - Exporting a valid table returns CSV with correct headers
  - Exporting non-existent table returns 404
  - Exporting table with invalid name returns 400
  - Exporting results with valid data returns CSV
  - Exporting results with empty data returns CSV with only headers
  - CSV content is properly formatted (quotes, escaping)

### Step 4: Add Download Button Styles
- Add CSS styles to `app/client/src/style.css` for `.download-table-button` and `.download-results-button`:
  - Style similar to existing `.remove-table-button` (lines 316-335)
  - Use appropriate hover states
  - Position button inline with existing buttons

### Step 5: Add Download Button to Table Items
- Modify `displayTables` function in `app/client/src/main.ts` (lines 253-323):
  - Create download button element with download icon (use HTML entity `&#x2B73;` or SVG download icon)
  - Insert button to the left of `removeButton`
  - Add click handler that calls `downloadTable(table.name)`

### Step 6: Add Download Button to Results Section
- Modify `displayResults` function in `app/client/src/main.ts` (lines 184-219):
  - Store the current results data in module scope for export
  - Add download button to left of toggle button in results header
  - Add click handler that calls `downloadResults()`
- Update `app/client/index.html` if needed for the results header structure

### Step 7: Implement Download Handlers
- Add `downloadTable` function to `app/client/src/main.ts`:
  - Call `/api/export/table/{tableName}` endpoint
  - Trigger browser download using `blob` and `URL.createObjectURL`
  - Handle loading state on button
  - Handle errors gracefully
- Add `downloadResults` function to `app/client/src/main.ts`:
  - POST current results to `/api/export/results`
  - Trigger browser download
  - Handle loading and errors

### Step 8: Add API Client Methods (Optional Enhancement)
- Optionally add methods to `app/client/src/api/client.ts`:
  - `exportTable(tableName: string): Promise<Blob>`
  - `exportResults(columns: string[], results: Record<string, any>[]): Promise<Blob>`
- Note: Direct fetch with blob handling may be simpler for download functionality

### Step 9: Run Backend Tests
- Run `cd app/server && uv run pytest` to verify all tests pass
- Fix any failing tests

### Step 10: Run Frontend Build Validation
- Run `cd app/client && bun tsc --noEmit` to verify TypeScript compiles
- Run `cd app/client && bun run build` to verify production build works

### Step 11: Run E2E Tests
- Read `.claude/commands/test_e2e.md`
- Execute `.claude/commands/e2e/test_table_export.md` E2E test
- Verify all test steps pass and screenshots are captured

### Step 12: Final Validation
- Execute all `Validation Commands` below to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint with valid table name
- Test table export endpoint with non-existent table
- Test table export endpoint with SQL injection attempts
- Test results export endpoint with valid data
- Test results export endpoint with empty data
- Test CSV formatting (special characters, quotes, newlines in data)
- Test Content-Disposition header is set correctly
- Test Content-Type header is `text/csv`

### Edge Cases
- Table with no rows (should return CSV with headers only)
- Table with special characters in column names
- Results with null/undefined values
- Results with very large datasets
- Table names with special characters (should be blocked by security)
- Empty results array export
- Unicode characters in data

## Acceptance Criteria
- Download button appears to the left of 'x' button for each table in Available Tables section
- Download button appears to the left of 'Hide' button in Query Results section
- Clicking table download button downloads a CSV file named `{table_name}.csv`
- Clicking results download button downloads a CSV file named `query_results.csv`
- Downloaded CSV files are properly formatted with headers as first row
- Export endpoints return proper Content-Type (`text/csv`) and Content-Disposition headers
- Invalid table names return appropriate error responses
- UI shows loading state during download
- All existing tests continue to pass
- TypeScript compiles without errors
- Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run pytest tests/test_export.py -v` - Run export-specific tests
- `cd app/client && bun tsc --noEmit` - Run frontend type checking to validate TypeScript compiles
- `cd app/client && bun run build` - Run frontend build to validate production build works
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_export.md` E2E test file to validate export functionality works

## Notes
- The download functionality uses browser's native download mechanism via Blob URLs
- CSV format is chosen for maximum compatibility with spreadsheet applications
- The export endpoints use `StreamingResponse` from FastAPI for efficient memory usage with large datasets
- Security considerations: Table name validation uses existing `sql_security` module to prevent SQL injection
- The download icon can use the HTML entity `&#x2B73;` (downward arrow) or an SVG icon for better cross-browser support
- Consider future enhancement: Allow users to choose export format (CSV, JSON, Excel)
- The results export stores current query results in module scope to avoid re-querying the database
