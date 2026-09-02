# Produk API — Backend CRUD di atas Neon (FastAPI + Render)
# Daniel - 5803024005
Backend yang mengubah isi tabel `produk` di database Neon lewat REST API.
Dokumentasi OpenAPI otomatis tersedia di `/docs` dan `/openapi.json`.

## Endpoint
| Method | Path             | Fungsi              |
|--------|------------------|---------------------|
| GET    | /produk          | Ambil semua produk  |
| GET    | /produk/{id}     | Ambil satu produk   |
| POST   | /produk          | Tambah produk       |
| PUT    | /produk/{id}     | Ubah produk         |
| DELETE | /produk/{id}     | Hapus produk        |

## Langkah singkat
1. Buat tabel di Neon SQL Editor -> jalankan `create-table-neon.sql`.
2. Salin connection string Neon (yang ada `-pooler`, mode `require`).
3. Push repo ini ke GitHub.
4. Di Render: New -> Web Service -> connect repo.
   - Build command : pip install -r requirements.txt
   - Start command : uvicorn main:app --host 0.0.0.0 --port $PORT
   - Environment   : DATABASE_URL = (connection string Neon)
5. Buka URL Render + `/docs` untuk mencoba API.

## Menjalankan lokal
    export DATABASE_URL="postgresql://...neon..."
    pip install -r requirements.txt
    uvicorn main:app --reload
    # buka https://03-openapi-daniel-six.vercel.app/docs