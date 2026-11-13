#!/usr/bin/env python3
"""Genera text/ (ejercicios) y soluciones/ a partir de _fuentes/master/*.miz,
los verifica con Mizar y escribe build/ejercicios.json.
Uso: gen.py [NOMBRE ...]   (sin argumentos: todos)"""
import os, re, sys, json, subprocess, glob
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.dirname(S)          # la raiz del tutorial
MSG = {}
cur = None
for l in open(os.path.join(os.environ['MIZFILES'], 'mizar.msg'), encoding='latin-1'):
    m = re.match(r'# (\d+)$', l.strip())
    if m: cur = int(m.group(1)); continue
    if cur is not None and l.strip() and cur not in MSG: MSG[cur] = l.strip()

def parse(path):
    sol, ej, exs = [], [], []
    st, cur = 'n', None
    for raw in open(path, encoding='utf-8').read().split('\n'):
        s = raw.strip()
        if s.startswith('::@ej '):
            ind = raw[:len(raw) - len(raw.lstrip())]
            m = re.match(r'::@ej (\S+) \| ?(.*)$', s)
            cur = dict(id=m.group(1), consigna=[m.group(2)], pistas=[], sol=[], alt=None, ind=ind)
            exs.append(cur); st = 'h'; continue
        if st == 'h' and s.startswith('::@pista '):
            cur['pistas'].append(s[9:]); continue
        if st == 'h' and s == '::@sol':
            head = [f"{cur['ind']}:: EJERCICIO {cur['id']}: {cur['consigna'][0]}"] + \
                   [f"{cur['ind']}::   {c}" for c in cur['consigna'][1:]]
            sol += head; cur['linea'] = len(ej) + 1; ej += head; st = 's'; continue
        if st == 'h' and s.startswith('::@'):
            cur['consigna'].append(s[3:].strip()); continue
        if st == 's' and s == '::@alt': cur['alt'] = []; st = 'a'; continue
        if st in 'sa' and s == '::@fin':
            if cur['alt'] is None and cur.get('hueco', True):
                pass
            st = 'n'; continue
        if st == 's': sol.append(raw); cur['sol'].append(raw); continue
        if st == 'a': ej.append(raw); cur['alt'].append(raw); continue
        assert not s.startswith('::@'), (path, raw)
        sol.append(raw); ej.append(raw)
    assert st == 'n', path
    return sol, ej, exs

def verify(d, n):
    a = f'{d}/{n}'
    for f in glob.glob(os.path.join(T, a + '.*')):
        if not f.endswith('.miz'): os.remove(f)
    r = subprocess.run(['makeenv', a], cwd=T, capture_output=True, text=True)
    envfail = os.path.exists(os.path.join(T, a + '.err')) and os.path.getsize(os.path.join(T, a + '.err')) > 0
    if not envfail:
        subprocess.run(['verifier', '-q', a], cwd=T, capture_output=True, text=True)
    errs = []
    try:
        errs = sorted(tuple(map(int, l.split())) for l in open(os.path.join(T, a + '.err')) if l.strip())
    except FileNotFoundError: pass
    for f in glob.glob(os.path.join(T, a + '.*')):
        if not f.endswith('.miz'): os.remove(f)
    return [dict(linea=l, col=c, cod=k, msg=MSG.get(k, '')) for l, c, k in errs], envfail

def variant(path, solved):
    """Texto con los ejercicios de `solved` resueltos y el resto sin resolver."""
    out, st, cur = [], 'n', None
    for raw in open(path, encoding='utf-8').read().split('\n'):
        s = raw.strip()
        if s.startswith('::@ej '): cur = re.match(r'::@ej (\S+)', s).group(1); st = 'h'; continue
        if st == 'h':
            if s == '::@sol': st = 's'
            continue
        if st == 's' and s == '::@alt': st = 'a'; continue
        if st in 'sa' and s == '::@fin': st = 'n'; continue
        if st == 's':
            if cur in solved: out.append(raw)
            continue
        if st == 'a':
            if cur not in solved: out.append(raw)
            continue
        out.append(raw)
    return out

LIBRE = {'t18_limp'}      # ejercicios que no producen errores de verificacion
UTILS = ['irrvoc', 'irrths', 'relprem', 'chklab', 'inacc', 'relinfer', 'reliters', 'trivdemo']

def utilidades(d, n):
    out = {}
    a = f'{d}/{n}'
    for u in UTILS:
        subprocess.run(['makeenv', a], cwd=T, capture_output=True, text=True)
        subprocess.run([u, a], cwd=T, capture_output=True, text=True)
        try:
            errs = sorted(tuple(map(int, l.split())) for l in open(os.path.join(T, a + '.err')) if l.strip())
        except FileNotFoundError: errs = []
        out[u] = [dict(linea=l, col=c, cod=k, msg=MSG.get(k, '')) for l, c, k in errs]
    for f in glob.glob(os.path.join(T, a + '.*')):
        if not f.endswith('.miz'): os.remove(f)
    return out

