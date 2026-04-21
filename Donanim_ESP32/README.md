# 🌍 Enduvia - Gerçek Zamanlı IoT Veri Akış Sistemi

Enduvia; çevresel verileri (sıcaklık, nem ve ışık) donanım seviyesinde toplayan, Firebase bulut altyapısı üzerinden anlık olarak ileten ve kullanıcı dostu bir web arayüzü ile görselleştiren uçtan uca (End-to-End) bir IoT sistemidir.

Bu proje, bir **Elektrik-Elektronik Mühendisi** ve bir **Yönetim Bilişim Sistemleri (YBS)** öğrencisinin disiplinler arası ortak çalışmasıyla, modern IoT standartlarına uygun olarak geliştirilmiştir.

---

## 🏗️ Sistem Mimarisi

Proje üç temel katmandan oluşmaktadır:

1. **Donanım Katmanı (Edge):**
   - **Mikrodenetleyici:** ESP32
   - **Sensörler:** DHT11 (Sıcaklık ve Nem), LDR (Ortam Işığı Seviyesi)
   - **İşlev:** Verilerin milisaniye hassasiyetinde okunması ve Wi-Fi üzerinden buluta güvenli iletimi.

2. **Bulut ve Veri Yönetimi (Backend):**
   - **Altyapı:** Firebase Realtime Database
   - **Güvenlik:** Firebase Authentication ve özel güvenlik kuralları (Security Rules) ile tam izolasyon.

3. **Veri Görselleştirme (Frontend):**
   - **Teknoloji:** Python & Streamlit
   - **İşlev:** Canlı veri akışının grafiksel analizi, anlık durum takibi ve geçmiş veri kayıtlarının yönetimi.

---

## 📂 Proje Yapısı

* **Donanim_ESP32/** : Gömülü Sistem Kodları (C++ / Arduino)
* **Yazilim_Dashboard/** : Veri Görselleştirme ve Arayüz (Python)

---

## 🛡️ Güvenlik ve İzolasyon

Projenin endüstriyel standartlara yakın olması adına veri izolasyonuna büyük önem verilmiştir. Gizli API anahtarları, Wi-Fi şifreleri ve özel JSON dosyaları `.gitignore` ile korunarak GitHub üzerinde asla paylaşılmamakta, "Secrets Management" prensipleri uygulanmaktadır.

---

## 👥 Geliştiriciler

* **Eren** - *Elektrik-Elektronik Mühendisliği*
  * Donanım mimarisi, devre tasarımı ve gömülü sistem yazılımı.
* **[Sevgilinin Adı ve Soyadı]** - *Yönetim Bilişim Sistemleri (YBS)*
  * Veritabanı yönetimi, bulut entegrasyonu ve veri görselleştirme dashboard geliştirme.
