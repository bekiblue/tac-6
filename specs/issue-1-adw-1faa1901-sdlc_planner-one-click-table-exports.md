# Feature: One Click Table Exports

## Metadata
issue_number: `1`
adw_id: `1faa1901`
issue_json: `{"number":1,"title":"One Click Table Exports","body":"Using adw_plan_build_review add one click table exports and once click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables. one for exporting query results.\n\nPlace a download button directly to the left of the 'x' icon for available tables.\nPlace a download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon."}`

## Feature Description
This feature adds one-click CSV export functionality to the Natural Language SQL Interface application. Users can download any uploaded table as a CSV file with a single click, and also export query results to CSV format. This makes it easy to extract data from the application for further analysis in spreadsheets or other tools.

The feature consists of:
1. A download button placed to the left of the 'x' (remove) icon for each table in the Available Tables section
2. A download button placed to the left of the 'Hide' button in the query results section
3. Two new API endpoints to handle the CSV export logic on the server side

## User Story
As a data analyst
I want to export tables and query results as CSV files with one click
So that I can easily download and share data for further analysis in spreadsheets or other tools

## Problem Statement
Users currently have no way to export their data from the application. After uploading data and running queries, they cannot easily get the results out of the system for use in other applications like Excel, Google Sheets, or data analysis tools.

## Solution Statement
Implement two export mechanisms:
1. **Table Export**: Add a download button next to each table that triggers a GET request to `/api/export/table/{table_name}`, which returns the full table contents as a CSV file download
2. **Results Export**: Add a download button in the results header that sends a POST request to `/api/export/results` with the current query results, returning them as a CSV file download

Both endpoints will return properly formatted CSV files with appropriate HTTP headers (`Content-Type: text/csv` and `Content-Disposition: attachment`) to trigger browser downloads.

## Relevant Files
Use these files to implement the feature:

- `README.md` - Project overview and API documentation to understand the existing API patterns
- `app/server/server.py` - Main FastAPI server where new endpoints will be added (contains existing endpoint patterns)
- `app/server/core/data_models.py` - Pydantic models where the `ExportResultsRequest` model will be added
- `app/server/core/sql_security.py` - Security module for safe table access (validate_identifier, execute_query_safely, check_table_exists)
- `app/client/index.html` - HTML structure where download buttons need to be integrated
- `app/client/src/main.ts` - Client-side logic where download functionality will be implemented
- `app/client/src/style.css` - CSS styles for the download buttons
- `app/client/src/api/client.ts` - API client (may need updates for export endpoints, though fetch can be used directly)
- `app/client/src/types.d.ts` - TypeScript type definitions (may need update if using API client)
- `.claude/commands/test_e2e.md` - Instructions for running E2E tests
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file to understand the format

### New Files
- `app/server/tests/test_export.py` - Unit tests for the export endpoints
- `.claude/commands/e2e/test_table_export.md` - E2E test file for the export functionality

## Implementation Plan
### Phase 1: Foundation
1. Add the `ExportResultsRequest` Pydantic model to `app/server/core/data_models.py`
2. Create the E2E test file to define expected behavior before implementation

### Phase 2: Core Implementation
1. Implement the `GET /api/export/table/{table_name}` endpoint in `server.py`
   - Validate table name using existing security module
   - Check table exists
   - Query all data from the table
   - Convert to CSV format using Python's csv module
   - Return as StreamingResponse with proper headers
2. Implement the `POST /api/export/results` endpoint in `server.py`
   - Accept columns and results arrays
   - Convert to CSV format
   - Return as StreamingResponse with proper headers
3. Write unit tests for both endpoints

