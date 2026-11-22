#!/usr/bin/env python3
"""App Store Connect mağaza kaydını API ile okur / doldurur.

Kullanım:
  magaza.py durum                 → uygulama, sürüm, yapı, yaş sınırı, inceleme bilgisi, görseller (yalnız okur)
  magaza.py doldur <metin.json>   → metinler, kategori, yaş sınırı, ücretsiz fiyat, inceleme bilgisi, yapı seçimi
  magaza.py gorsel <klasör>       → 6.9" iPhone ekran görüntülerini yükler (eskilerini siler)
  magaza.py gonder                → incelemeye gönderir
Ortam: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_PATH, BUNDLE_ID; inceleme girişi için DEMO_KOD / DEMO_PIN (sır).
Not: "App Privacy" (veri kullanımı) bölümü API'de yok; App Store Connect'ten elle doldurulur.
"""
import hashlib, json, os, sys, time, urllib.request, urllib.error
import jwt

API = 'https://api.appstoreconnect.apple.com'


def _token():
    with open(os.environ['ASC_KEY_PATH']) as f:
        key = f.read()
    now = int(time.time())
    return jwt.encode({'iss': os.environ['ASC_ISSUER_ID'], 'iat': now, 'exp': now + 1200, 'aud': 'appstoreconnect-v1'},
                      key, algorithm='ES256', headers={'kid': os.environ['ASC_KEY_ID'], 'typ': 'JWT'})


def istek(yontem, yol, govde=None, ham=None, basliklar=None, tam_url=None):
    h = {'Authorization': 'Bearer ' + _token()} if not tam_url else {}
    if govde is not None:
        h['Content-Type'] = 'application/json'
    h.update(basliklar or {})
    veri = json.dumps(govde).encode() if govde is not None else ham
    req = urllib.request.Request(tam_url or (API + yol), method=yontem, data=veri, headers=h)
    try:
        with urllib.request.urlopen(req) as r:
            b = r.read()
            return json.loads(b) if b and r.headers.get('Content-Type', '').startswith('application/json') else {}
    except urllib.error.HTTPError as e:
        e.govde = e.read().decode(errors="replace")
        print(f'API hatası {e.code} {yontem} {yol or tam_url[:60]}: {e.govde[:1500]}', file=sys.stderr)
        raise


def uygulama():
    d = istek('GET', '/v1/apps?filter[bundleId]=' + os.environ['BUNDLE_ID'])['data']
    if not d:
        raise SystemExit('Uygulama kaydı yok: ' + os.environ['BUNDLE_ID'])
    return d[0]


