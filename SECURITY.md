# Güvenlik yaklaşımı

- Yalnızca tanımlı komutlar çalışır; bilinmeyen istekler reddedilir.
- Uygulama açma, web sayfası açma ve rapor üretme arayüzde açık onay ister.
- Çekirdeğin approved parametresi yalnızca güvenilen arayüz kodu tarafından geçirilir; kullanıcı metninden türetilmez.
- Mikrofon yalnızca düğmeyle açılır, 8 saniyede kapanır; iptal desteklenir. Ses biyometrik kimlik doğrulama değildir.
- Ses yanıtı sırasında yeni kayıt başlatılmaz. Stereo Karışımı engellenir.
- Uzak sunucu, dinleyen ağ portu veya bulut model bağlantısı yoktur.
- API anahtarı gerekmez. Kayıtlar, raporlar, ortamlar ve modeller Git dışında tutulur.

Sınırlamalar: Bağımlılıkların tedarik zinciri, Windows ses sürücüleri ve bilgisayardaki diğer kullanıcı süreçleri bu uygulamanın güvenlik sınırının dışındadır. Tam güvenlik garantisi veya bağımsız güvenlik denetimi iddiası yoktur. İşlem onayı bir işletim sistemi sandbox'ı değildir. Uygulama kapanırken başlamış onaylı işlem tamamlanabilir.

Güvenlik sorunu bildirirken erişim anahtarı, ses kaydı veya kişisel sistem raporu eklemeyin. GitHub deposunda özel güvenlik bildirimi etkinleştirildikten sonra onu kullanın.
