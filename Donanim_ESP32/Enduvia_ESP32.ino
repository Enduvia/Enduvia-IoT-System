/*
 * Proje Adı: Enduvia - Gerçek Zamanlı IoT Veri Akış Sistemi
 * Geliştirici: [Eren/Horasan] (Donanım ve Gömülü Sistem) & [Aysenur/Ulusoy] (Veri Yönetimi ve Arayüz)
 * Donanım: ESP32, DHT11 (Sıcaklık ve Nem), LDR (Işık)
 * Açıklama: Bu donanım modülü, çevresel verileri okuyup güvenli bir şekilde (Kimlik Doğrulamalı) 
 * Firebase Realtime Database'e gönderir. Python/Streamlit tabanlı Enduvia kontrol paneli ile entegre çalışır.
 */

#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include <addons/TokenHelper.h>     // Firebase token yönetimi için
#include <addons/RTDBHelper.h>      // RTDB hata ayıklama için

// --- GÜVENLİK VE AĞ AYARLARI (Kullanıcı Tarafından Doldurulacak) ---
#define WIFI_SSID "BURAYA_WIFI_ADINIZI_YAZIN" 
#define WIFI_PASSWORD "BURAYA_WIFI_SIFRENIZI_YAZIN"

#define API_KEY "BURAYA_FIREBASE_API_KEY_YAZIN"
#define DATABASE_URL "BURAYA_FIREBASE_URL_YAZIN"
#define USER_EMAIL "BURAYA_FIREBASE_KULLANICI_MAILI_YAZIN"
#define USER_PASSWORD "BURAYA_FIREBASE_SIFRESI_YAZIN"

// --- DONANIM PIN TANIMLAMALARI ---
#define DHTPIN 13          // DHT11 Data Pini (GPIO 13)
#define DHTTYPE DHT11      // Sensör Tipi
#define LDRPIN 34          // LDR Analog Pini (GPIO 34)

// --- NESNE OLUŞTURMALARI ---
DHT dht(DHTPIN, DHTTYPE);
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// --- ZAMANLAYICI DEĞİŞKENLERİ (Non-Blocking Delay) ---
unsigned long son_gonderim = 0;
const long aralik = 5000;  // 5 saniyede bir veri gönderimi

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // 1. Wi-Fi Bağlantısı
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Wi-Fi'ya Baglaniliyor");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\n[BASARI] Wi-Fi Baglantisi Kuruldu!");
  Serial.print("IP Adresi: ");
  Serial.println(WiFi.localIP());

  // 2. Firebase Kurulumu ve Kimlik Doğrulama
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  config.token_status_callback = tokenStatusCallback; // Token durumunu izle
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop() {
  unsigned long su_an = millis();
  
  // millis() kullanarak bekleme yapmadan (kodu dondurmadan) 5 saniyede bir ölçüm al
  if (su_an - son_gonderim >= aralik) {
    son_gonderim = su_an;
    
    // Sensör verilerini oku
    float sicaklik = dht.readTemperature();
    float nem = dht.readHumidity();
    int isik = analogRead(LDRPIN);

    // Sensör okuma hatası kontrolü
    if (isnan(sicaklik) || isnan(nem)) {
      Serial.println("[HATA] DHT11 sensorunden veri alinamadi! Baglantilari kontrol edin.");
      return;
    }

    // Verileri Enduvia veritabanına gönder
    if (Firebase.ready()) {
      bool t_durum = Firebase.RTDB.setFloat(&fbdo, "enduvia_verileri/sicaklik", sicaklik);
      bool h_durum = Firebase.RTDB.setFloat(&fbdo, "enduvia_verileri/nem", nem);
      bool l_durum = Firebase.RTDB.setInt(&fbdo, "enduvia_verileri/isik", isik);

      if (t_durum && h_durum && l_durum) {
        Serial.printf("[OK] Veriler Enduvia Bulutuna Iletildi! S: %.1f C | N: %.1f %% | I: %d lux\n", sicaklik, nem, isik);
      } else {
        Serial.println("[HATA] Veri gonderimi basarisiz oldu: " + fbdo.errorReason());
      }
    }
  }
}
