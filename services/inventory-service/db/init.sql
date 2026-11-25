CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL
);

INSERT INTO products (name, price, stock) VALUES
    ('Wireless Mouse', 799.00, 50),
    ('Mechanical Keyboard', 3499.00, 20),
    ('USB-C Cable', 299.00, 200),
    ('Laptop Stand', 1299.00, 35),
    ('Webcam HD', 2199.00, 15);