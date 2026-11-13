#!/usr/bin/env python3
"""Arma tutorial/index.html a partir de parts/*.html y ejercicios.json."""
import os, re, json, glob, html
B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(B)), 'index.html')
J = f'{B}/ejercicios.json'
if not os.path.exists(J):
    raise SystemExit('Falta ejercicios.json: ejecuta antes  python3 _fuentes/build/gen.py  (sin argumentos)')
d = json.load(open(J))
faltan = sorted(os.path.basename(p)[:-4] for p in glob.glob(f'{os.path.dirname(B)}/master/*.miz')
                if os.path.basename(p)[:-4] not in d)
if faltan:
    raise SystemExit('ejercicios.json no tiene ' + ', '.join(faltan) + ': ejecuta  python3 _fuentes/build/gen.py  (sin argumentos)')
datos = {}
for n, v in d.items():
    ejs = []
    for x in v['ejercicios']:
        vistos, sint = set(), []
        for e in v['solo'].get(x['id'], []):
            if e['cod'] not in vistos: vistos.add(e['cod']); sint.append(dict(cod=e['cod'], msg=e['msg']))
        if n == 't06_env': sint = []   # ejercicios encadenados: el sintoma depende del orden
        e = dict(id=x['id'], consigna=x['consigna'], pistas=x['pistas'], sol=x['sol'], alt=x['alt'], linea=x['linea'], sint=sint)
        if n == 't11_def' and x['id'] == '1':   # la solucion no esta en el .miz sino en un vocabulario nuevo
            e.update(sol='Odoble', alt=None, rot='Contenido del archivo nuevo dict/t11_mio.voc')
        ejs.append(e)
    item = dict(ejercicios=ejs, errores=v['errores'])
    if n == 't18_limp': item['util'] = v['extra']['util_ej']
    if n == 't06_env':
        item['etapas'] = [sorted({e['cod'] for e in et['errores']}) for et in v['etapas']]
    datos[n] = item
src = ''.join(open(p, encoding='utf-8').read() for p in sorted(glob.glob(f'{B}/parts/*.html')))
def miz(m): return '<div class="bloque"><pre class="miz">' + html.escape(m.group(1).strip('\n'), quote=False) + '</pre></div>'
src = re.sub(r'<miz>\n?(.*?)</miz>', miz, src, flags=re.S)
src = re.sub(r'<div class="bloque"><pre class="miz">(.*?)</pre></div>',
             lambda m: m.group(0) if '&lt;' in m.group(1) or '&amp;' in m.group(1) or '&gt;' in m.group(1) or not re.search(r'[<>&]', m.group(1)) else miz(m), src, flags=re.S)
src = re.sub(r'<c>(.*?)</c>', lambda m: '<code>' + html.escape(m.group(1), quote=False) + '</code>', src, flags=re.S)
src = re.sub(r'<cl>(.*?)</cl>', lambda m: '<code class="l">' + html.escape(m.group(1), quote=False) + '</code>', src, flags=re.S)
blob = json.dumps(datos, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert '/*__DATOS__*/' in src
src = src.replace('/*__DATOS__*/', blob)
open(OUT, 'w', encoding='utf-8').write(src)
print(f'{OUT}: {len(src.encode("utf-8"))//1024} KB, {sum(len(v["ejercicios"]) for v in datos.values())} ejercicios')
# comprobaciones simples
for m in re.finditer(r'data-archivo="(\w+)"', src):
    assert m.group(1) in datos, m.group(1)
ids = set(re.findall(r'class="quiz" data-id="(\w+)"', src))
defs = set(re.findall(r'^  (l\d\d[a-c]): \{ p:', src, flags=re.M))
print('quiz sin definir:', ids - defs, '| definidos sin usar:', defs - ids)
