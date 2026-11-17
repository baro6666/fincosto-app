# fincosto

fincosto uygulamasinin telefon kabugu (PWA). Uygulamanin kendisi Google Apps Script uzerinde calisir.

Adres: https://app.fincosto.com/ (eski https://baro6666.github.io/fincosto-app/ adresi buraya yonlenir)

Firma linki: `https://app.fincosto.com/?f=FIRMA_KODU`

## iPhone uygulaması (`ios/`)

WKWebView ile app.fincosto.com'u açan yerel uygulama (paket `com.fincosto.app`, takım `Y7UHFYN396`).
Xcode projesi `ios/project.yml`'den XcodeGen ile üretilir. `.github/workflows/ios.yml` her `ios/` değişikliğinde
(ya da Actions → "iOS → TestFlight" → Run workflow ile elle) GitHub'ın Mac sunucusunda derleyip TestFlight'a yükler.
Gerekli sırlar: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8`.
