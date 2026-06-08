#!/usr/bin/env python3
import urllib.request, re, ssl, gzip, unicodedata
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={"User-Agent":"Lavf/60.3.100"}
def fetch(u,t=40):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=ctx).read().decode("utf-8","replace")
    except Exception as e: print("  !",u[:45],e); return ""
def fixmoji(s):
    try:
        if any(c in s for c in "ÃðÂ"): return s.encode("latin-1","ignore").decode("utf-8","ignore") or s
    except: pass
    return s
def realname(line): return fixmoji(line.rsplit(",",1)[-1].strip())
def lastgroup(line):
    m=re.findall(r'group-title="([^"]*)"',line); return m[-1] if m else ""
def tvgid(line):
    m=re.search(r'tvg-id="([^"]*)"',line); return m.group(1) if m else ""
def tvglogo(line):
    m=re.search(r'tvg-logo="([^"]*)"',line); v=m.group(1) if m else ""
    return v if v.startswith("http") else ""


ACR={"TV","HD","FHD","UHD","4K","ESPN","HBO","TNT","FX","AXN","CNN","USA","CR","MX","AR","UK","NBA","NFL","MLB","UFC","WWE","MTV","HTV","TUDN","DAZN","PBS","CW","AMC","ID","A&E","FOX","NBC","CBS","ABC","RT","DW","BBC","TYC","KMK","RCN","UCR","OPA","GEX","VM","SOY","DIRECTV","PPV","RFTV","TD","FUTV","CDF","GOL","TVE","RTVE","ATV","DGO","GP","F1"}
CONN={"de","la","el","los","las","del","y","e","o","a","en","the","of","and","por","para","con","vs"}
def norm(n):
    n=re.sub(r"\s{2,}"," ",n).strip().lstrip("+ ").strip()
    out=[]
    for idx,w in enumerate(n.split(" ")):
        wu=re.sub(r"[^A-Za-z0-9&]","",w).upper(); wl=wu.lower()
        if not wu: continue
        if wl in CONN and idx>0: out.append(wl)
        elif wu in ACR: out.append(wu)
        elif re.match(r"^[0-9]",w): out.append(w)
        elif w.isupper() and 2<=len(wu)<=5 and sum(c in "AEIOU" for c in wu)<=1: out.append(wu)
        else: out.append(w.capitalize())
    return " ".join(out).strip()
def dkey(n):
    k=n.lower()
    k=re.sub(r"\b(cr|mx|ar|hd|fhd|uhd|sd|4k|este|oeste|norte|sur|latino|plus|tv|canal)\b","",k)
    return re.sub(r"[^a-z0-9]","",k)
def strip_q(n):  # quita (720p), [not 24/7], [geo-blocked] sin importar mayus
    n=re.sub(r"\s*\(\d+p\)","",n); n=re.sub(r"\s*\[[^\]]*\]","",n,flags=re.I)
    return n.strip()

out=[]
PAISES={"cr":"Costa Rica","mx":"México","ar":"Argentina","co":"Colombia","cl":"Chile","pe":"Perú","ec":"Ecuador","ve":"Venezuela","es":"España","us":"USA"}
for cc,pais in PAISES.items():
    L=fetch(f"https://raw.githubusercontent.com/Romaxa55/world_ip_tv/master/output/{cc}.m3u").splitlines()
    for i,l in enumerate(L):
        if l.startswith("#EXTINF") and i+1<len(L) and L[i+1].startswith("http"):
            out.append((0,f"Canales de {pais}",norm(strip_q(realname(l))),L[i+1].strip(),tvgid(l),tvglogo(l)))

CO={"españa":"Canales de España","espana":"Canales de España","costa rica":"Canales de Costa Rica","mexico":"Canales de México","méxico":"Canales de México","peru":"Canales de Perú","perú":"Canales de Perú","colombia":"Canales de Colombia","argentina":"Canales de Argentina","chile":"Canales de Chile","ecuador":"Canales de Ecuador","venezuela":"Canales de Venezuela"}
def cat(g,n):
    s=(g+" "+n).lower()
    if any(k in s for k in ["adult","xxx","porn"]): return None
    if any(k in s for k in ["portugal","brasil","brazil","italia","alema","francia","france","russia","рос","arab","türk","turk"]): return None
    if "evento" in g.lower() or re.match(r"^\s*\d{1,2}\s*[-:]",n): return "Eventos"
    for k,v in CO.items():
        if k in g.lower(): return v
    if any(k in s for k in ["espn","deporte","sport","futbol","fútbol"," gol","liga","nba","ufc","wwe","tenis","dazn","tudn","futv","td+","claro sports","win sports","directv sport"]): return "Deportes"
    if "24/7" in s or "24-7" in s: return "24/7"
    if any(k in s for k in ["infantil","kids","disney","cartoon","nick","junior","boomerang"]): return "Infantil"
    if any(k in s for k in ["noticias"," news","cnn","telemundo"]): return "Noticias"
    if any(k in s for k in ["music","música","mtv"," htv","trace"]): return "Música"
    if any(k in s for k in ["cristian","religi","enlace","ewtn","tbn","iglesia"]): return "Cristianos"
    if any(k in s for k in ["serie","novela","warner","sony","comedy","universal tv"]): return "Series"
    if any(k in s for k in ["cine","pelicul","movie","hbo","golden","star channel","cinemax","cinecanal","space","paramount"," amc","studio","ondeman","satelite"]): return "Películas"
    return "Variados"
