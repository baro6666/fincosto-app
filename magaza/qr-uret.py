#!/usr/bin/env python3
"""İndirme QR kodu + basılabilir afiş üretir.

Kullanım:  python3 magaza/qr-uret.py            → genel (app.fincosto.com/indir)
           python3 magaza/qr-uret.py hamour     → firmaya özel (açılınca firma kodu hazır gelir)
Çıktı: magaza/qr/fincosto-indir[-firma]-qr.svg / .png ve -afis.png / .pdf
Gerekenler: pip install segno; afiş için Playwright (Chromium).
"""
import os, re, sys, subprocess, json
import segno

KOK = os.path.dirname(os.path.abspath(__file__))
firma = re.sub(r'[^a-z0-9_]', '', (sys.argv[1] if len(sys.argv) > 1 else '').lower())
url = 'https://app.fincosto.com/indir' + ('?f=' + firma if firma else '')
ad = 'fincosto-indir' + ('-' + firma if firma else '')
os.makedirs(os.path.join(KOK, 'qr'), exist_ok=True)

LACIVERT = '#13254A'
logo = re.search(r'`(.*)`', open(os.path.join(KOK, 'logo-svg.js'), encoding='utf-8').read(), re.S).group(1)

qr = segno.make(url, error='h', boost_error=False)
n = qr.symbol_size(border=2)[0]          # modül cinsinden kenar (kenar boşluğu dahil)
koyu = []
for y, satir in enumerate(qr.matrix_iter(border=2)):
    for x, v in enumerate(satir):
        if v:
            koyu.append(f'M{x} {y}h1v1h-1z')
# Ortadaki logo: alanın ~%22'si (H düzeyi %30 onarım payı bırakır)
L = round(n * 0.22, 2); bosluk = round(L * 0.14, 2)
lx = (n - L) / 2
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">
<rect width="{n}" height="{n}" fill="#fff"/>
<path fill="{LACIVERT}" d="{''.join(koyu)}"/>
<rect x="{lx - bosluk}" y="{lx - bosluk}" width="{L + 2 * bosluk}" height="{L + 2 * bosluk}" rx="{bosluk * 1.6}" fill="#fff"/>
<svg x="{lx}" y="{lx}" width="{L}" height="{L}" viewBox="0 0 512 512" shape-rendering="geometricPrecision"><clipPath id="k"><rect width="512" height="512" rx="110"/></clipPath><g clip-path="url(#k)">{logo}</g></svg>
</svg>'''
svg_yol = os.path.join(KOK, 'qr', ad + '-qr.svg')
open(svg_yol, 'w', encoding='utf-8').write(svg)

# PNG + afiş: Chromium ile çizilir
alt = ('Firma: <b>' + firma + '</b>') if firma else 'Firma kodunuzu ve PIN\'inizi yöneticinizden alın'
afis = f'''<!doctype html><meta charset="utf-8"><style>
@page {{ size: A5; margin: 0 }}
body {{ margin: 0; font-family: "Open Sans","Segoe UI",system-ui,sans-serif; }}
.a {{ width: 148mm; height: 210mm; box-sizing: border-box; background: {LACIVERT}; color: #F3F5F9; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 7mm; padding: 14mm; text-align: center; }}
.m {{ font-size: 15mm; font-weight: 700; letter-spacing: -.4mm; margin: 0 }} .m span {{ color: #C9A24A }}
.s {{ font-size: 5mm; color: #A9B3C6; margin: -4mm 0 0 }}
.q {{ background: #fff; border-radius: 6mm; padding: 5mm; width: 88mm; box-shadow: 0 2mm 6mm rgba(0,0,0,.3) }} .q svg {{ display: block; width: 100%; height: auto }}
.b {{ font-size: 7mm; font-weight: 700; margin: 0 }} .b span {{ color: #C9A24A }}
.t {{ font-size: 4.2mm; color: #A9B3C6; line-height: 1.5; margin: 0 }} .t b {{ color: #F3F5F9 }}
.u {{ font-size: 3.6mm; color: #7F8BA3; letter-spacing: .2mm }}
</style><div class="a"><p class="m">fin<span>costo</span></p><p class="s">Şube kasa, personel ve maliyet takibi</p>
<div class="q">{svg}</div><p class="b">Uygulamayı <span>indirin</span></p>
<p class="t">Telefonunuzun kamerasını QR koda tutun,<br>çıkan bağlantıya dokunun.<br>{alt}</p>
<div class="u">{url.replace('https://', '')}</div></div>'''
afis_yol = os.path.join(KOK, 'qr', ad + '-afis.html')
open(afis_yol, 'w', encoding='utf-8').write(afis)
js = '''const {chromium}=require('playwright');(async()=>{const [svg,afis,png,apng,pdf]=process.argv.slice(1);const b=await chromium.launch();
let p=await b.newPage({viewport:{width:1200,height:1200}});await p.setContent('<body style="margin:0">'+require('fs').readFileSync(svg,'utf8').replace('<svg ','<svg width="1200" height="1200" '));await p.screenshot({path:png});
p=await b.newPage({viewport:{width:560,height:794},deviceScaleFactor:3});await p.goto('file://'+afis);await p.screenshot({path:apng,fullPage:true});await p.pdf({path:pdf,format:'A5',printBackground:true});await b.close();})();'''
q = os.path.join(KOK, 'qr', ad)
subprocess.run(['node', '-e', js, svg_yol, afis_yol, q + '-qr.png', q + '-afis.png', q + '-afis.pdf'], check=True,
               env=dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()))
os.remove(afis_yol)
print('QR:', url, '→', q + '-qr.svg/.png,', q + '-afis.png/.pdf')