def surum(app_id):
    v = istek('GET', f'/v1/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=5')['data']
    duzenlenebilir = [x for x in v if x['attributes']['appStoreState'] in
                      ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED', 'REJECTED', 'METADATA_REJECTED', 'INVALID_BINARY')]
    return (duzenlenebilir or v or [None])[0]


def app_info(app_id):
    infos = istek('GET', f'/v1/apps/{app_id}/appInfos')['data']
    return [i for i in infos if i['attributes'].get('appStoreState') != 'READY_FOR_SALE'][0] if infos else None


def durum():
    a = uygulama(); aid = a['id']
    print('Uygulama:', a['attributes']['name'], '| paket:', a['attributes']['bundleId'], '| dil:', a['attributes'].get('primaryLocale'))
    v = surum(aid)
    if v:
        print('Sürüm:', v['attributes']['versionString'], '| durum:', v['attributes']['appStoreState'])
        for l in istek('GET', f"/v1/appStoreVersions/{v['id']}/appStoreVersionLocalizations")['data']:
            at = l['attributes']
            print('  Sürüm metni', at['locale'], '| açıklama:', len(at.get('description') or ''), 'karakter | anahtar:', bool(at.get('keywords')),
                  '| destek:', at.get('supportUrl'))
            for s in istek('GET', f"/v1/appStoreVersionLocalizations/{l['id']}/appScreenshotSets")['data']:
                n = len(istek('GET', f"/v1/appScreenshotSets/{s['id']}/appScreenshots")['data'])
                print('    görsel seti', s['attributes']['screenshotDisplayType'], n, 'adet')
        try:
            b = istek('GET', f"/v1/appStoreVersions/{v['id']}/build")['data']
            print('  Seçili yapı:', b and b['attributes']['version'])
        except Exception:
            print('  Seçili yapı: yok')
        try:
            r = istek('GET', f"/v1/appStoreVersions/{v['id']}/appStoreReviewDetail")['data']
            at = r['attributes'] if r else {}
            print('  İnceleme bilgisi: giriş gerekli=', at.get('demoAccountRequired'), '| kullanıcı adı dolu=', bool(at.get('demoAccountName')),
                  '| iletişim=', bool(at.get('contactEmail')))
        except Exception:
            print('  İnceleme bilgisi: yok')
    for b in istek('GET', f'/v1/builds?filter[app]={aid}&sort=-uploadedDate&limit=3')['data']:
        print('Yapı:', b['attributes']['version'], b['attributes']['processingState'], b['attributes']['uploadedDate'])
    i = app_info(aid)
    if i:
        print('App info durum:', i['attributes'].get('appStoreState'), '| yaş:', i['attributes'].get('appStoreAgeRating'))
        for l in istek('GET', f"/v1/appInfos/{i['id']}/appInfoLocalizations")['data']:
            at = l['attributes']
            print('  Bilgi', at['locale'], '| ad:', at.get('name'), '| alt başlık:', at.get('subtitle'), '| gizlilik:', at.get('privacyPolicyUrl'))
        try:
            c = istek('GET', f"/v1/appInfos/{i['id']}/primaryCategory")['data']
            print('  Kategori:', c and c['id'])
        except Exception:
            print('  Kategori: yok')
    try:
        p = istek('GET', f'/v1/apps/{aid}/appPriceSchedule')
        print('Fiyat çizelgesi:', 'var' if p.get('data') else 'yok')
    except Exception:
        print('Fiyat çizelgesi: yok')


YAS_EVET_HAYIR = {'gambling', 'unrestrictedWebAccess', 'lootBox', 'advertising', 'ageAssurance', 'healthOrWellnessTopics',
                  'messagingAndChat', 'parentalControls', 'userGeneratedContent', 'socialMedia', 'seventeenPlus'}


def _yerel(liste, locale):
    return [x for x in liste if x['attributes']['locale'] == locale]


def doldur(metin_yolu):
    m = json.load(open(metin_yolu, encoding='utf-8'))
    a = uygulama(); aid = a['id']; dil = m.get('dil', 'tr')
    v = surum(aid)
    if not v:
        v = istek('POST', '/v1/appStoreVersions', {'data': {'type': 'appStoreVersions', 'attributes': {'platform': 'IOS', 'versionString': m['surum']},
                  'relationships': {'app': {'data': {'type': 'apps', 'id': aid}}}}})['data']
    vid = v['id']
    istek('PATCH', f'/v1/appStoreVersions/{vid}', {'data': {'type': 'appStoreVersions', 'id': vid, 'attributes': {
        'copyright': m['telif'], 'releaseType': 'AFTER_APPROVAL'}}})
    # Sürüm metinleri
    for loc, t in m['metin'].items():
        ls = istek('GET', f'/v1/appStoreVersions/{vid}/appStoreVersionLocalizations')['data']
        at = {'description': t['aciklama'], 'keywords': t['anahtar'], 'supportUrl': m['destek'], 'marketingUrl': m.get('pazarlama'),
              'promotionalText': t.get('tanitim')}
        mevcut = _yerel(ls, loc)
        if mevcut:
            istek('PATCH', f"/v1/appStoreVersionLocalizations/{mevcut[0]['id']}", {'data': {'type': 'appStoreVersionLocalizations', 'id': mevcut[0]['id'], 'attributes': at}})
        else:
            at['locale'] = loc
            istek('POST', '/v1/appStoreVersionLocalizations', {'data': {'type': 'appStoreVersionLocalizations', 'attributes': at,
                  'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': vid}}}}})
        print('Sürüm metni yazıldı:', loc)
    # Uygulama bilgisi: ad, alt başlık, gizlilik adresi, kategori
    i = app_info(aid)
    for loc, t in m['metin'].items():
        ls = istek('GET', f"/v1/appInfos/{i['id']}/appInfoLocalizations")['data']
        at = {'name': t['ad'], 'subtitle': t['altbaslik'], 'privacyPolicyUrl': m['gizlilik']}
        mevcut = _yerel(ls, loc)
        if mevcut:
            istek('PATCH', f"/v1/appInfoLocalizations/{mevcut[0]['id']}", {'data': {'type': 'appInfoLocalizations', 'id': mevcut[0]['id'], 'attributes': at}})
        else:
            at['locale'] = loc
            istek('POST', '/v1/appInfoLocalizations', {'data': {'type': 'appInfoLocalizations', 'attributes': at,
                  'relationships': {'appInfo': {'data': {'type': 'appInfos', 'id': i['id']}}}}})
        print('Uygulama bilgisi yazıldı:', loc)
    istek('PATCH', f"/v1/appInfos/{i['id']}", {'data': {'type': 'appInfos', 'id': i['id'], 'relationships': {
        'primaryCategory': {'data': {'type': 'appCategories', 'id': m['kategori']}}}}})
    print('Kategori:', m['kategori'])
    # Yaş sınırı: her şey yok → 4+
    yas = istek('GET', f"/v1/appInfos/{i['id']}/ageRatingDeclaration")['data']
    print('Yaş anketi alanları:', sorted(yas['attributes'].keys()))
    yat = {}
    for k, v in yas['attributes'].items():   # boş kalan yeni sorular: evet/hayır olanlar False, derece olanlar NONE
        if v is None and k not in ('kidsAgeBand', 'ageRatingOverride', 'ageRatingOverrideV2', 'koreaAgeRatingOverride'):
            yat[k] = False if k in YAS_EVET_HAYIR else 'NONE'
    yat.update(m['yas'])
    for k in ('developerAgeRatingInfoUrl', 'gracRatingClassificationNumber'):
        yat.pop(k, None)
    for deneme in range(6):   # Apple alanların türünü hata mesajında söyler: ona göre düzeltip yeniden dene
        try:
            istek('PATCH', f"/v1/ageRatingDeclarations/{yas['id']}", {'data': {'type': 'ageRatingDeclarations', 'id': yas['id'], 'attributes': yat}})
            break
        except urllib.error.HTTPError as e:
            if e.code != 409 or deneme == 5:
                raise
            for h in json.loads(e.govde).get('errors', []):
                alan = (h.get('source') or {}).get('pointer', '').split('/')[-1]
                d = h.get('detail', '')
                if 'Expected a BOOLEAN' in d:
                    yat[alan] = False
                elif 'Expected a STRING' in d or 'not a valid' in d.lower() or 'one of' in d.lower():
                    yat[alan] = 'NONE'
                elif 'must provide a value' in d:
                    yat[alan] = False if alan in YAS_EVET_HAYIR else 'NONE'
                elif alan in yat:
                    yat.pop(alan)
    print('Yaş sınırı anketi dolduruldu')
    # Ücretsiz: temel ülke TR, fiyat noktası 0
    try:
        noktalar = istek('GET', f'/v1/apps/{aid}/appPricePoints?filter[territory]=TUR&limit=200')['data']
        sifir = [p for p in noktalar if float(p['attributes'].get('customerPrice') or 0) == 0][0]
        istek('POST', '/v1/appPriceSchedules', {'data': {'type': 'appPriceSchedules', 'relationships': {
            'app': {'data': {'type': 'apps', 'id': aid}},
            'baseTerritory': {'data': {'type': 'territories', 'id': 'TUR'}},
            'manualPrices': {'data': [{'type': 'appPrices', 'id': '${fiyat}'}]}}},
            'included': [{'type': 'appPrices', 'id': '${fiyat}', 'attributes': {'startDate': None},
                          'relationships': {'appPricePoint': {'data': {'type': 'appPricePoints', 'id': sifir['id']}}}}]})
        print('Fiyat: ücretsiz')
    except Exception as e:
        print('Fiyat ayarlanamadı (elle bakın):', e)
    # İnceleme bilgisi (demo giriş)
    r = m['inceleme']
    at = {'contactFirstName': r['ad'], 'contactLastName': r['soyad'], 'contactEmail': r['eposta'], 
          'demoAccountRequired': True, 'demoAccountName': os.environ.get('DEMO_KOD', 'demo'),
          'notes': r['not']}
    if os.environ.get('DEMO_PIN'):   # boşsa App Store Connect'te elle girilen şifreye dokunma
        at['demoAccountPassword'] = os.environ['DEMO_PIN']
    if r.get('telefon'):
        at['contactPhone'] = r['telefon']
    try:
        rd = istek('GET', f'/v1/appStoreVersions/{vid}/appStoreReviewDetail')['data']
    except Exception:
        rd = None
    if rd:
        istek('PATCH', f"/v1/appStoreReviewDetails/{rd['id']}", {'data': {'type': 'appStoreReviewDetails', 'id': rd['id'], 'attributes': at}})
    else:
        istek('POST', '/v1/appStoreReviewDetails', {'data': {'type': 'appStoreReviewDetails', 'attributes': at,
              'relationships': {'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': vid}}}}})
    print('İnceleme bilgisi yazıldı')
    # Son işlenmiş yapıyı seç
    bs = istek('GET', f'/v1/builds?filter[app]={aid}&filter[processingState]=VALID&sort=-uploadedDate&limit=1')['data']
    if bs:
        b = bs[0]
        if b['attributes'].get('usesNonExemptEncryption') is None:
            istek('PATCH', f"/v1/builds/{b['id']}", {'data': {'type': 'builds', 'id': b['id'], 'attributes': {'usesNonExemptEncryption': False}}})
        istek('PATCH', f'/v1/appStoreVersions/{vid}/relationships/build', {'data': {'type': 'builds', 'id': b['id']}})
        print('Yapı seçildi:', b['attributes']['version'])
    else:
        print('İşlenmiş yapı yok')


