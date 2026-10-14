# Flask Sales Dashboard

A read-only Python web application that connects to Azure SQL Database (or SQL Server with a trusted TLS certificate), reads your Sales table, and displays its actual columns and rows in a searchable HTML dashboard. No fixed Sales schema is assumed.

## Windows setup

1. Install Python 3.10 or newer and Microsoft ODBC Driver 18 for SQL Server:
   https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Extract the ZIP. Open a terminal in the `flask_sales_dashboard` folder.
3. Install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Edit `.env` in your editor. Use your actual Azure server, database, SQL username and password. Set `SQL_SCHEMA=dbo` and `SQL_TABLE=Sales` to match your database. Do not include `https://` in SQL_SERVER. Keep port 1433 for Azure SQL Database. SQL authentication must be enabled for this example.
5. Add your current public IP to the Azure SQL server's firewall (Networking page) when connecting through its public endpoint. The login needs SELECT permission on the table.
6. Run:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

7. Open http://127.0.0.1:5000 in your browser. Keep the terminal running. Press Ctrl+C to stop.

On Linux/macOS, create the venv with `python3 -m venv .venv`, install with `.venv/bin/python -m pip install -r requirements.txt`, copy the example using `cp .env.example .env`, and run `.venv/bin/python app.py`. Install the Microsoft ODBC driver for your operating system separately.

## How it works

1. The browser sends GET `/` to Flask on port 5000.
2. `dashboard()` calls `fetch_sales()`.
3. SQLAlchemy + pyodbc connects to your database on port 1433 with encryption and certificate validation.
4. A SELECT query retrieves up to the selected limit (maximum 1,000 rows).
5. `render_template()` passes the result to `templates/dashboard.html`.
6. Jinja creates the HTML table. CSS styles it, and JavaScript filters loaded rows.

`GET /?limit=250` loads up to 250 records. The Refresh button queries SQL Server again. Search works across the rows already loaded, not the full database. Set `SQL_ORDER_COLUMN` to your unique sale ID column for predictable ordering; without it, SQL Server may return any subset on refresh. Only simple schema/table/column identifiers with letters, numbers and underscores are supported.

The cards show fetched rows, columns, and connection status. These are not sales revenue metrics or a total row count. No fake sales data is included. An empty table and a failed connection have different UI states.

## Database access and errors

Credentials stay in the server-side `.env` file; the browser receives HTML only. The app performs SELECT queries and does not load, change, or delete data. `.env` is excluded by `.gitignore`.

If data does not load, check the exact server/database/table names, ODBC driver installation, SQL authentication, login permissions, network connection, and Azure IP firewall rule. If SQL_ORDER_COLUMN is set, confirm that column exists. A connection error returns HTTP 503 with a readable message rather than exposing connection strings.

This project runs locally without authentication. If you later host it for other users, add authentication and deploy through a production WSGI server. Flask's development server is for local testing.

## Validation performed

Application syntax and Flask routes, rendered rows, escaping, empty table, missing configuration, connection failure, and row-limit handling are checked using simulated query results. Your live Azure SQL connection must be verified on your computer with your credentials. No live database access was performed during creation.

## References

- Flask templates: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
- SQLAlchemy SQL Server connections: https://docs.sqlalchemy.org/en/20/dialects/mssql.html
