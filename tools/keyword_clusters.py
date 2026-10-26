"""Classes that look environment- or fixture-dependent, with their method counts and baseline hits (to choose cfg GROUPS).
Usage: python3 -I keyword_clusters.py <App>"""
import csv, collections, re, sys
rows = list(csv.DictReader(open('graphs/%s/out/methods.csv' % sys.argv[1])))
KW = {
 'network': r'(http|url|download|upload|sync|cloud|dropbox|oauth|ftp|smb|sftp|webdav|network|socket|retrofit|okhttp|request|fetch|torrent|tracker|feed|rss|peer)',
 'account': r'(login|auth|token|account|credential|password|passcode|biometric|fingerprint|keystore|crypt)',
 'hardware': r'(camera|record|audio|bluetooth|nfc|gps|location|sensor|vibrat|flash|torch|tts|speech|voice|microphone|scanner|qr|barcode)',
 'files': r'(import|export|backup|restore|zip|archive|csv|json|xml|qif|ofx|pdf|storage|document|media|folder)',
 'system': r'(notification|widget|shortcut|alarm|boot|receiver|service|job|scheduler|worker|provider)',
}
cls = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in rows:
    c = r['method'].split('(')[0].rsplit('.', 1)[0]
    top = c.split('$')[0]
    h = r['monkey_hit'] == '1' or r['ape_hit'] == '1'
    d = cls[top]
    d[0] += 1; d[1] += 1 if h else 0; d[2] += 1 if r['verdict'] == 'DEAD' else 0
for k, rx in KW.items():
    print('== %s' % k)
    out = []
    for c, (n, h, dd, _x) in sorted(cls.items()):
        if re.search(rx, c, re.I) and n - h - dd > 0:
            out.append('%s %d/%d/%d' % (c, n - h - dd, h, dd))
    print('  (unhit-alive / hit / dead):', '; '.join(out[:60]))
