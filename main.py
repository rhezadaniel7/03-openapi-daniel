"""
Backend CRUD untuk tabel `produk` di Neon (Postgres) — Level 3 (HATEOAS).
Setiap response produk menyertakan `_links`. Sebagian link BERSYARAT pada stok:
inilah "engine of application state" — link berubah mengikuti state data.
"""
import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(
    title="Produk API",
    description="Backend CRUD untuk tabel produk di database Neon. Level 3 (HATEOAS).",
    version="2.0.0",
)


def get_conn():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL belum di-set")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


class ProdukInput(BaseModel):
    nama: str
    harga: int
    stok: int = 0


def build_links(produk_id: int, stok: int) -> dict:
    """Link navigasi. Yang bersyarat pada stok = bukti HATEOAS Level 3 sesungguhnya."""
    links = {
        "self":   {"href": f"/produk/{produk_id}", "method": "GET"},
        "update": {"href": f"/produk/{produk_id}", "method": "PUT"},
        "delete": {"href": f"/produk/{produk_id}", "method": "DELETE"},
        "list":   {"href": "/produk", "method": "GET"},
    }
    # Link berubah tergantung state:
    if stok > 0:
        links["kurangi-stok"] = {"href": f"/produk/{produk_id}/kurangi-stok", "method": "POST"}
    else:  # stok habis -> tidak bisa dikurangi, tawarkan restock
        links["restock"] = {"href": f"/produk/{produk_id}/restock", "method": "POST"}
    return links


def with_links(row: dict) -> dict:
    return {**row, "_links": build_links(row["id"], row["stok"])}


@app.get("/")
def root():
    return {"status": "ok", "dokumentasi": "/docs"}


@app.get("/produk", summary="Ambil daftar produk")
def list_produk():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, harga, stok FROM produk ORDER BY id")
        rows = cur.fetchall()
    return [with_links(r) for r in rows]


@app.get("/produk/{produk_id}", summary="Ambil satu produk")
def get_produk(produk_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, harga, stok FROM produk WHERE id = %s", (produk_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return with_links(row)


@app.post("/produk", status_code=201, summary="Tambah produk")
def create_produk(data: ProdukInput):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produk (nama, harga, stok) VALUES (%s, %s, %s) "
            "RETURNING id, nama, harga, stok",
            (data.nama, data.harga, data.stok),
        )
        conn.commit()
        row = cur.fetchone()
    return with_links(row)


@app.put("/produk/{produk_id}", summary="Ubah produk")
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
    return with_links(row)


@app.delete("/produk/{produk_id}", status_code=204, summary="Hapus produk")
def delete_produk(produk_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM produk WHERE id = %s", (produk_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return None


@app.post("/produk/{produk_id}/kurangi-stok", summary="Kurangi stok produk")
def kurangi_stok(produk_id: int, jumlah: int = 1):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, harga, stok FROM produk WHERE id = %s", (produk_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        if jumlah > row["stok"]:
            raise HTTPException(status_code=409, detail="Stok tidak cukup")
        cur.execute(
            "UPDATE produk SET stok = stok - %s WHERE id = %s "
            "RETURNING id, nama, harga, stok",
            (jumlah, produk_id),
        )
        conn.commit()
        row = cur.fetchone()
    return with_links(row)


@app.post("/produk/{produk_id}/restock", summary="Tambah stok produk")
def restock(produk_id: int, jumlah: int = 10):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE produk SET stok = stok + %s WHERE id = %s "
            "RETURNING id, nama, harga, stok",
            (jumlah, produk_id),
        )
        conn.commit()
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return with_links(row)