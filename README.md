
# İzin Takip Sistemi

İzin Takip Sistemi, personel izin yönetimini kolaylaştırmak için geliştirilmiş bir web uygulamasıdır. Django framework'ü ile geliştirilmiş ve Docker kullanılarak containerized edilmiştir.

---

## 🚀 Özellikler

- Personel izin taleplerini oluşturma ve yönetme.
- Yönetici paneli ile izin taleplerini onaylama/redetme.
- **WebSocket** ile gerçek zamanlı bildirimler (Geç kalma bildirimleri için kullanılır).
- **Redis tabanlı Celery** ile arka plan işlemleri (Yıllık izin güncelleme bildirimi için kullanılır).
- PostgreSQL veritabanı entegrasyonu.

---

## 👀 Ekran Görüntüleri

### Personel Paneli
![Personel Paneli](admin.png)

Personel panelinde kullanıcı kalan izin günlerini görebilir ve "Bildirim Gönder" butonunu kullanarak giriş saatini belirtebilir.

### Yetkili Paneli
![Yetkili Paneli](./çalışan.png)

Yetkili panelinde:
- Mavi alan içindeki geç kalma bildirimleri **WebSocket** ile gerçek zamanlı olarak gelir.
- Diğer izin güncelleme bildirimleri ise **Celery** arka plan görevleri ile iletilir.

---

## 📂 Proje Yapısı

```
izin_takip/
├── accounts/              # Kullanıcı işlemleri (giriş, kayıt, profil)
├── leave_management/      # İzin yönetimi
├── izin_takip/            # Proje ayarları ve asıl dosyalar
├── templates/             # HTML şablonları
├── Dockerfile             # Docker imajını oluşturmak için
├── docker-compose.yml     # Çoklu servis yönetimi için
├── requirements.txt       # Gerekli Python kütüphaneleri
└── README.md              # Proje açıklaması
```

---

## 🛠️ Gereksinimler

- **Docker** ve **Docker Compose**
- **Python 3.9+**
- **PostgreSQL** (Docker ile birlikte gelir)
- **Redis** (Docker ile birlikte gelir)

---

## 🔧 Kurulum

1. **Projeyi klonlayın:**

   ```bash
   git clone https://github.com/kullanici/izin-takip-sistemi.git
   cd izin-takip-sistemi
   ```

2. **Docker ile ortamı başlatın:**

   ```bash
   docker-compose up --build
   ```

3. **Veritabanı migrasyonlarını çalıştırın:**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Statik dosyaları toplayın:**

   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

5. **Süper kullanıcı oluşturun:**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Yetkili Paneli Kullanıcı Giriş Bilgileri**:
   - Kullanıcı adı: **twontechadmin**
   - Şifre: **admin1234**

---

## 🚀 Çalıştırma

Uygulamayı başlatmak için:

```bash
docker-compose up
```

Uygulamaya şu adresten erişebilirsiniz: [http://localhost:8000](http://localhost:8000)

---

## 🔒 Ortam Değişkenleri

Aşağıdaki ortam değişkenlerini `.env` dosyasına ekleyin:

```env
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
POSTGRES_DB=postgres
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin1234
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 📦 Docker Servisleri

- **Web:** Django uygulaması (Port: 8000)
- **DB:** PostgreSQL veritabanı (Port: 5432)
- **Redis:** Mesajlaşma ve görev kuyruğu (Port: 6379)
- **Celery Worker:** Arka plan görevleri için Celery işçisi

---

## 🔧 Geliştirme

Geliştirme ortamında çalıştırmak için:

1. **Docker servislerini başlatın:**

   ```bash
   docker-compose up
   ```

2. **Kodda değişiklik yapın ve sayfayı yenileyin.**

---

## 🛠️ Test

Birim testlerini çalıştırmak için:

```bash
docker-compose exec web python manage.py test
```
Projeyi çalıştırdıktan sonra /swagger/ URL'sine giderek Swagger dokümantasyonunu görüntüleyebilirsiniz.
---
## 📜 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasını inceleyin.
