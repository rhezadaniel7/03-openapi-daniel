CREATE TABLE IF NOT EXISTS produk (
    id     SERIAL PRIMARY KEY,
    nama   VARCHAR(255) NOT NULL,
    harga  INTEGER      NOT NULL,
    stok   INTEGER      DEFAULT 0
);

INSERT INTO produk (nama, harga, stok) VALUES
    ('Kopi Susu', 18000, 25),
    ('Teh Tarik', 15000, 40);