def gorsel(klasor):
    a = uygulama(); v = surum(a['id'])
    ls = istek('GET', f"/v1/appStoreVersions/{v['id']}/appStoreVersionLocalizations")['data']
    for l in ls:
        setler = istek('GET', f"/v1/appStoreVersionLocalizations/{l['id']}/appScreenshotSets")['data']
        tip = 'APP_IPHONE_67'
        s = [x for x in setler if x['attributes']['screenshotDisplayType'] == tip]
        if s:
            for g in istek('GET', f"/v1/appScreenshotSets/{s[0]['id']}/appScreenshots")['data']:
                istek('DELETE', f"/v1/appScreenshots/{g['id']}")
            sid = s[0]['id']
        else:
            sid = istek('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': tip},
                        'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': l['id']}}}}})['data']['id']
        for ad in sorted(f for f in os.listdir(klasor) if f.endswith('.png')):
            yol = os.path.join(klasor, ad); veri = open(yol, 'rb').read()
            g = istek('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': ad, 'fileSize': len(veri)},
                      'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': sid}}}}})['data']
            for op in g['attributes']['uploadOperations']:
                parca = veri[op['offset']:op['offset'] + op['length']]
                istek(op['method'], None, ham=parca, basliklar={h['name']: h['value'] for h in op['requestHeaders']}, tam_url=op['url'])
            istek('PATCH', f"/v1/appScreenshots/{g['id']}", {'data': {'type': 'appScreenshots', 'id': g['id'], 'attributes': {
                'uploaded': True, 'sourceFileChecksum': hashlib.md5(veri).hexdigest()}}})
            print('Görsel yüklendi:', l['attributes']['locale'], ad)