def prel(on):
    import shutil
    shutil.rmtree(f'{T}/prel', ignore_errors=True)
    if on:
        subprocess.run(['miz2prel', 'soluciones/t18_bib'], cwd=T, capture_output=True, text=True)
        for f in glob.glob(f'{T}/soluciones/t18_bib.*'):
            if not f.endswith('.miz'): os.remove(f)

def check_variants(n, exs):
    """Cada ejercicio debe ser necesario; ademas se registran las etapas acumulativas."""
    ids = [x['id'] for x in exs]
    res = {}
    os.makedirs(f'{T}/zz', exist_ok=True)
    for i in ids:
        open(f'{T}/zz/{n}.miz', 'w', encoding='utf-8').write('\n'.join(variant(f'{S}/master/{n}.miz', set(ids) - {i})))
        e, _ = verify('zz', n)
        res[i] = e
        if not e and n not in LIBRE: print(f'  !! {n}: el ejercicio {i} no produce ningun error al quedar sin resolver')
    etapas = []
    for k in range(len(ids) + 1):
        open(f'{T}/zz/{n}.miz', 'w', encoding='utf-8').write('\n'.join(variant(f'{S}/master/{n}.miz', set(ids[:k]))))
        e, env = verify('zz', n)
        etapas.append(dict(resueltos=k, errores=e, entorno=env))
    os.remove(f'{T}/zz/{n}.miz'); os.rmdir(f'{T}/zz')
    return res, etapas

def main():
    names = sys.argv[1:] or sorted(os.path.basename(p)[:-4] for p in glob.glob(S + '/master/*.miz'))
    jpath = S + '/build/ejercicios.json'
    data = json.load(open(jpath)) if os.path.exists(jpath) else {}
    for n in names:
        sol, ej, exs = parse(f'{S}/master/{n}.miz')
        for lines, d in ((sol, 'soluciones'), (ej, 'text')):
            for i, l in enumerate(lines):
                if len(l.encode('utf-8')) > 79 or len(l) > 77: print(f'  !! {d}/{n}.miz:{i+1}: linea larga ({len(l)})')
                if '\t' in l: print(f'  !! tab en {d}/{n}.miz:{i+1}')
            open(f'{T}/{d}/{n}.miz', 'w', encoding='utf-8').write('\n'.join(lines))
        extra = {}
        if n == 't18_uso':
            prel(False); extra['sin_prel'], _ = verify('text', n); prel(True)
        es, _ = verify('soluciones', n)
        ee, envfail = verify('text', n)
        if n in LIBRE:
            extra['util_ej'] = utilidades('text', n); extra['util_sol'] = utilidades('soluciones', n)
            for u, e in extra['util_sol'].items():
                if e: print(f'  !! {n}: la solucion no esta limpia segun {u}: {e}')
            print('   utilidades sobre el ejercicio: ' + '; '.join(f"{u}: " + ','.join(f"{e['linea']}:*{e['cod']}" for e in v) for u, v in extra['util_ej'].items()))
        print(f"{n}: solucion {'OK' if not es else 'ERRORES'}; ejercicio con {len(ee)} errores" + (' (ENTORNO)' if envfail else ''))
        for e in es: print(f"   SOL {e['linea']}:{e['col']} *{e['cod']} {e['msg']}\n       {sol[e['linea']-1].strip()}")
        if '-v' in os.environ.get('GENFLAGS', ''):
            for e in ee: print(f"   EJ  {e['linea']}:{e['col']} *{e['cod']} {e['msg']}\n       {ej[e['linea']-1].strip()}")
        solo, etapas = check_variants(n, exs)
        if '-e' in os.environ.get('GENFLAGS', ''):
            for et in etapas:
                print(f"   ETAPA {et['resueltos']}: " + ', '.join(f"{e['linea']}:*{e['cod']}" for e in et['errores']))
        if n == 't18_uso': prel(False)
        data[n] = dict(nombre=n, solo=solo, etapas=etapas, extra=extra, ejercicios=[dict(id=x['id'], consigna=' '.join(x['consigna']), pistas=x['pistas'],
                        sol='\n'.join(x['sol']), alt=None if x['alt'] is None else '\n'.join(x['alt']), linea=x['linea'])
                        for x in exs], errores=ee, entorno=envfail, sol_ok=not es,
                       fuente='\n'.join(ej), solucion='\n'.join(sol))
    json.dump(data, open(jpath, 'w'), ensure_ascii=False, indent=1)

main()
