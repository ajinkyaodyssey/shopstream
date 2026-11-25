import os

import psycopg
from fastapi import FastAPI

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://shop:shop@localhost:5432/inventory"
)

app = FastAPI(title="Inventory Service")


def get_conn():
    return psycopg.connect(DATABASE_URL)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def list_products():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, price, stock FROM products ORDER BY id")
            rows = cur.fetchall()
    return [
        {"id": r[0], "name": r[1], "price": float(r[2]), "stock": r[3]}
        for r in rows
    ]
