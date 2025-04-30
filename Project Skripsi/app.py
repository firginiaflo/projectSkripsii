import streamlit as st
import pandas as pd
import joblib
import sqlite3
import hashlib

# Load model
model = joblib.load("model_rekomendasi2.pkl")

# Pertanyaan DASS
questions = [
    "1. Menjadi marah karena hal-hal kecil/sepele", 
    "2. Mulut terasa kering",
    "3. Tidak dapat melihat hal yang positif dari suatu kejadian", 
    "4. Merasakan gangguan dalam bernapas (napas cepat, sulit bernapas)",
    "5. Merasa sepertinya tidak kuat lagi untuk melakukan suatu kegiatan", 
    "6. Cenderung bereaksi berlebihan pada situasi", 
    "7. Kelemahan pada anggota tubuh",
    "8. Sulit relaksasi atau bersantai", 
    "9. Cemas berlebihan dalam suatu situasi namun bisa lega jika hal atau situasi berakhir", 
    "10. Pesimis", 
    "11. Mudah merasa kesal",
    "12. Merasa banyak menghabiskan energi karena cemas", 
    "13. Sedih dan depresi", 
    "14. Tidak sabaran", 
    "15. Kelelahan",
    "16. Kehilangan minat pada banyak hal (misalnya: makan, ambulasi, sosialisasi)", 
    "17. Merasa tidak layak", 
    "18. Mudah tersinggung", 
    "19. Berkeringat tanpa stimulasi oleh cuaca maupun latihan fisik",
    "20. Ketakutan tanpa alasan", 
    "21. Merasa hidup tidak berharga", 
    "22. Sulit istirahat", 
    "23. Kesulitan dalam menelan",
    "24. Tidak dapat menikmati hal-hal yang dilakukan", 
    "25. Perubahan kegiatan jantung dan denyut nadi tanpa stimulasi oleh latihan fisik", 
    "26. Merasa hilang harapan dan putus asa", 
    "27. Mudah marah", 
    "28. Mudah panik",
    "29. Kesulitan untuk tenang setelah sesuatu yang mengganggu", 
    "30. Takut diri terhambat oleh tugas-tugas yang tidak biasa dilakukan", 
    "31. Sulit untuk antusias pada banyak hal", 
    "32. Sulit mentoleransi gangguan-gangguan terhadap hal yang sedang dilakukan",
    "33. Berada pada keadaan tegang", 
    "34. Merasa tidak berharga", 
    "35. Tidak dapat memaklumi hal apapun yang menghalangi anda untuk menyelesaikan hal yang sedang Anda lakukan", 
    "36. Ketakutan",
    "37. Tidak ada harapan untuk masa depan", 
    "38. Merasa hidup tidak berarti", 
    "39.	Mudah gelisah", 
    "40. Khawatir dengan situasi saat diri Anda mungkin menjadi panik dan mempermalukan diri sendiri",
    "41. Gemetar", 
    "42. Sulit untuk meningkatkan inisiatif dalam melakukan sesuatu"
]