### Phase 3: Integration
1. Add download button styling to `style.css`
2. Update `displayTables()` function in `main.ts` to add download button next to remove button
3. Update `displayResults()` function in `main.ts` to add download button next to hide button
4. Implement `downloadTable()` and `downloadResults()` functions in `main.ts`
5. Run E2E tests to verify the feature works end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test File
- Create `.claude/commands/e2e/test_table_export.md` based on the format in `test_basic_query.md`
- Define test steps that verify:
  - Download button appears next to table 'x' icon
  - Download button appears next to results 'Hide' button
  - Clicking table download triggers CSV download
  - Clicking results download triggers CSV download
  - Use the down arrow symbol (&#x2B73;) as the download icon

### Task 2: Add Export Data Model
- Add `ExportResultsRequest` model to `app/server/core/data_models.py`:
  ```python
  class ExportResultsRequest(BaseModel):
      columns: List[str]
      results: List[Dict[str, Any]]
  ```

### Task 3: Implement Table Export Endpoint
- Add `GET /api/export/table/{table_name}` endpoint to `app/server/server.py`
- Import necessary modules: `csv`, `io`, `StreamingResponse` from fastapi.responses
- Validate table name using `validate_identifier()` from `sql_security`
- Check table exists using `check_table_exists()`
- Fetch all data using `execute_query_safely()` with `SELECT * FROM {table}`
- Convert to CSV using `csv.writer()`
- Return `StreamingResponse` with:
  - `media_type="text/csv"`
  - `Content-Disposition: attachment; filename="{table_name}.csv"`

### Task 4: Implement Results Export Endpoint
- Add `POST /api/export/results` endpoint to `app/server/server.py`
- Accept `ExportResultsRequest` body
- Convert columns and results to CSV format
- Return `StreamingResponse` with:
  - `media_type="text/csv"`
  - `Content-Disposition: attachment; filename="query_results.csv"`

### Task 5: Write Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py`
- Test cases for table export:
  - Valid table returns CSV with correct headers
  - Non-existent table returns 404
  - Invalid table name (SQL injection attempt) returns 400
  - Empty table returns CSV with headers only
- Test cases for results export:
  - Valid results return CSV
  - Empty results return headers only
  - Special characters in data are properly escaped
  - Null values are handled correctly

### Task 6: Add Download Button Styles
- Add styles to `app/client/src/style.css`:
  - `.download-table-button` - styled similar to `.remove-table-button` but with different hover color
  - `.download-results-button` - styled for the results section
  - `.table-actions` - container for download and remove buttons
  - `.results-actions` - container for download and toggle buttons

### Task 7: Update Table Display to Include Download Button
- Modify `displayTables()` function in `app/client/src/main.ts`
- Create actions container div for download and remove buttons
- Add download button with:
  - Class: `download-table-button`
  - innerHTML: `&#x2B73;` (down arrow symbol)
  - title: "Download table as CSV"
  - onclick: `downloadTable(table.name)`
- Place download button before remove button

### Task 8: Implement downloadTable Function
- Add `downloadTable(tableName: string)` function to `main.ts`
- Show loading state on button
- Fetch `/api/export/table/${tableName}`
- On success: create blob and trigger download
- On error: display error message
- Reset button state in finally block

### Task 9: Update Results Display to Include Download Button
- Modify `displayResults()` function in `main.ts`
- Store current results in global state for export: `currentResults = { columns, results }`
- Create actions container in results header
- Add download button before toggle button
- Button specs:
  - Class: `download-results-button`
  - innerHTML: `&#x2B73;`
  - title: "Download results as CSV"
  - onclick: `downloadResults()`

### Task 10: Implement downloadResults Function
- Add `downloadResults()` function to `main.ts`
- Add global state: `let currentResults: { columns: string[]; results: Record<string, any>[] } | null = null;`
- Show loading state on button
- POST to `/api/export/results` with current columns and results
- On success: create blob and trigger download
- On error: display error message
- Reset button state in finally block

### Task 11: Add triggerDownload Helper Function
- Add helper function to handle browser download:
  ```typescript
  function triggerDownload(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  ```

### Task 12: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint with valid tables
- Test table export with non-existent tables (404)
- Test table export with invalid/malicious table names (400)
- Test table export with empty tables (headers only)
- Test results export with valid data
- Test results export with empty results
- Test results export with special characters (commas, quotes, newlines)
- Test results export with null/missing values
- Test CSV format compliance (proper escaping, column order)
- Test HTTP response headers (Content-Type, Content-Disposition)

### Edge Cases
- Table names with special characters (should be rejected by validator)
- SQL injection attempts in table names
- Very large tables (performance)
- Unicode characters in data
- Results with mismatched columns and data
- Empty column names
- Concurrent export requests

## Acceptance Criteria
- [ ] Download button (down arrow icon ⬇) appears directly to the left of the 'x' icon for each table in Available Tables
- [ ] Download button (down arrow icon ⬇) appears directly to the left of the 'Hide' button in query results section
- [ ] Clicking table download button triggers immediate CSV file download named `{table_name}.csv`
- [ ] Clicking results download button triggers immediate CSV file download named `query_results.csv`
- [ ] Downloaded CSV files are properly formatted with headers and data
- [ ] Special characters in data are properly escaped in CSV output
- [ ] Download buttons show loading state while export is in progress
- [ ] Error messages are displayed if export fails
- [ ] All existing functionality (query, upload, remove, hide) continues to work
- [ ] All server tests pass
- [ ] TypeScript compilation succeeds without errors
- [ ] Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_export.md` to validate the export functionality works end-to-end
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run TypeScript type checking to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- The down arrow symbol used for the download icon is `&#x2B73;` (⬇) which is a Unicode character that works across platforms
- The CSV export uses Python's built-in `csv` module which handles proper escaping of special characters automatically
- The `StreamingResponse` from FastAPI is used for efficient memory usage when exporting large tables
- The table export endpoint reuses existing security infrastructure (`validate_identifier`, `check_table_exists`, `execute_query_safely`) to ensure SQL injection protection
- The results export endpoint receives pre-validated data from the client (the results from a previous query), so no additional SQL security is needed
- Consider adding pagination or row limits for very large table exports in future iterations
- The global `currentResults` state in the client stores the most recent query results for export; this is cleared when results show an error
