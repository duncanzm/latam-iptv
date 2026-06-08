#!/usr/bin/env python3
import urllib.request, re, ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={"User-Agent":"Lavf/60.3.100"}
def fetch(u,t=40):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=ctx).read().decode("utf-8","replace")
    except Exception as e: print("  !",u[:45],e); return ""

def fixmoji(s):  # arregla tildes dobles-codificadas
    try:
        if "Ã" in s or "ð" in s or "Â" in s: return s.encode("latin-1","ignore").decode("utf-8","ignore") or s
    except: pass
    return s
def realname(line):  # nombre = despues de la ULTIMA coma; sin logo base64
    return fixmoji(line.rsplit(",",1)[-1].strip())
def lastgroup(line):
    m=re.findall(r'group-title="([^"]*)"',line); return m[-1] if m else ""

out=[]
PAISES={"cr":"Costa Rica","mx":"México","ar":"Argentina","co":"Colombia","cl":"Chile","pe":"Perú","ec":"Ecuador","ve":"Venezuela","es":"España","us":"USA"}
for cc,pais in PAISES.items():
    L=fetch(f"https://raw.githubusercontent.com/Romaxa55/world_ip_tv/master/output/{cc}.m3u").splitlines()
    for i,l in enumerate(L):
        if l.startswith("#EXTINF") and i+1<len(L) and L[i+1].startswith("http"):
            nm=re.sub(r"\s*\(\d+p\).*$","",realname(l)).replace("[Geo-blocked]","").replace("[Not 24/7]","").strip()
            out.append((0,f"Canales de {pais}",nm,L[i+1].strip()))

CO={"españa":"Canales de España","espana":"Canales de España","costa rica":"Canales de Costa Rica","mexico":"Canales de México","méxico":"Canales de México","peru":"Canales de Perú","perú":"Canales de Perú","colombia":"Canales de Colombia","argentina":"Canales de Argentina","chile":"Canales de Chile","ecuador":"Canales de Ecuador","venezuela":"Canales de Venezuela"}
def cat(g,n):
    s=(g+" "+n).lower()
    if any(k in s for k in ["adult","xxx","porn"]): return None
    if any(k in s for k in ["portugal","brasil","brazil","italia","alema","francia","france","russia","рос","arab","عربية","türk","turk"]): return None
    for k,v in CO.items():
        if k in g.lower(): return v
    if any(k in s for k in ["espn","deporte","sport","futbol","fútbol"," gol","liga","nba","ufc","wwe","tenis","eventos","dazn","tudn","futv","td+","claro sports","win sports"]): return "Deportes"
    if "24/7" in s or "24-7" in s: return "24/7"
    if any(k in s for k in ["infantil","kids","disney","cartoon","nick","junior","boomerang"," inf "]): return "Infantil"
    if any(k in s for k in ["noticias"," news","cnn","telemundo","noti "]): return "Noticias"
    if any(k in s for k in ["music","música","mtv"," htv","trace"]): return "Música"
    if any(k in s for k in ["cristian","religi","enlace","ewtn","tbn","iglesia"]): return "Cristianos"
    if any(k in s for k in ["serie","novela","warner","sony","comedy","universal tv"]): return "Series"
    if any(k in s for k in ["cine","pelicul","movie","hbo","golden","star channel","cinemax","cinecanal","space","paramount"," amc","studio","ondeman","satelite"]): return "Películas"
    return "Variados"
def clean(n):
    n=re.sub(r"^\s*[A-Za-z0-9\-]{1,6}\s*[\|:]\s*","",n)   # quita "ARG |", "ES:", "2M |", "D-ESP |"
    n=re.sub(r"\b(FHD|UHD|SD|HD|4K\+?)\b","",n)
    n=re.sub(r"[\*#]\w*|⭐️?|\(KO\)|\.\.+|\bNORTE\b|\bSUR\b|\bEdge\b","",n)
    return re.sub(r"\s{2,}"," ",n).strip(" *|-:")
ORD={"Deportes":1,"Películas":2,"Series":3,"24/7":4,"Infantil":5,"Noticias":6,"Música":7,"Cristianos":8,"Variados":9}
pt=fetch("http://galileatv.top:8080/get.php?username=deco-20&password=VumqaPUzpX&type=m3u_plus&output=ts").splitlines()
for i,l in enumerate(pt):
    if l.startswith("#EXTINF") and i+1<len(pt) and pt[i+1].startswith("http"):
        c=cat(lastgroup(l),realname(l))
        if not c: continue
        nm=clean(realname(l))
        if nm and len(nm)<60: out.append((0 if c.startswith("Canales") else ORD[c],c,nm,pt[i+1].strip()))

out.sort(key=lambda x:(x[0], x[1], x[2].lower()))
seen=set(); f=open("latam.m3u","w"); f.write("#EXTM3U\n")
for o,g,n,u in out:
    if (g,n) in seen: continue
    seen.add((g,n)); f.write(f'#EXTINF:-1 group-title="{g}",{n}\n{u}\n')
f.close(); print("TOTAL:",len(seen))
