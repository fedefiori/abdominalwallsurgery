#!/usr/bin/env bash
# ============================================================================
# Collaudo post-pubblicazione di chirurgiadellaparete.it (da lanciare DOPO il
# cambio DNS, una riga per controllo). Uso: bash scripts/collaudo-301.sh
# Criteri hub 04/10/2026: ogni redirect in UN solo salto; i crawler ricevono
# l'HTML completo, non il guscio; i file SEO alla radice sono quelli generati.
# ============================================================================
D="https://www.chirurgiadellaparete.it"
FAIL=0

check() { # check <path> <atteso_http> <atteso_location_o_vuoto>
  local out loc code
  out=$(curl -s -o /dev/null -w "%{http_code} %{redirect_url}" --max-time 15 "$D$1")
  code=${out%% *}; loc=${out#* }
  if [ "$code" = "$2" ] && { [ -z "$3" ] || [ "$loc" = "$3" ]; }; then
    echo "OK   $1 -> $code $loc"
  else
    echo "FAIL $1 -> $code $loc (atteso $2 $3)"; FAIL=1
  fi
}

echo "== 1. Le 10 rotte invariate: 200 diretto, nessun salto =="
for p in "/" \
  "/anatomia-della-parete-addominale-e-abdominal-core/" \
  "/difetti-della-parete-addominale-e-classificazione/" \
  "/sintomi-e-complicanze/" \
  "/radiologia/" \
  "/preabilitazione-dei-pazienti-all-intervento-chirurgico/" \
  "/la-terapia-chirurgica/" \
  "/le-protesi-in-chirurgia-della-parete-e-il-piano-di-posizionamento-della-protesi/" \
  "/le-complicanze-chirurgiche-la-vac-therapy/" \
  "/contatti/"; do
  check "$p" 200 ""
done

echo "== 2. Le due uscite dal dominio: 301 in un solo salto =="
check "/la-diastasi-dei-muscoli-retti/" 301 "https://www.diastasiedintorni.it/cose-una-diastasi/"
check "/chi-sono/" 301 "https://www.federicofiori.com/curriculum"
check "/home" 301 "$D/"
check "/articoli/tecnica-tesar-riparazione-endoscopica-sublay-anteriore" 301 "$D/articoli"

echo "== 3. File SEO alla radice (via Worker, generati dal backend) =="
curl -s --max-time 15 "$D/sitemap.xml" | grep -q "<urlset" && echo "OK   sitemap.xml e' XML" || { echo "FAIL sitemap.xml"; FAIL=1; }
curl -s --max-time 15 "$D/sitemap.xml" | grep -q "/video/" && echo "OK   /video/ in sitemap" || { echo "FAIL /video/ mancante in sitemap"; FAIL=1; }
curl -s --max-time 15 "$D/robots.txt" | grep -q "GPTBot" && echo "OK   robots.txt con allow-list AI" || { echo "FAIL robots.txt"; FAIL=1; }
curl -s --max-time 15 "$D/llms.txt" | grep -q "Federico Fiori" && echo "OK   llms.txt generato" || { echo "FAIL llms.txt"; FAIL=1; }

echo "== 4. I crawler ricevono l'HTML completo (non il guscio) =="
for ua in Googlebot GPTBot PerplexityBot; do
  for p in "/" "/la-terapia-chirurgica/" "/video/"; do
    h=$(curl -s --max-time 20 -A "$ua" "$D$p")
    if echo "$h" | grep -q "<header><nav" && echo "$h" | grep -q "max-snippet:-1" && echo "$h" | grep -q "application/ld+json"; then
      echo "OK   $ua $p (nav + robots + JSON-LD)"
    else
      echo "FAIL $ua $p: HTML incompleto"; FAIL=1
    fi
  done
done

echo "== 5. 404 vero su indirizzo inesistente =="
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$D/indirizzo-che-non-esiste/")
[ "$code" = "404" ] && echo "OK   404 status" || { echo "FAIL 404 -> $code"; FAIL=1; }

echo "== 6. Pagina Video: caricamento al clic =="
curl -s --max-time 15 "$D/video/" | grep -q "youtube-nocookie" && echo "nota: iframe nel guscio SPA (normale: il nocookie parte al clic nel browser)"

[ $FAIL -eq 0 ] && echo "COLLAUDO SUPERATO" || echo "COLLAUDO CON ERRORI"
