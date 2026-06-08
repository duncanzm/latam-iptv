#!/usr/bin/env python3
# Combina canales NACIONALES (world_ip_tv, auto-verificados) + PREMIUM (servidor Xtream)
# Limpia nombres y organiza por grupos. Salida: latam.m3u
import urllib.request, re, ssl

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {"User-Agent":"Lavf/60.3.100"}
def fetch(url, t=30):
    try:
        return urllib.request.urlopen(urllib.request.Request(url,headers=UA), timeout=t, context=ctx).read().decode("utf-8","replace")
    except Exception as e:
        print("  ! falla", url[:50], e); return ""

# --- 1) NACIONALES (world_ip_tv por pais) ---
PAISES = {"cr":"Costa Rica","mx":"Mexico","ar":"Argentina","co":"Colombia","cl":"Chile",
          "pe":"Peru","ec":"Ecuador","ve":"Venezuela","es":"Espana","us":"USA"}
entries=[]  # (group, name, url)
for cc,pais in PAISES.items():
    txt = fetch(f"https://raw.githubusercontent.com/Romaxa55/world_ip_tv/master/output/{cc}.m3u")
    lines = txt.splitlines()
    for i,l in enumerate(lines):
        if l.startswith("#EXTINF") and i+1<len(lines) and lines[i+1].startswith("http"):
            name = l.split(",",1)[-1].strip()
            name = re.sub(r"\s*\(\d+p\).*$","",name).replace("[Geo-blocked]","").replace("[Not 24/7]","").strip()
            entries.append((f"NACIONAL {pais}", name, lines[i+1].strip()))
print(f"Nacionales: {len(entries)}")

# --- 2) PREMIUM (Xtream get.php) ---
PREM = "http://galileatv.top:8080/get.php?username=deco-20&password=VumqaPUzpX&type=m3u_plus&output=ts"
# grupos del server que SI queremos (premium / utiles)
KEEP = ["ESPN","PREMIUM","DEPORTES","EVENTOS","CINE","TELEMUNDO","PELICUL","24/7 LATINO"]
ptxt = fetch(PREM).splitlines()
def clean(n):
    n = re.sub(r"^\s*(2M|SD|HD|FHD|UHD|CINE US|CINE|DEP|CR|MX|AR|CO|CL|PE|EC|VE|ES|US|BR|COL|PERU)\s*\|\s*","",n,flags=re.I)
    n = re.sub(r"\b(FHD|UHD|SD|HD)\b","",n)
    n = re.sub(r"[\*#]CB|⭐️?|\bNORTE\b|\bSUR\b|\bEdge\b","",n)
    n = re.sub(r"\s{2,}"," ",n).strip(" *|-")
    return n
prem=0
for i,l in enumerate(ptxt):
    if l.startswith("#EXTINF") and i+1<len(ptxt) and ptxt[i+1].startswith("http"):
        g = re.search(r'group-title="([^"]*)"',l); g=g.group(1) if g else ""
        if not any(k.lower() in g.lower() for k in KEEP): continue
        name = clean(l.split(",",1)[-1].strip())
        if not name: continue
        grp = "PREMIUM "+re.sub(r"PREMIUM ","",g,flags=re.I).strip().title()
        entries.append((grp, name, ptxt[i+1].strip())); prem+=1
print(f"Premium: {prem}")

# --- 3) escribir m3u ordenado por grupo ---
entries.sort(key=lambda e:(e[0], e[1].lower()))
with open("latam.m3u","w") as f:
    f.write("#EXTM3U\n")
    for g,n,u in entries:
        f.write(f'#EXTINF:-1 group-title="{g}",{n}\n{u}\n')
print(f"TOTAL: {len(entries)} canales")
