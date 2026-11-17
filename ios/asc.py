#!/usr/bin/env python3
"""App Store Connect API ile geçici dağıtım sertifikası + App Store profili oluşturur / siler.

Neden: sertifika adında 'ç' olduğu için Xcode'un ürettiği imza şartı (ada göre) Apple doğrulamasından
geçmiyor (NFD/NFC farkı). İmzayı kendimiz, Team ID'ye göre şartla atıyoruz; bunun için yerel bir
dağıtım sertifikası gerekiyor. Sertifika her derlemede oluşturulup iş bitince iptal edilir.

Kullanım:
  asc.py hazirla <csr.pem> <cikti_klasoru>   → sertifika.cer, profil.mobileprovision, kimlikler.json
  asc.py temizle <cikti_klasoru>             → profili siler, sertifikayı iptal eder
Ortam: ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_PATH, BUNDLE_ID
"""
import base64, json, os, sys, time, urllib.request, urllib.error
import jwt  # PyJWT

API = 'https://api.appstoreconnect.apple.com/v1'


def _token():
    with open(os.environ['ASC_KEY_PATH']) as f:
        key = f.read()
    now = int(time.time())
    return jwt.encode({'iss': os.environ['ASC_ISSUER_ID'], 'iat': now, 'exp': now + 1200, 'aud': 'appstoreconnect-v1'},
                      key, algorithm='ES256', headers={'kid': os.environ['ASC_KEY_ID'], 'typ': 'JWT'})


def _istek(yontem, yol, govde=None):
    req = urllib.request.Request(API + yol, method=yontem,
                                 data=json.dumps(govde).encode() if govde is not None else None,
                                 headers={'Authorization': 'Bearer ' + _token(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            b = r.read()
            return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        hata = e.read().decode(errors='replace')
        print(f'API hatası {e.code} {yontem} {yol}: {hata[:800]}', file=sys.stderr)
        raise


def hazirla(csr_yolu, klasor):
    os.makedirs(klasor, exist_ok=True)
    with open(csr_yolu) as f:
        csr = ''.join(l.strip() for l in f if '-----' not in l)
    sert = _istek('POST', '/certificates', {'data': {'type': 'certificates',
                                                     'attributes': {'certificateType': 'DISTRIBUTION', 'csrContent': csr}}})['data']
    with open(os.path.join(klasor, 'sertifika.cer'), 'wb') as f:
        f.write(base64.b64decode(sert['attributes']['certificateContent']))
    bundle = os.environ['BUNDLE_ID']
    bl = _istek('GET', '/bundleIds?filter[identifier]=' + bundle + '&filter[platform]=IOS')['data']
    bl = [b for b in bl if b['attributes']['identifier'] == bundle]
    if not bl:
        raise SystemExit('Paket kimliği bulunamadı: ' + bundle)
    ad = 'fincosto CI ' + time.strftime('%Y%m%d%H%M%S')
    prof = _istek('POST', '/profiles', {'data': {'type': 'profiles', 'attributes': {'name': ad, 'profileType': 'IOS_APP_STORE'},
                                                'relationships': {
                                                    'bundleId': {'data': {'type': 'bundleIds', 'id': bl[0]['id']}},
                                                    'certificates': {'data': [{'type': 'certificates', 'id': sert['id']}]}}}})['data']
    with open(os.path.join(klasor, 'profil.mobileprovision'), 'wb') as f:
        f.write(base64.b64decode(prof['attributes']['profileContent']))
    with open(os.path.join(klasor, 'kimlikler.json'), 'w') as f:
        json.dump({'sertifika': sert['id'], 'profil': prof['id'], 'profilAdi': ad, 'profilUuid': prof['attributes']['uuid']}, f)
    print('Geçici sertifika ve profil hazır:', ad)


def temizle(klasor):
    yol = os.path.join(klasor, 'kimlikler.json')
    if not os.path.exists(yol):
        return
    k = json.load(open(yol))
    for tur, kimlik in (('profiles', k.get('profil')), ('certificates', k.get('sertifika'))):
        if not kimlik:
            continue
        try:
            _istek('DELETE', f'/{tur}/{kimlik}')
            print('Silindi:', tur)
        except Exception:
            print('Silinemedi:', tur)


if __name__ == '__main__':
    if sys.argv[1] == 'hazirla':
        hazirla(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'temizle':
        temizle(sys.argv[2])
