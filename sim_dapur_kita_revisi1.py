import streamlit as st
import hashlib
import json
import os
from datetime import datetime

# ------------------- Konstanta dan Inisialisasi -------------------
PRODUCTS = {
    "Sendok A": 15000,
    "Sendok B": 20000,
    "Sendok C": 25000,
    "Sendok D": 30000,
    "Pisau A": 15000,
    "Pisau B": 20000,
    "Pisau Bungkus (C)": 30000,
    "Saringan": 10000,
    "Toples kecil": 12000
}
DATA_FILE = "dapur_kita_data.json"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = hashlib.sha256("dapur123".encode()).hexdigest()

# ------------------- Fungsi Utilitas -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"inventory": [], "transactions": [], "sales": [], "journal_entries": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# ------------------- Halaman Login -------------------
def login_page():
    st.title("DAPUR KITA - LOGIN")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == DEFAULT_USERNAME and hash_password(password) == DEFAULT_PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Username atau password salah.")

# ------------------- Halaman Home -------------------
def home_page():
    st.title("TOKO DAPUR KITA")
    st.markdown("""
    Selamat datang di Sistem Manajemen Toko Dapur Kita!
    """)
    menu = st.selectbox("Pilih Menu", [
        "🏠 Home", 
        "📦 Persediaan", 
        "🧾 Transaksi", 
        "💰 Pendapatan", 
        "📒 Jurnal Umum", 
        "📊 Profitabilitas"
    ])
    if menu == "🏠 Home":
        st.info("Silakan pilih menu lain di atas untuk mulai menggunakan aplikasi.")
    elif menu == "📦 Persediaan":
        inventory_page()
    elif menu == "🧾 Transaksi":
        transaction_page()
    elif menu == "💰 Pendapatan":
        sales_page()
    elif menu == "📒 Jurnal Umum":
        journal_page()
    elif menu == "📊 Profitabilitas":
        profitability_page()

# ------------------- Halaman Persediaan -------------------
def inventory_page():
    st.header("Tambah Transaksi Persediaan")
    data = st.session_state["data"]

    with st.form("form_inventory"):
        date = st.text_input("Tanggal (YYYY-MM-DD)")
        product = st.selectbox("Jenis Barang", list(PRODUCTS.keys()))
        price = PRODUCTS[product]
        st.markdown(f"**Harga per Barang:** Rp {price}")
        quantity = st.number_input("Jumlah Barang", min_value=1, value=1)
        method = st.selectbox("Metode Pembayaran", ["Tunai", "Kredit", "Retur Pembelian"])
        submitted = st.form_submit_button("Tambah Transaksi")

        if submitted:
            if not validate_date(date):
                st.error("Format tanggal tidak valid.")
            else:
                total = quantity * price * (-1 if method == "Retur Pembelian" else 1)
                keterangan = "Retur Pembelian" if method == "Retur Pembelian" else "Pembelian"

                data["inventory"].append({
                    "date": date, "product": product,
                    "quantity": quantity, "price": price, "total": total
                })
                data["transactions"].append({
                    "date": date, "type": product,
                    "description": keterangan, "amount": total,
                    "payment_method": method
                })

                # Jurnal
                if method == "Retur Pembelian":
                    data["journal_entries"].append({
                        "date": date, "description": f"Retur pembelian {product}",
                        "account": "Utang Usaha", "debit": 0, "credit": -total
                    })
                    data["journal_entries"].append({
                        "date": date, "description": f"Pengurangan persediaan karena retur {product}",
                        "account": "Persediaan", "debit": -total, "credit": 0
                    })
                else:
                    data["journal_entries"].append({
                        "date": date, "description": f"Pembelian {product}",
                        "account": "Persediaan", "debit": total, "credit": 0
                    })
                    if method == "Tunai":
                        data["journal_entries"].append({
                            "date": date, "description": f"Pembayaran tunai pembelian {product}",
                            "account": "Kas", "debit": 0, "credit": total
                        })
                save_data(data)
                st.success("Transaksi persediaan berhasil ditambahkan.")

