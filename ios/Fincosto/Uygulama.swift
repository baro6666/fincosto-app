import UIKit
import WebKit

// fincosto iOS uygulaması: app.fincosto.com kabuğunu tam ekran açar.
// Uygulamanın kendisi web'de çalışır; burası yalnız yerel çerçeve (yenileme, çevrimdışı ekranı,
// harici bağlantılar, açılır pencereler, kamera / fotoğraf erişimi).

let ANA_ADRES = URL(string: "https://app.fincosto.com/")!
let LACIVERT = UIColor(red: 0x0E / 255, green: 0x1D / 255, blue: 0x33 / 255, alpha: 1)
let ALTIN = UIColor(red: 0xC9 / 255, green: 0xA2 / 255, blue: 0x4A / 255, alpha: 1)

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        let w = UIWindow(frame: UIScreen.main.bounds)
        w.backgroundColor = LACIVERT
        w.rootViewController = AnaEkran()
        w.makeKeyAndVisible()
        window = w
        return true
    }

    // fincosto bağlantısıyla açılış (ör. https://app.fincosto.com/?f=firma)
    func application(_ application: UIApplication, continue userActivity: NSUserActivity,
                     restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        if let url = userActivity.webpageURL, let ana = window?.rootViewController as? AnaEkran {
            ana.ac(url)
            return true
        }
        return false
    }
}

class AnaEkran: UIViewController, WKNavigationDelegate, WKUIDelegate {
    private var web: WKWebView!
    private let cevrimdisi = UIView()
    private let yukleniyor = UIActivityIndicatorView(style: .large)
    private var yuklendi = false

    override var preferredStatusBarStyle: UIStatusBarStyle { .lightContent }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = LACIVERT

        let ayar = WKWebViewConfiguration()
        ayar.websiteDataStore = .default()          // oturum ve firma kodu cihazda kalır
        ayar.allowsInlineMediaPlayback = true
        ayar.defaultWebpagePreferences.allowsContentJavaScript = true
        ayar.preferences.javaScriptCanOpenWindowsAutomatically = true

        web = WKWebView(frame: .zero, configuration: ayar)
        web.navigationDelegate = self
        web.uiDelegate = self
        web.allowsBackForwardNavigationGestures = false
        web.isOpaque = false
        web.backgroundColor = LACIVERT
        web.scrollView.backgroundColor = LACIVERT
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.customUserAgent = nil
        web.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(web)
        NSLayoutConstraint.activate([
            web.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            web.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            web.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            web.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        ])

        // Aşağı çekip yenile
        let yenile = UIRefreshControl()
        yenile.tintColor = ALTIN
        yenile.addTarget(self, action: #selector(yenileCekildi(_:)), for: .valueChanged)
        web.scrollView.refreshControl = yenile

        yukleniyor.color = ALTIN
        yukleniyor.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(yukleniyor)
        NSLayoutConstraint.activate([
            yukleniyor.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            yukleniyor.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])

        cevrimdisiKur()
        ac(ANA_ADRES)
    }

    func ac(_ url: URL) {
        cevrimdisi.isHidden = true
        if !yuklendi { yukleniyor.startAnimating() }
        web.load(URLRequest(url: url))
    }

    @objc private func yenileCekildi(_ s: UIRefreshControl) {
        if web.url == nil || !cevrimdisi.isHidden { ac(ANA_ADRES) } else { web.reload() }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { s.endRefreshing() }
    }

    // ── Çevrimdışı ekranı ──
    private func cevrimdisiKur() {
        cevrimdisi.backgroundColor = LACIVERT
        cevrimdisi.isHidden = true
        cevrimdisi.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(cevrimdisi)
        NSLayoutConstraint.activate([
            cevrimdisi.topAnchor.constraint(equalTo: view.topAnchor),
            cevrimdisi.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            cevrimdisi.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            cevrimdisi.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        ])
        let baslik = UILabel()
        baslik.text = "İnternet bağlantısı yok"
        baslik.font = .boldSystemFont(ofSize: 20)
        baslik.textColor = .white
        let aciklama = UILabel()
        aciklama.text = "fincosto'yu kullanmak için internete bağlanın."
        aciklama.font = .systemFont(ofSize: 15)
        aciklama.textColor = UIColor(white: 0.75, alpha: 1)
        aciklama.numberOfLines = 0
        aciklama.textAlignment = .center
        let dugme = UIButton(type: .system)
        dugme.setTitle("Tekrar dene", for: .normal)
        dugme.titleLabel?.font = .boldSystemFont(ofSize: 17)
        dugme.backgroundColor = ALTIN
        dugme.setTitleColor(LACIVERT, for: .normal)
        dugme.layer.cornerRadius = 12
        dugme.contentEdgeInsets = UIEdgeInsets(top: 14, left: 28, bottom: 14, right: 28)
        dugme.addTarget(self, action: #selector(tekrarDene), for: .touchUpInside)
        let yigin = UIStackView(arrangedSubviews: [baslik, aciklama, dugme])
        yigin.axis = .vertical
        yigin.alignment = .center
        yigin.spacing = 16
        yigin.translatesAutoresizingMaskIntoConstraints = false
        cevrimdisi.addSubview(yigin)
        NSLayoutConstraint.activate([
            yigin.centerXAnchor.constraint(equalTo: cevrimdisi.centerXAnchor),
            yigin.centerYAnchor.constraint(equalTo: cevrimdisi.centerYAnchor),
            yigin.leadingAnchor.constraint(greaterThanOrEqualTo: cevrimdisi.leadingAnchor, constant: 32),
        ])
    }

    @objc private func tekrarDene() { ac(web.url ?? ANA_ADRES) }

    // ── Gezinme ──
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        yuklendi = true
        yukleniyor.stopAnimating()
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        hataGoster(error)
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        hataGoster(error)
    }