# Buat database dan tabel
def create_tables():
    with sqlite3.connect("user_data.db") as conn:
        c = conn.cursor()
        q_columns = ', '.join([f"Q{i+1} INTEGER" for i in range(42)])
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS hasil (
                nama TEXT,
                nim TEXT,
                keluhan TEXT,
                rekomendasi TEXT,
                skor_depresi INTEGER,
                skor_kecemasan INTEGER,
                skor_stres INTEGER,
                {q_columns}
            )
        ''')
        c.execute('''CREATE TABLE IF NOT EXISTS konselor (
            username TEXT,
            password TEXT
        )''')
        conn.commit()

create_tables()

# # Akun konselor 
# def tambah_konselor_default():
#     username = "admin"
#     password = "admin123"
#     password_hash = hashlib.sha256(password.encode()).hexdigest()
#     with sqlite3.connect("user_data.db") as conn:
#         c = conn.cursor()
#         c.execute("SELECT * FROM konselor WHERE username = ?", (username,))
#         if not c.fetchone():
#             c.execute("INSERT INTO konselor (username, password) VALUES (?, ?)", (username, password_hash))
#             conn.commit()

# tambah_konselor_default()


# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login konselor
def login_konselor(username, password):
    password_hash = hash_password(password)
    with sqlite3.connect("user_data.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM konselor WHERE username = ? AND password = ?", (username, password_hash))
        return c.fetchone()

# Interpretasi DASS
def interpretasi_dass(nilai, tipe):
    if tipe == "Depresi":
        if nilai <= 9: return "Normal"
        elif nilai <= 13: return "Ringan"
        elif nilai <= 20: return "Sedang"
        elif nilai <= 27: return "Parah"
        else: return "Sangat Parah"
    elif tipe == "Kecemasan":
        if nilai <= 7: return "Normal"
        elif nilai <= 9: return "Ringan"
        elif nilai <= 14: return "Sedang"
        elif nilai <= 19: return "Parah"
        else: return "Sangat Parah"
    elif tipe == "Stres":
        if nilai <= 14: return "Normal"
        elif nilai <= 18: return "Ringan"
        elif nilai <= 25: return "Sedang"
        elif nilai <= 33: return "Parah"
        else: return "Sangat Parah"

# Hitung skor DASS
def hitung_dass(row):
    dep = [3,5,10,13,16,17,21,24,26,31,34,37,38]
    anx = [2,4,7,9,12,19,20,23,25,28,30,36,40,41]
    stres = [1,6,8,11,14,15,18,22,27,29,32,33,35,39,42]
    skor_dass = {
        'Depresi': sum(int(row[f"Q{i}"]) for i in dep),
        'Kecemasan': sum(int(row[f"Q{i}"]) for i in anx),
        'Stres': sum(int(row[f"Q{i}"]) for i in stres)
    }
    return skor_dass

# Halaman Mahasiswa
def mahasiswa_page():
    st.title("Form Mahasiswa")
    nama = st.text_input("Nama")
    nim = st.text_input("NIM")
    keluhan = st.text_area("Keluhan atau Permasalahan")

    with st.container():
        st.markdown("""
        <div style='text-align: center'>
            <h3>Kuesioner DASS</h3>
            <p>(0 = Tidak Pernah, 1 = Jarang, 2 = Sering, 3 = Selalu)</p>
        </div>
        """, unsafe_allow_html=True)

    responses = []
    all_answered = True

    for i, q in enumerate(questions):
        jawaban = st.selectbox(q, options=["", 0, 1, 2, 3], key=f"q{i}")
        if jawaban == "":
            all_answered = False
        responses.append(jawaban)

    if st.button("Submit"):
        if not nama.strip():
            st.warning("Nama wajib diisi")
        elif not nim.strip():
            st.warning("NIM wajib diisi.")
        elif not all_answered:
            st.warning("Semua pertanyaan DASS harus dijawab.")
        else:
            # Buat DataFrame
            df = pd.DataFrame([responses], columns=[f"Q{i+1}" for i in range(42)])

            # Prediksi pendekatan
            rekomendasi = model.predict(df)[0]

            # Hitung skor DASS
            skor_dass = hitung_dass(df.iloc[0])

            # Tambah definisi
            kolom_tambahan = ['nama', 'nim', 'keluhan', 'rekomendasi', 'skor_depresi', 'skor_kecemasan', 'skor_stres']
            all_columns = ', '.join(kolom_tambahan + list(df.columns))  # hasil: "nama, nim, ..., Q1, Q2, ..., Q42"
            placeholders = ','.join(['?'] * (7 + 42))
            values = (nama, nim, keluhan, rekomendasi, skor_dass['Depresi'], skor_dass['Kecemasan'], skor_dass['Stres'], *responses)



            # Simpan ke Database
            with sqlite3.connect("user_data.db") as conn:
                c = conn.cursor()
                placeholders = ','.join(['?'] * (7 + 42)) #4 data, 3 skor, 42 pertanyaan
                query = f"INSERT INTO hasil ({all_columns}) VALUES ({placeholders})"
                values = (nama, nim, keluhan, rekomendasi, skor_dass['Depresi'], skor_dass['Kecemasan'], skor_dass['Stres'], *responses)
                c.execute(query, values)
                conn.commit()
            st.success("Jawaban Anda berhasil disimpan.")

# Halaman Konselor
def konselor_page():
    if st.session_state.get("login_konselor"):
        tampilkan_dashboard_konselor()
    else:
        form_login_konselor()

def form_login_konselor():
    st.title("Login Konselor")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_konselor(username, password):
            st.success("Login berhasil")
            st.session_state['login_konselor'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Login gagal. Periksa username dan password.")

def tampilkan_dashboard_konselor():
    st.title("Riwayat Mahasiswa")

    with sqlite3.connect("user_data.db") as conn:
        conn.row_factory = sqlite3.Row
        hasil = pd.read_sql("SELECT rowid, * FROM hasil", conn)

    if hasil.empty:
        st.info("Belum ada data.")
        return

    label_to_rowid = {
        f"{row['nama']} ({row['nim']})": row['rowid']
        for _, row in hasil.iterrows()
    }

    selected_label = st.selectbox("Pilih Mahasiswa", list(label_to_rowid.keys()))
    selected_rowid = label_to_rowid[selected_label]
    data = hasil[hasil["rowid"] == selected_rowid].iloc[0]

    st.write(f"**Nama:** {data['nama']}")
    st.write(f"**NIM:** {data['nim']}")
    st.write(f"**Keluhan:** {data['keluhan']}")
    st.write(f"**Rekomendasi Pendekatan:** `{data['rekomendasi']}`")


    st.subheader("Indikator DASS")

    skor_dass = {
        "Depresi": data['skor_depresi'],
        "Kecemasan": data['skor_kecemasan'],
        "Stres": data['skor_stres']
}
    for tipe in skor_dass:
        nilai = skor_dass[tipe]
        kategori = interpretasi_dass(skor_dass[tipe], tipe)
        st.write(f"- {tipe}: {nilai} → **{kategori}**")

    st.markdown("### 📊 Visualisasi Skor DASS")
    df_chart = pd.DataFrame.from_dict(skor_dass, orient='index', columns=['Skor'])
    st.bar_chart(df_chart)

    # Tombol Logout
    if st.button("Logout"):
        st.session_state['login_konselor'] = False
        st.session_state['username'] = ""
        st.success("Anda telah logout.")
        st.rerun()
    
# Navigasi
menu = st.sidebar.selectbox("Pilih Halaman", ["Mahasiswa", "Konselor"])
if menu == "Mahasiswa":
    mahasiswa_page()
else:
    konselor_page()
