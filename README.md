# JARVIS • harunokmen

Türkçe, yerel ses işleme kullanan kişisel Windows asistanı. © 2026 harunokmen.

## Özellikler

- Animasyonlu küre, koyu masaüstü paneli ve sohbet alanı.
- İşlemci, bellek ve disk göstergeleri.
- Mikrofon seçimi, 8 saniyeyle sınırlı bas-konuş ve iptal düğmesi.
- Vosk ile çevrimdışı Türkçe tanıma; isteğe bağlı Windows sesli yanıtı.
- Sabit komut izin listesi; uygulama açma ve rapor için kullanıcı onayı.
- Ses kayıtları ve sohbet geçmişi diske yazılmaz.

Bu bir asistan uygulamasıdır; yeni eğitilmiş dil modeli değildir. Serbest sohbet, kişi doğrulama, uzaktan kontrol ve otomatik sistem optimizasyonu bu sürümde bulunmaz. Ses tanımanın doğruluğu mikrofon ve ortama bağlıdır.

## Kurulum

Windows ve Python 3.12 x64 (Tcl/Tk dahil) gerektirir. PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Kurulum.ps1 -Python C:\Python312\python.exe
```

Python yolunu kurulu python.exe yoluyla değiştirin. Ardından `Baslat.cmd` açın. İlk kurulum Python paketleri ve 35 MB Türkçe modelini indirir. Sonraki ses tanıma işlemleri yereldir. Tarayıcı açma komutu internete bağlanır.

## Komutlar

`saat kaç`, `tarih ne`, `sistem durumu`, `not defteri aç`, `hesap makinesi aç`, `tarayıcı aç`, `görev yöneticisi aç`, `performans raporu`, `yardım`.

Bas-konuş modunda Jarvis öneki isteğe bağlıdır. Mikrofon kapalı başlar. Konuş düğmesine basınca model hazırlanır, DİNLİYOR yazısı göründüğünde konuşun. Durdur düğmesi tanınan komutu iptal eder. Mikrofon ve Windows sesli yanıtı gerçek donanımda ayrıca doğrulanmalıdır.

## Güvenlik ve mahremiyet

Komut metni kabukta çalıştırılmaz. Onay gerektiren işlemler çekirdekte de engellenir. Bu kontrol yerel bilgisayara zaten erişebilen bir saldırgana karşı işletim sistemi güvenlik sınırı değildir. Uygulamayı standart kullanıcı olarak çalıştırın. Rapor bilgisayar bilgisi içerir ve Git'e dahil edilmez. Ayrıntılar: [SECURITY.md](SECURITY.md).

## Geliştirme

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe app.py
```

`app.py`: arayüz, iş kuyruğu ve mikrofon. `core.py`: komut çözümleme ve izin kapısı. `Performans-Raporu.ps1`: salt okunur tanılama.

Üç referans projenin panel, küre ve sohbet fikirleri özgün uygulamada birleştirildi; bu projelerin kaynak kodları kopyalanmadı. Ayrıntılar [REFERENCES.md](REFERENCES.md). İmza ürün ve telif imzasıdır; kriptografik kod imzası değildir.