    private func hataGoster(_ error: Error) {
        let e = error as NSError
        if e.domain == NSURLErrorDomain && e.code == NSURLErrorCancelled { return }
        yukleniyor.stopAnimating()
        if e.domain == NSURLErrorDomain { cevrimdisi.isHidden = false }
    }

    // WhatsApp, telefon, e-posta ve uygulama dışı sayfalar sistemde açılır
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { return decisionHandler(.allow) }
        let sema = (url.scheme ?? "").lowercased()
        if ["tel", "mailto", "sms", "whatsapp", "itms-apps"].contains(sema) {
            UIApplication.shared.open(url)
            return decisionHandler(.cancel)
        }
        let host = (url.host ?? "").lowercased()
        if navigationAction.targetFrame?.isMainFrame == true && sema.hasPrefix("http")
            && (host == "wa.me" || host.hasSuffix("whatsapp.com")) {
            UIApplication.shared.open(url)
            return decisionHandler(.cancel)
        }
        decisionHandler(.allow)
    }

    // window.open: yazdırma / PDF / rapor pencereleri uygulama içinde ayrı sayfada açılır
    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url, let host = url.host?.lowercased(),
           host == "wa.me" || host.hasSuffix("whatsapp.com") {
            UIApplication.shared.open(url)
            return nil
        }
        let sayfa = AcilirSayfa(ayar: configuration)
        present(UINavigationController(rootViewController: sayfa), animated: true)
        return sayfa.web
    }

    // Sayfadaki alert / confirm / prompt
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "Tamam", style: .default) { _ in completionHandler() })
        ust().present(a, animated: true)
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "Vazgeç", style: .cancel) { _ in completionHandler(false) })
        a.addAction(UIAlertAction(title: "Tamam", style: .default) { _ in completionHandler(true) })
        ust().present(a, animated: true)
    }

    func webView(_ webView: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String, defaultText: String?,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (String?) -> Void) {
        let a = UIAlertController(title: nil, message: prompt, preferredStyle: .alert)
        a.addTextField { $0.text = defaultText }
        a.addAction(UIAlertAction(title: "Vazgeç", style: .cancel) { _ in completionHandler(nil) })
        a.addAction(UIAlertAction(title: "Tamam", style: .default) { _ in completionHandler(a.textFields?.first?.text) })
        ust().present(a, animated: true)
    }

    // Kamera / mikrofon izni sorulduğunda sistem izni yeterli (iOS 15+)
    @available(iOS 15.0, *)
    func webView(_ webView: WKWebView, requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                 initiatedByFrame frame: WKFrameInfo, type: WKMediaCaptureType,
                 decisionHandler: @escaping (WKPermissionDecision) -> Void) {
        decisionHandler(.grant)
    }

    private func ust() -> UIViewController {
        var v: UIViewController = self
        while let p = v.presentedViewController { v = p }
        return v
    }
}

// Açılır pencere (yazdır / PDF / rapor): kapat ve paylaş düğmeli
class AcilirSayfa: UIViewController, WKUIDelegate {
    let web: WKWebView

    init(ayar: WKWebViewConfiguration) {
        web = WKWebView(frame: .zero, configuration: ayar)
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError("kullanılmaz") }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .white
        web.uiDelegate = self
        web.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(web)
        NSLayoutConstraint.activate([
            web.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            web.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            web.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            web.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        ])
        navigationItem.leftBarButtonItem = UIBarButtonItem(title: "Kapat", style: .done, target: self, action: #selector(kapat))
        navigationItem.rightBarButtonItem = UIBarButtonItem(barButtonSystemItem: .action, target: self, action: #selector(paylas))
    }

    @objc private func kapat() { dismiss(animated: true) }

    // Yazdır / PDF olarak kaydet / paylaş
    @objc private func paylas() {
        let yazdir = UIPrintInteractionController.shared
        yazdir.printFormatter = web.viewPrintFormatter()
        yazdir.present(animated: true)
    }

    func webViewDidClose(_ webView: WKWebView) { dismiss(animated: true) }

    // Sayfa kendi window.print()'ini çağırırsa
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "Tamam", style: .default) { _ in completionHandler() })
        present(a, animated: true)
    }
}
