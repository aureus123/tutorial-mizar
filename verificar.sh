#!/bin/sh
# Uso:  ./verificar.sh ARTICULO        verifica text/ARTICULO.miz  (tu ejercicio)
#       ./verificar.sh -s ARTICULO     verifica soluciones/ARTICULO.miz
#       ./verificar.sh -t              verifica todos los ejercicios de text/
#       ./verificar.sh -s -t           verifica todas las soluciones
# Lista los errores con su explicacion (sin modificar el archivo .miz).
# Requiere los binarios de Mizar (makeenv, verifier) en el PATH y la variable
# MIZFILES apuntando al directorio compartido de Mizar (el que contiene mml.vct).
cd "$(dirname "$0")"
if [ -z "$MIZFILES" ] || ! command -v verifier > /dev/null; then
  echo "Definir MIZFILES y poner los binarios de Mizar en el PATH." >&2; exit 1
fi
dir=text
if [ "$1" = "-s" ]; then dir=soluciones; shift; fi
if [ "$1" = "-t" ]; then
  for f in "$dir"/*.miz; do
    n=$(basename "$f" .miz)
    if [ "$dir" = soluciones ]; then sh "$0" -s "$n" | tail -1; else sh "$0" "$n" | tail -1; fi
  done
  exit 0
fi
if [ -z "$1" ]; then sed -n '2,5p' "$0"; exit 1; fi
n=$(basename "$1" .miz)
a="$dir/$n"
if [ ! -f "$a.miz" ]; then echo "No existe $a.miz" >&2; exit 1; fi
rm -f "$a.err"
makeenv "$a" > "$a.acc.log" 2>&1
if [ -s "$a.err" ]; then echo "ERRORES EN EL ENTORNO (environ)"; else verifier -q "$a" > /dev/null 2>&1; fi
python3 - "$a" "$MIZFILES/mizar.msg" <<'PY'
import sys, re
a, msgf = sys.argv[1], sys.argv[2]
msgs, cur = {}, None
for l in open(msgf, encoding='latin-1'):
    m = re.match(r'# (\d+)$', l.strip())
    if m: cur = int(m.group(1)); continue
    if cur is not None and l.strip() and cur not in msgs: msgs[cur] = l.strip()
src = open(a + '.miz', encoding='latin-1').read().split('\n')
try: errs = sorted(tuple(map(int, l.split())) for l in open(a + '.err') if l.strip())
except FileNotFoundError: errs = []
for ln, col, code in errs:
    print(f"{a}.miz:{ln}:{col}: *{code} {msgs.get(code, '')}\n    {src[ln-1].strip() if 0 < ln <= len(src) else ''}")
if any(800 <= k < 900 for _, _, k in errs):
    print("    (errores 8xx: el entorno pide algo que no se encuentra. Si el articulo usa la\n"
          "     biblioteca local, ejecuta antes:  miz2prel text/ARTICULO_IMPORTADO)")
print(f"ERRORES: {len(errs)}  ({a}.miz)" if errs else f"OK: {a}.miz verificado sin errores")
PY
# se conservan solo las fuentes
find "$dir" -name "$n.*" ! -name "$n.miz" -delete