def iptal():
    a = uygulama()
    for durum in ('WAITING_FOR_REVIEW', 'IN_REVIEW', 'UNRESOLVED_ISSUES'):
        for s in istek('GET', f"/v1/reviewSubmissions?filter[app]={a['id']}&filter[state]={durum}&filter[platform]=IOS")['data']:
            istek('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'canceled': True}}})
            print('Gönderim geri çekildi:', durum)


def gonder():
    a = uygulama(); v = surum(a['id'])
    istek('PATCH', f"/v1/apps/{a['id']}", {'data': {'type': 'apps', 'id': a['id'], 'attributes': {
        'contentRightsDeclaration': 'DOES_NOT_USE_THIRD_PARTY_CONTENT'}}})
    print('İçerik hakları beyanı: üçüncü taraf içerik yok')
    acik = istek('GET', f"/v1/reviewSubmissions?filter[app]={a['id']}&filter[state]=READY_FOR_REVIEW&filter[platform]=IOS")['data']
    s = acik[0] if acik else istek('POST', '/v1/reviewSubmissions', {'data': {'type': 'reviewSubmissions', 'attributes': {'platform': 'IOS'},
              'relationships': {'app': {'data': {'type': 'apps', 'id': a['id']}}}}})['data']
    mevcut = istek('GET', f"/v1/reviewSubmissions/{s['id']}/items")['data']
    if mevcut:
        istek('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'submitted': True}}})
        print('İncelemeye gönderildi')
        return
    istek('POST', '/v1/reviewSubmissionItems', {'data': {'type': 'reviewSubmissionItems', 'relationships': {
        'reviewSubmission': {'data': {'type': 'reviewSubmissions', 'id': s['id']}},
        'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': v['id']}}}}})
    istek('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'submitted': True}}})
    print('İncelemeye gönderildi')


if __name__ == '__main__':
    k = sys.argv[1]
    if k == 'durum':
        durum()
    elif k == 'doldur':
        doldur(sys.argv[2])
    elif k == 'gorsel':
        gorsel(sys.argv[2])
    elif k == 'gonder':
        gonder()
    elif k == 'iptal':
        iptal()
    elif k == 'adduzelt':   # gönderimi geri çek, metinleri yaz, yeniden gönder
        iptal()
        for _ in range(30):
            v = surum(uygulama()['id'])
            if v['attributes']['appStoreState'] in ('DEVELOPER_REJECTED', 'PREPARE_FOR_SUBMISSION'):
                break
            time.sleep(10)
        doldur(sys.argv[2])
        gonder()
