#!/usr/bin/env python3
"""Consulta la biblioteca de Mizar (MML) leyendo los resumenes (.abs).

  ./mml.py XREAL_1:63 XCMPLX_1:def 4     muestra teoremas/definiciones/esquemas por referencia
  ./mml.py -g 'sqrt.*<=' [ARTICULO ...]   busca items cuyo texto coincide con la expresion regular
                                          (en toda la MML o solo en los articulos dados)
Requiere la variable MIZFILES.
"""
import os, re, sys, glob

def items(path):
    """Divide un .abs en items (theorem, definition, registration, scheme, ...)."""
    txt = open(path, encoding='latin-1').read()
    txt = txt.split('\nbegin', 1)[-1]
    parts = re.split(r'\n(?=(?:theorem|definition|registration|scheme|notation|reserve|begin)\b)', txt)
    out = []
    for p in parts:
        lines = p.rstrip().split('\n')
        # se descartan los comentarios y lineas en blanco que quedan al final del item
        while lines and (not lines[-1].strip() or lines[-1].lstrip().startswith('::')
                         and not re.search(r'::\s*[A-Z0-9_]+:', lines[-1])):
            lines.pop()
        if lines and not lines[0].startswith('begin'): out.append('\n'.join(lines))
    return out

def by_ref(ref):
    m = re.match(r'([A-Za-z0-9_]+):(def |sch )?\s*(\d+)$', ref)
    if not m:
        print(f'Referencia no reconocida: {ref}'); return
    art, kind, num = m.group(1).upper(), (m.group(2) or ''), m.group(3)
    path = os.path.join(os.environ['MIZFILES'], 'abstr', art.lower() + '.abs')
    if not os.path.exists(path):
        print(f'No existe el articulo {art}'); return
    tag = re.compile(r'::\s*' + re.escape(f'{art}:{kind}{num}') + r'(?!\d)')
    for it in items(path):
        if tag.search(it):
            print(f'--- {art}:{kind}{num}'); print(it); print(); return
    print(f'No se encontro {art}:{kind}{num}')

def grep(rx, arts):
    rx = re.compile(rx)
    base = os.path.join(os.environ['MIZFILES'], 'abstr')
    paths = [os.path.join(base, a.lower() + '.abs') for a in arts] or sorted(glob.glob(base + '/*.abs'))
    n = 0
    for p in paths:
        if not os.path.exists(p): continue
        for it in items(p):
            flat = ' '.join(l for l in it.split('\n') if not l.lstrip().startswith('::$'))
            if rx.search(flat):
                print(it); print(); n += 1
                if n >= 60:
                    print('... (mas de 60 resultados: refina la busqueda)'); return

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or 'MIZFILES' not in os.environ:
        print(__doc__); sys.exit(1)
    if a[0] == '-g':
        grep(a[1], a[2:])
    else:
        refs, i = [], 0
        while i < len(a):          # permite "XCMPLX_1:def" "4" separados por el shell
            if a[i].endswith(('def', 'sch')) and i + 1 < len(a):
                refs.append(a[i] + ' ' + a[i+1]); i += 2
            else:
                refs.append(a[i]); i += 1
        for r in refs: by_ref(r)
