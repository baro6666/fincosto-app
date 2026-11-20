# Mağaza kayıtları (Google Play · App Store)

Hesap: kişisel (T. Baran Dinç). Uygulama: app.fincosto.com kabuğu (Android: TWA, paket `com.fincosto.app.twa`; iOS: WKWebView).

## Ortak metinler

**Uygulama adı (30 karakter):** fincosto – Şube Yönetimi

**Kısa açıklama (Play, 80 karakter):** Restoran ve şubeler için kasa, personel, puantaj, masraf ve fatura takibi.

**Alt başlık (App Store, 30 karakter):** Kasa, personel ve şube takibi

**Uzun açıklama:**

fincosto; restoran, kafe ve çok şubeli işletmelerin günlük operasyonunu tek uygulamada toplar. İşletmeniz fincosto'ya kayıtlıysa size verilen firma kodu ve kişisel PIN'inizle giriş yaparsınız; her çalışan yalnız rolüne açılan ekranları görür.

• Kasa: günlük nakit kaydı, kasa raporu, kasa farkları, POS (Kerzz, ROP) aktarımı
• Personel: işe giriş / çıkış, puantaj, izin ve alacak izin, evrak takibi
• Bordro: maaş, avans, kesinti ve mesai hesapları
• Masraf ve fatura: fiş ile masraf girişi, gelen faturalar, cari hesaplar ve ekstreler
• Stok: günlük sayım, fark raporu, sipariş
• Onay akışı: müdür ve merkez onayları, bildirimler
• Rol ve kart yetkileri: işletme sahibi kimin hangi ekranı göreceğini seçer

Verileriniz işletmenizin kendi Google hesabındaki tablolarda tutulur. PIN'ler şifreli (geri çözülemez özet) saklanır.

Not: fincosto işletmelere yönelik bir hizmettir; uygulamayı kullanmak için işletmenizin fincosto hesabı olmalıdır. Bilgi: baran@fincosto.com

**Anahtar kelimeler (App Store, 100 karakter):** restoran,kasa,puantaj,personel,bordro,şube,masraf,fatura,stok,işletme,pos,cari

**Kategori:** İş (Business) · **Yaş sınırı:** 3+ / Herkes · **Gizlilik politikası:** https://app.fincosto.com/gizlilik.html

## İnceleme ekibine not (her iki mağaza)

> fincosto is a business (B2B) app for restaurant and multi-branch operators. Accounts are created by the business owner; there is no public sign-up.
> Demo access: open the app, enter company code `demo`, then PIN `______` (Owner) or `______` (Cashier). The demo company contains sample data only.

(Demo firması kurulunca PIN'ler buraya yazılır — gerçek müşteri verisi kullanılmaz.)

## Google Play — Veri güvenliği formu (taslak)

- Toplanan veriler: Ad (kişisel bilgi), finansal bilgi (işletme kasa/masraf kayıtları), fotoğraflar (fiş/evrak, isteğe bağlı)
- Amaç: Uygulama işlevi. Reklam / analiz / üçüncü tarafa satış: **yok**
- Aktarımda şifreleme: **evet** (HTTPS)
- Silme talebi: baran@fincosto.com (işletme sahibi kullanıcıyı siler; kayıtlar işletmenin tablosunda kalır)
- Hesap oluşturma uygulama içinden: **hayır** (işletme sahibi oluşturur)

## Görseller

- Play: simge 512×512 (`icon-512.png`), öne çıkan görsel 1024×500, telefon ekran görüntüsü en az 2 adet (1080×1920)
- App Store: 6.9" ekran görüntüleri 1290×2796 (en az 3), simge 1024×1024 (saydamlık yok)
- Ekran görüntüleri demo firmasından alınacak (gerçek veri yok).

## İndirme QR kodu

Basılı QR her zaman **https://app.fincosto.com/indir** adresine gider (firmaya özel: `/indir?f=firmakodu`, açılınca firma kodu
hazır gelir). Sayfa (`indir/index.html`) telefonu tanır: mağaza bağlantısı tanımlıysa App Store / Google Play'e, değilse
iPhone'da "Ana Ekrana Ekle", Android'de "Uygulamayı yükle" adımlarına, bilgisayarda QR'a yönlendirir. Uygulamalar mağazaya
çıkınca yalnız sayfadaki `PLAY_URL` / `APPSTORE_URL` doldurulur; **basılı QR değişmez**.
Üretim: `python3 magaza/qr-uret.py [firmakodu]` → `magaza/qr/` (QR .svg/.png, A5 afiş .png/.pdf).
