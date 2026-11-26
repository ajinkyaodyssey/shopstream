
import os
from typing import Optional  # Used for fields that can have None values

import psycopg  # PostgreSQL database connection library
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field  # Used for request data validation

# Get DB URL from environment; use local PostgreSQL URL if not provided
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://shop:shop@localhost:5432/inventory"
)

COLUMNS = "id, name, price, stock"  # Columns we need from products table

app = FastAPI(title="Inventory Service")  # Create FastAPI application


# Structure and validation rules for creating/replacing a product
class ProductIn(BaseModel):
    name: str = Field(min_length=1)  # Name cannot be empty
    price: float = Field(gt=0)  # Price must be greater than 0
    stock: int = Field(ge=0)  # Stock cannot be negative


# Structure for partially updating a product
class ProductPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)  # Optional name
    price: Optional[float] = Field(default=None, gt=0)  # Optional price
    stock: Optional[int] = Field(default=None, ge=0)  # Optional stock


def get_conn():
    return psycopg.connect(DATABASE_URL)  # Connect to PostgreSQL database


def to_product(row):
    # Convert database row into a JSON-friendly dictionary
    return {"id": row[0], "name": row[1], "price": float(row[2]), "stock": row[3]}


@app.get("/health")
def health():
    return {"status": "ok"}  # Check whether API is running


@app.get("/products")
def list_products():
    # Open database connection and cursor
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {COLUMNS} FROM products ORDER BY id")  # Fetch all products
        return [to_product(r) for r in cur.fetchall()]  # Convert rows into dictionaries


@app.get("/products/{product_id}")
def get_product(product_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT {COLUMNS} FROM products WHERE id = %s",
            (product_id,),  # Pass product ID safely as a query parameter
        )
        row = cur.fetchone()  # Fetch one matching product

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")  # Return 404 if missing

    return to_product(row)  # Return product details


@app.post("/products", status_code=201)
def create_product(body: ProductIn, response: Response):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) "
            f"RETURNING {COLUMNS}",  # Insert product and return its details
            (body.name, body.price, body.stock),  # Values from request body
        )
        row = cur.fetchone()  # Get the newly created product

    response.headers["Location"] = f"/products/{row[0]}"  # URL of new product
    return to_product(row)  # Return created product


@app.put("/products/{product_id}")
def replace_product(product_id: int, body: ProductIn):
    # PUT replaces all editable product fields
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE products SET name = %s, price = %s, stock = %s "
            f"WHERE id = %s RETURNING {COLUMNS}",  # Update and return product
            (body.name, body.price, body.stock, product_id),
        )
        row = cur.fetchone()  # Get updated product

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return to_product(row)  # Return updated product


@app.patch("/products/{product_id}")
def update_product(product_id: int, body: ProductPatch):
    # Keep only fields provided by the user; ignore fields with None
    fields = body.model_dump(exclude_none=True)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")  # Nothing to update

    # Dynamically create SQL SET clause based on supplied fields
    set_clause = ", ".join(f"{name} = %s" for name in fields)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE products SET {set_clause} WHERE id = %s RETURNING {COLUMNS}",
            (*fields.values(), product_id),  # Pass new values followed by product ID
        )
        row = cur.fetchone()  # Get updated product

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return to_product(row)  # Return updated product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM products WHERE id = %s",
            (product_id,),  # Delete product using its ID
        )
        deleted = cur.rowcount  # Number of rows deleted

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return Response(status_code=204)  # Return success with no response body
