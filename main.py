"""
Backend CRUD untuk tabel `produk` di Neon (Postgres).
FastAPI otomatis menyediakan dokumentasi OpenAPI di /docs dan /openapi.json.

Menjalankan lokal:
    export DATABASE_URL="postgresql://...neon..."   # connection string Neon
    uvicorn main:app --reload
"""
import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(
    title="Produk API",
    description="Backend CRUD untuk tabel produk di database Neon.",
    version="1.0.0",
)


def get_conn():
    """Buka koneksi ke Neon. Koneksi dibuka per-request agar aman di hosting."""
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL belum di-set")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


# --- Skema data (ini yang jadi schema di OpenAPI) ---
class ProdukInput(BaseModel):
    nama: str
    harga: int
    stok: int = 0


class Produk(ProdukInput):
    id: int


# --- Endpoint ---
@app.get("/")
def root():
    return {"status": "ok", "dokumentasi": "/docs"}


@app.get("/produk", response_model=list[Produk], summary="Ambil daftar produk")
def list_produk():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, harga, stok FROM produk ORDER BY id")
        return cur.fetchall()


@app.get("/produk/{produk_id}", response_model=Produk, summary="Ambil satu produk")
def get_produk(produk_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, harga, stok FROM produk WHERE id = %s", (produk_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        return row


@app.post("/produk", response_model=Produk, status_code=201, summary="Tambah produk")
def create_produk(data: ProdukInput):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produk (nama, harga, stok) VALUES (%s, %s, %s) "
            "RETURNING id, nama, harga, stok",
            (data.nama, data.harga, data.stok),
        )
        conn.commit()
        return cur.fetchone()


@app.put("/produk/{produk_id}", response_model=Produk, summary="Ubah produk")
def update_produk(produk_id: int, data: ProdukInput):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE produk SET nama=%s, harga=%s, stok=%s WHERE id=%s "
            "RETURNING id, nama, harga, stok",
            (data.nama, data.harga, data.stok, produk_id),
        )
        conn.commit()
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        return row


@app.delete("/produk/{produk_id}", status_code=204, summary="Hapus produk")
def delete_produk(produk_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM produk WHERE id = %s", (produk_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return None