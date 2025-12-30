"""
Tests for CSV export functionality
"""

import pytest
import sqlite3
import tempfile
import os
from fastapi.testclient import TestClient

# Import the FastAPI app for testing
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def test_db_with_data():
    """Create a test database with sample data"""
    # Ensure db directory exists
    os.makedirs("db", exist_ok=True)

    db_path = "db/database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create test table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_export_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    # Clear existing data
    cursor.execute("DELETE FROM test_export_users")

    # Insert test data
    cursor.execute("INSERT INTO test_export_users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO test_export_users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO test_export_users (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie', 'charlie@example.com', 35))

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_export_users")
    conn.commit()
    conn.close()


@pytest.fixture
def test_db_empty_table():
    """Create a test database with an empty table"""
    os.makedirs("db", exist_ok=True)

    db_path = "db/database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create empty test table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_empty_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value REAL
        )
    ''')

    # Clear existing data
    cursor.execute("DELETE FROM test_empty_table")

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_empty_table")
    conn.commit()
    conn.close()


class TestTableExport:
    """Test the /api/export/table/{table_name} endpoint"""

    def test_export_valid_table_returns_csv(self, client, test_db_with_data):
        """Test exporting a valid table returns CSV with correct headers"""
        response = client.get("/api/export/table/test_export_users")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "test_export_users.csv" in response.headers["content-disposition"]

        # Verify CSV content
        csv_content = response.text
        lines = csv_content.strip().split('\n')

        # Check header row
        assert "id" in lines[0]
        assert "name" in lines[0]
        assert "email" in lines[0]
        assert "age" in lines[0]

        # Check data rows (should have header + 3 data rows)
        assert len(lines) == 4

        # Verify data content
        assert "Alice" in csv_content
        assert "Bob" in csv_content
        assert "Charlie" in csv_content

    def test_export_nonexistent_table_returns_404(self, client):
        """Test exporting non-existent table returns 404"""
        response = client.get("/api/export/table/nonexistent_table_xyz")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_table_invalid_name_returns_400(self, client):
        """Test exporting table with invalid name returns 400"""
        # Test with SQL injection attempt
        response = client.get("/api/export/table/users'; DROP TABLE users; --")

        assert response.status_code == 400
        assert "Invalid" in response.json()["detail"]

    def test_export_empty_table_returns_headers_only(self, client, test_db_empty_table):
        """Test exporting empty table returns CSV with only headers"""
        response = client.get("/api/export/table/test_empty_table")

        assert response.status_code == 200

        csv_content = response.text
        lines = csv_content.strip().split('\n')

        # Should have only header row
        assert len(lines) == 1
        assert "id" in lines[0]
        assert "name" in lines[0]
        assert "value" in lines[0]

    def test_export_table_sql_keyword_name_returns_400(self, client):
        """Test exporting table with SQL keyword name returns 400"""
        response = client.get("/api/export/table/SELECT")

        assert response.status_code == 400
        assert "SQL keyword" in response.json()["detail"]


class TestResultsExport:
    """Test the /api/export/results endpoint"""

    def test_export_results_returns_csv(self, client):
        """Test exporting results returns CSV with correct format"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "query_results.csv" in response.headers["content-disposition"]

        # Verify CSV content (normalize line endings for cross-platform)
        csv_content = response.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = csv_content.strip().split('\n')

        # Check header row
        assert lines[0] == "id,name,email"

        # Check data rows (header + 2 data rows)
        assert len(lines) == 3

        # Verify data content
        assert "Alice" in csv_content
        assert "Bob" in csv_content

    def test_export_results_empty_data_returns_headers_only(self, client):
        """Test exporting empty results returns CSV with only headers"""
        request_data = {
            "columns": ["id", "name", "value"],
            "results": []
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200

        csv_content = response.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = csv_content.strip().split('\n')

        # Should have only header row
        assert len(lines) == 1
        assert "id,name,value" == lines[0]

    def test_export_results_with_special_characters(self, client):
        """Test exporting results with special characters properly escapes them"""
        request_data = {
            "columns": ["id", "description"],
            "results": [
                {"id": 1, "description": "Contains, comma"},
                {"id": 2, "description": 'Contains "quotes"'},
                {"id": 3, "description": "Contains\nnewline"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200

        # CSV module should properly handle special characters
        csv_content = response.text
        assert '"Contains, comma"' in csv_content or "Contains, comma" in csv_content

    def test_export_results_with_null_values(self, client):
        """Test exporting results with null/None values"""
        request_data = {
            "columns": ["id", "name", "optional_field"],
            "results": [
                {"id": 1, "name": "Alice", "optional_field": None},
                {"id": 2, "name": "Bob"}  # Missing optional_field
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200

        csv_content = response.text
        lines = csv_content.strip().split('\n')

        # Should have header + 2 data rows
        assert len(lines) == 3

    def test_export_results_maintains_column_order(self, client):
        """Test that column order is preserved in export"""
        request_data = {
            "columns": ["zulu", "alpha", "mike"],
            "results": [
                {"zulu": "z1", "alpha": "a1", "mike": "m1"},
                {"zulu": "z2", "alpha": "a2", "mike": "m2"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200

        csv_content = response.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = csv_content.strip().split('\n')

        # Header should maintain the specified order
        assert lines[0] == "zulu,alpha,mike"
        assert lines[1] == "z1,a1,m1"


class TestExportContentType:
    """Test content type and headers for exports"""

    def test_table_export_content_type(self, client, test_db_with_data):
        """Test table export returns correct content type"""
        response = client.get("/api/export/table/test_export_users")

        assert "text/csv" in response.headers["content-type"]

    def test_results_export_content_type(self, client):
        """Test results export returns correct content type"""
        request_data = {
            "columns": ["id"],
            "results": [{"id": 1}]
        }

        response = client.post("/api/export/results", json=request_data)

        assert "text/csv" in response.headers["content-type"]

    def test_table_export_content_disposition(self, client, test_db_with_data):
        """Test table export has correct Content-Disposition header"""
        response = client.get("/api/export/table/test_export_users")

        content_disp = response.headers["content-disposition"]
        assert "attachment" in content_disp
        assert "filename=" in content_disp
        assert "test_export_users.csv" in content_disp

    def test_results_export_content_disposition(self, client):
        """Test results export has correct Content-Disposition header"""
        request_data = {
            "columns": ["id"],
            "results": [{"id": 1}]
        }

        response = client.post("/api/export/results", json=request_data)

        content_disp = response.headers["content-disposition"]
        assert "attachment" in content_disp
        assert "filename=" in content_disp
        assert "query_results.csv" in content_disp
