import os
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(Path(__file__).with_name('.env'))
app = Flask(__name__)


@lru_cache(maxsize=1)
def database_engine():
    url = URL.create(
        'mssql+pyodbc',
        username=os.environ['SQL_USERNAME'],
        password=os.environ['SQL_PASSWORD'],
        host=os.environ['SQL_SERVER'],
        port=int(os.getenv('SQL_PORT', '1433')),
        database=os.environ['SQL_DATABASE'],
        query={
            'driver': os.getenv('SQL_DRIVER', 'ODBC Driver 18 for SQL Server'),
            'Encrypt': 'yes',
            'TrustServerCertificate': 'no',
            'Connection Timeout': '10',
        },
    )
    return create_engine(url, pool_pre_ping=True, hide_parameters=True)


def fetch_sales():
    schema = os.getenv('SQL_SCHEMA', 'dbo') 
    table = os.getenv('SQL_TABLE', 'Sales')
    order_column = os.getenv('SQL_ORDER_COLUMN', '').strip()
    ordering = ' ORDER BY ' + order_column if order_column else ''
    query = text(f'SELECT * FROM {schema}.{table}{ordering}')
    with database_engine().connect() as connection:
        result = connection.execute(query)
        columns = list(result.keys())
        rows = [tuple(row) for row in result.fetchall()]
    return columns, rows


@app.get('/')
def dashboard():
    columns, rows, error = [], [], None
    try:
        columns, rows = fetch_sales()
    except (ValueError, ImportError) as exc:
        error = str(exc) if isinstance(exc, ValueError) else 'Could not identify the error.'
    except SQLAlchemyError:
        error = ('Could not read the Sales table. Check your server and database names, '
                 'SQL login, client IP firewall rule, installed ODBC driver, and SELECT permission. '
                 'Also check SQL_SCHEMA, SQL_TABLE, and SQL_ORDER_COLUMN in .env.')
    return render_template(
        'dashboard.html', columns=columns, rows=rows, error=error,
        table_name=os.getenv('SQL_SCHEMA', 'dbo') + '.' + os.getenv('SQL_TABLE', 'Sales'),
        updated=datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M:%S UTC') if not error else None,
    ), (503 if error else 200)


@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
