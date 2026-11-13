# Fuentes del tutorial

Los archivos de `text/`, `soluciones/` e `index.html` se generan a partir de lo que hay aquí.
Si quieres cambiar un ejercicio o el texto de una lección, edita la fuente y regenera.

- `master/NOMBRE.miz`: cada artículo completo, con los huecos marcados:

      ::@ej 3 | Consigna del ejercicio (primer renglón)
      ::@ continuación de la consigna
      ::@pista Texto de una pista (HTML; sólo se usa en la página)
      ::@sol
        renglones de la solución
      ::@alt
        renglones que ve el estudiante en su lugar (opcional)
      ::@fin

- `build/gen.py [NOMBRE ...]`: genera `text/NOMBRE.miz` y `soluciones/NOMBRE.miz`, los verifica
  con Mizar (la solución debe dar cero errores y cada hueco debe producir alguno) y guarda los
  errores esperados en `build/ejercicios.json`. Sin argumentos procesa todos.
- `build/parts/*.html`: el texto de la página, por partes. `<miz>…</miz>` es un bloque de código
  y `<c>…</c>` código en línea (se escapan solos).
- `build/build_html.py`: une las partes con `ejercicios.json` y escribe `index.html`.

`ejercicios.json` no está en el repositorio: la primera vez hay que ejecutar `gen.py` sin argumentos
para crearlo. Después se puede regenerar sólo un artículo con `gen.py NOMBRE`.

      python3 _fuentes/build/gen.py && python3 _fuentes/build/build_html.py

Ojo: `gen.py` vuelve a escribir `text/`, así que borra lo que hayas resuelto ahí, y al procesar
`t18_uso` crea y luego elimina la carpeta `prel/`. Hace falta Mizar instalado (ver `README.md`).