# ------------------- Halaman Pendapatan -------------------
def sales_page():
    st.header("Tambah Pendapatan")
    data = st.session_state["data"]

    with st.form("form_sales"):
        date = st.text_input("Tanggal (YYYY-MM-DD)")
        product = st.selectbox("Barang", list(PRODUCTS.keys()))
        price = PRODUCTS[product]
        st.markdown(f"**Harga per Barang:** Rp {price}")
        quantity = st.number_input("Jumlah Terjual", min_value=1, value=1)
        method = st.selectbox("Metode Pembayaran", ["Tunai", "Kredit", "Retur Penjualan"])
        submitted = st.form_submit_button("Tambah Pendapatan")

        if submitted:
            if not validate_date(date):
                st.error("Format tanggal tidak valid.")
            else:
                total = price * quantity * (-1 if method == "Retur Penjualan" else 1)
                keterangan = "Retur Penjualan" if method == "Retur Penjualan" else "Penjualan"

                data["sales"].append({
                    "date": date, "product": product, "price": price,
                    "quantity": quantity, "total": total, "payment_method": method
                })
                data["transactions"].append({
                    "date": date, "type": product,
                    "description": keterangan, "amount": total, "payment_method": method
                })

                # Jurnal
                if method == "Retur Penjualan":
                    data["journal_entries"].append({
                        "date": date, "description": f"Retur penjualan {product}",
                        "account": "Persediaan", "debit": -total, "credit": 0
                    })
                    data["journal_entries"].append({
                        "date": date, "description": f"Pengembalian kas karena retur {product}",
                        "account": "Kas", "debit": 0, "credit": -total
                    })
                else:
                    akun = "Kas" if method == "Tunai" else "Piutang Usaha"
                    data["journal_entries"].append({
                        "date": date, "description": f"{keterangan.lower()} {product}",
                        "account": akun, "debit": total, "credit": 0
                    })
                    data["journal_entries"].append({
                        "date": date, "description": f"Pengurangan persediaan karena {keterangan.lower()} {product}",
                        "account": "Persediaan", "debit": 0, "credit": total
                    })

                save_data(data)
                st.success("Pendapatan berhasil ditambahkan.")

# ------------------- Halaman Transaksi -------------------
def transaction_page():
    st.header("Data Transaksi")
    data = st.session_state["data"]
    if data["transactions"]:
        st.dataframe(data["transactions"])
        index_to_delete = st.number_input("Pilih indeks transaksi untuk dihapus", min_value=0, max_value=len(data["transactions"])-1)
        if st.button("Hapus Transaksi"):
            transaksi = data["transactions"].pop(index_to_delete)
            data["inventory"] = [item for item in data["inventory"] if not (item["total"] == transaksi["amount"] and item["product"] == transaksi["type"])]
            data["sales"] = [item for item in data["sales"] if not (item["total"] == transaksi["amount"] and item["product"] == transaksi["type"])]
            data["journal_entries"] = [entry for entry in data["journal_entries"] if entry["date"] != transaksi["date"] or entry["description"].find(transaksi["type"]) == -1]
            save_data(data)
            st.success("Transaksi berhasil dihapus.")
            st.rerun()
    else:
        st.info("Belum ada transaksi.")

# ------------------- Halaman Jurnal -------------------
def journal_page():
    st.header("Jurnal Umum")
    data = st.session_state["data"]
    if data["journal_entries"]:
        st.dataframe(data["journal_entries"])
        index_to_delete = st.number_input("Pilih indeks jurnal untuk dihapus", min_value=0, max_value=len(data["journal_entries"])-1)
        if st.button("Hapus Jurnal"):
            deleted = data["journal_entries"].pop(index_to_delete)
            save_data(data)
            st.success(f"Entri jurnal pada tanggal {deleted['date']} dengan akun {deleted['account']} berhasil dihapus.")
            st.rerun()
    else:
        st.info("Belum ada entri jurnal.")

# ------------------- Halaman Profitabilitas -------------------
def profitability_page():
    st.header("Laporan Profitabilitas")
    data = st.session_state["data"]
    total_inventory = sum(item["total"] for item in data["inventory"])
    total_sales = sum(item["total"] for item in data["sales"])
    profit = total_sales - total_inventory

    st.metric("Total Biaya Produksi", f"Rp {total_inventory:,.0f}")
    st.metric("Total Pendapatan", f"Rp {total_sales:,.0f}")
    st.metric("Laba/Rugi", f"Rp {profit:,.0f}")

# ------------------- Main -------------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "data" not in st.session_state:
        st.session_state["data"] = load_data()

    if not st.session_state["logged_in"]:
        login_page()
    else:
        home_page()

if __name__ == "__main__":
    main()