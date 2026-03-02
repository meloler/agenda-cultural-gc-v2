import urllib.request
req = urllib.request.Request('https://teatroperezgaldos.es/es/sitemap.xml', headers={'User-Agent': 'Mozilla/5.0'})
try:
    sitemap = urllib.request.urlopen(req).read().decode('utf-8')
    print(sitemap[:500])
except Exception as e:
    req = urllib.request.Request('https://teatroperezgaldos.es/sitemap.xml', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        sitemap = urllib.request.urlopen(req).read().decode('utf-8')
        print(sitemap[:500])
    except Exception as e2:
        print("Sitemap not found", e2)
