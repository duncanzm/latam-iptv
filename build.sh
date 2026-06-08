#!/bin/bash
# Construye lista IPTV solo Latam + US + España desde world_ip_tv (auto-verificado)
set -e
OUT="latam.m3u"
echo "#EXTM3U" > "$OUT"
# US, España + Latam hispanohablante
for c in us es mx ar co cl pe ec ve cr do py hn pr gt sv bo cu pa ni uy; do
  curl -sL --fail "https://raw.githubusercontent.com/Romaxa55/world_ip_tv/master/output/$c.m3u" 2>/dev/null | grep -v "^#EXTM3U" >> "$OUT" || echo "skip $c"
done
echo "Canales: $(grep -c '#EXTINF' "$OUT")"