def clean(n):
    n=re.sub(r"^\s*\d{1,2}\s*[-:]\s*","",n)  # quita hora "00 - "
    n=re.sub(r"^\s*[A-Za-z0-9\-]{1,6}\s*[\|:]\s*","",n)
    n=re.sub(r"\b(FHD|UHD|SD|HD|4K\+?)\b","",n)
    n=re.sub(r"[\*#]\w*|⭐️?|\(KO\)|\.\.+|\bEdge\b","",n)
    return re.sub(r"\s{2,}"," ",strip_q(n)).strip(" *|-:")
ORD={"Deportes":1,"Eventos":2,"Películas":3,"Series":4,"24/7":5,"Infantil":6,"Noticias":7,"Música":8,"Cristianos":9,"Variados":10}
pt=fetch("http://galileatv.top:8080/get.php?username=deco-20&password=VumqaPUzpX&type=m3u_plus&output=ts").splitlines()
for i,l in enumerate(pt):
    if l.startswith("#EXTINF") and i+1<len(pt) and pt[i+1].startswith("http"):
        c=cat(lastgroup(l),realname(l))
        if not c: continue
        nm=norm(clean(realname(l)))
        if nm and 2<=len(nm)<55: out.append((0 if c.startswith("Canales") else ORD[c],c,nm,pt[i+1].strip(),tvgid(l),tvglogo(l)))

# ---- EPG matching: asigna tvg-id real cruzando nombres con epgshare01 ----
def deacc(s): return "".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")
ESTOP={"canal","de","costa","rica","mexico","argentina","colombia","chile","peru","ecuador","venezuela","espana","spain","usa","hd","fhd","uhd","sd","tv","the","el","la","los","las","del","y","en","senal","channel","television","tele","est","oeste","norte","sur"}
def etoks(name):
    s=deacc(name).lower(); s=re.sub(r"\(.*?\)"," ",s); s=re.sub(r"[^a-z0-9 ]"," ",s)
    return frozenset(t for t in s.split() if t and t not in ESTOP)
EPG_CC=["CR1","MX1","AR1","CO1","CL1","PE1","EC1","ES1"]
EPG_URLS=[f"https://epgshare01.online/epgshare01/epg_ripper_{c}.xml.gz" for c in EPG_CC]
exact={}; allchans=[]
for url in EPG_URLS:
    try:
        raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60,context=ctx).read()
        xml=gzip.decompress(raw).decode("utf-8","replace")
        for m in re.finditer(r'<channel id="([^"]*)">(.*?)</channel>',xml,re.S):
            cid=m.group(1)
            for dn in re.findall(r'<display-name[^>]*>([^<]*)',m.group(2)):
                t=etoks(dn)
                if not t: continue
                if t not in exact: exact[t]=cid
                allchans.append((t,cid))
    except Exception as e: print("  EPG !",url[-22:],e)
print("EPG index:",len(exact),"exact /",len(allchans),"total")
def epgmatch(name):
    nt=etoks(name)
    if not nt: return ""
    if nt in exact: return exact[nt]
    if len(nt)<2 or not any(not t.isdigit() for t in nt): return ""
    best="";bx=99
    for et,cid in allchans:
        if nt<et:
            ex=len(et-nt)
            if ex<bx: bx=ex;best=cid
    return best
PREMIUM_EPG="http://galileatv.top:8080/xmltv.php?username=deco-20&password=VumqaPUzpX"
HEADER=",".join(EPG_URLS+[PREMIUM_EPG])
out.sort(key=lambda x:(x[0], x[1], x[2].lower()))
seen=set(); f=open("latam.m3u","w"); f.write(f'#EXTM3U url-tvg="{HEADER}"\n'); w=0; epgn=0
for o,g,n,u,tid,logo in out:
    kk=(g,dkey(n))
    if kk in seen or not dkey(n): continue
    seen.add(kk)
    eid=epgmatch(n)                       # tvg-id real desde EPG (ignora el original, suele ser basura)
    if eid: epgn+=1
    attrs=f'tvg-id="{eid or tid}"' + (f' tvg-logo="{logo}"' if logo else "")
    f.write(f'#EXTINF:-1 {attrs} group-title="{g}",{n}\n{u}\n'); w+=1
f.close(); print("TOTAL:",w,"| con EPG:",epgn)
