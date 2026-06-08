#!/usr/bin/env python3
import urllib.request, re, ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={"User-Agent":"Lavf/60.3.100"}
def fetch(u,t=40):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=ctx).read().decode("utf-8","replace")
    except Exception as e: print("  !",u[:45],e); return ""

PAISES={"cr":"Costa Rica","mx":"México","ar":"Argentina","co":"Colombia","cl":"Chile","pe":"Perú","ec":"Ecuador","ve":"Venezuela","es":"España","us":"USA"}
out=[]  # (orden, grupo, nombre, url)

# NACIONALES
for cc,pais in PAISES.items():
    L=fetch(f"https://raw.githubusercontent.com/Romaxa55/world_ip_tv/master/output/{cc}.m3u").splitlines()
    for i,l in enumerate(L):
        if l.startswith("#EXTINF") and i+1<len(L) and L[i+1].startswith("http"):
            nm=re.sub(r"\s*\(\d+p\).*$","",l.split(",",1)[-1]).replace("[Geo-blocked]","").replace("[Not 24/7]","").strip()
            out.append((1,f"Canales de {pais}",nm,L[i+1].strip()))

# PREMIUM por grupo original -> categoria
CO={"españa":"Canales de España","espana":"Canales de España","costa rica":"Canales de Costa Rica",
    "mexico":"Canales de México","méxico":"Canales de México","peru":"Canales de Perú","perú":"Canales de Perú",
    "colombia":"Canales de Colombia","argentina":"Canales de Argentina","chile":"Canales de Chile",
    "ecuador":"Canales de Ecuador","venezuela":"Canales de Venezuela"}
def cat(g,n):
    s=(g+" "+n).lower()
    if any(k in s for k in ["adult","xxx","porn"]) : return None
    if any(k in s for k in ["portugal","francia","france","brasil","brazil","italia","alema"]): return None
    for k,v in CO.items():
        if k in g.lower(): return v
    if any(k in s for k in ["espn","deporte","sport","futbol","fútbol"," gol","liga","nba","ufc","wwe","tenis","eventos","dazn","tudn","futv","td+"]): return "Deportes"
    if "24/7" in s or "24-7" in s: return "24/7"
    if any(k in s for k in ["infantil","kids","disney","cartoon","nick","junior","boomerang"]): return "Infantil"
    if any(k in s for k in ["noticias"," news","cnn","telemundo"]): return "Noticias"
    if any(k in s for k in ["music","música","mtv"]): return "Música"
    if any(k in s for k in ["cristian","religi","enlace","ewtn"]): return "Cristianos"
    if any(k in s for k in ["serie","novela","warner","sony","comedy"]): return "Series"
    if any(k in s for k in ["cine","pelicul","movie","hbo","golden","star channel","cinemax","cinecanal","space","paramount"," amc","studio universal","ondeman","satelite"]): return "Películas"
    if "latino" in s: return "Variados Latino"
    return "Variados"
def clean(n):
    n=re.sub(r"^\s*(2M|SD|HD|FHD|UHD|CINE US|CINE|DEP|CR|MX|AR|CO|CL|PE|EC|VE|ES|US|BR|COL|PERU)\s*\|\s*","",n,flags=re.I)
    n=re.sub(r"\b(FHD|UHD|SD|HD)\b","",n); n=re.sub(r"[\*#]CB|⭐️?|\bNORTE\b|\bSUR\b|\bEdge\b","",n)
    return re.sub(r"\s{2,}"," ",n).strip(" *|-")
ORD={"Deportes":2,"Películas":3,"Series":4,"24/7":5,"Infantil":6,"Noticias":7,"Música":8,"Cristianos":9,"Variados Latino":10,"Variados":11}
pt=fetch("http://galileatv.top:8080/get.php?username=deco-20&password=VumqaPUzpX&type=m3u_plus&output=ts").splitlines()
for i,l in enumerate(pt):
    if l.startswith("#EXTINF") and i+1<len(pt) and pt[i+1].startswith("http"):
        g=re.search(r'group-title="([^"]*)"',l); g=g.group(1) if g else ""
        c=cat(g,l.split(",",1)[-1])
        if not c: continue
        nm=clean(l.split(",",1)[-1].strip())
        if nm: out.append((ORD.get(c,1) if c.startswith("Canales") else ORD.get(c,11),c,nm,pt[i+1].strip()))

out.sort(key=lambda x:(0 if x[1].startswith("Canales") else x[0], x[1], x[2].lower()))
with open("latam.m3u","w") as f:
    f.write("#EXTM3U\n")
    for o,g,n,u in out: f.write(f'#EXTINF:-1 group-title="{g}",{n}\n{u}\n')
print("TOTAL:",len(out))
