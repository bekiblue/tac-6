# E2E Test: Table Export Functionality

Test the one-click table export and query results export functionality in the Natural Language SQL Interface application.

## User Story

As a data analyst
I want to export tables and query results as CSV files with one click
So that I can easily download and share data for further analysis in spreadsheets or other tools

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Upload Data button
   - Available Tables section

5. Click the "Upload Data" button to open the upload modal
6. Take a screenshot of the upload modal
7. Click on "Users Data" sample data button to load sample data
8. Wait for the table to appear in "Available Tables" section
9. Take a screenshot after data is loaded

10. **Verify** the users table appears in the Available Tables section
11. **Verify** a download button (⬇) appears to the left of the 'x' button for the users table
12. Take a screenshot showing the download button next to the table

13. Click the download button for the users table
14. **Verify** the browser initiates a download (a CSV file download should be triggered)
15. Take a screenshot after clicking the download button

16. Enter the query: "Show all users"
17. Click the Query button
18. Wait for query results to appear
19. Take a screenshot of the query results

20. **Verify** the query results section is visible
21. **Verify** a download button appears to the left of the 'Hide' button in the results header
22. Take a screenshot showing the download button in the results section

23. Click the download button in the results section
24. **Verify** the browser initiates a download for query results
25. Take a screenshot after clicking the results download button

26. Click "Hide" button to verify it still works
27. **Verify** results are hidden
28. Take a final screenshot

## Success Criteria
- Download button appears next to the 'x' button for each table
- Download button appears next to the 'Hide' button in results section
- Clicking table download button triggers CSV file download
- Clicking results download button triggers CSV file download
- Downloaded files should be in CSV format
- Hide button continues to work correctly
- All screenshots are captured successfully
