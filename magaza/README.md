# Mağaza kayıtları (Google Play · App Store)

Hesap: kişisel (T. Baran Dinç). Uygulama: app.fincosto.com kabuğu (Android: TWA, paket `com.fincosto.app.twa`; iOS: WKWebView).

## Ortak metinler

**Uygulama adı:** fincosto

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

Demo firması: kod `demo` ("Demo Restoran", uydurma veri). Demo PIN'leri bu depoya yazılmaz (depo herkese açık); App Store Connect → App Review → Sign-in bölümüne ve Play Console → Uygulama erişimi'ne elle girilir.

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

## App Store kaydı (API)

GitHub → Actions → **App Store kaydı** → Run workflow → `islem`:
`durum` (okur) · `doldur` (metin.json: metinler, kategori, yaş sınırı, ücretsiz, inceleme bilgisi, son yapı) · `gorsel`
(`magaza/ekran/appstore`) · `gonder` (incelemeye gönderir). **App Privacy** bölümü API'de yok, elle doldurulur.
Ekran görüntüleri: `magaza/ekran/play` (1080×1920), `magaza/ekran/appstore` (1290×2796), demo firmadan.
