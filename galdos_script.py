import urllib.request, re, json
req = urllib.request.Request('https://teatroperezgaldos.es/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req).read().decode('utf-8')
    urls = re.findall(r'href=[\"\']([^\"\']+)[\"\']', res)
    for u in set(urls):
        if 'salvaje' in u or 'friolera' in u:
            print(u)
except Exception as e:
    print(e)
