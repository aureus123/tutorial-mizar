# tutorial-mizar

Tutorial interactivo, en español, para aprender a formalizar matemática en
[Mizar](https://mizar.uwb.edu.pl/). Está pensado para estudiantes de grado:
lógica, igualdades y desigualdades, ecuaciones polinómicas, conjuntos, funciones
monótonas, límites y continuidad, inducción, cardinales y estructuras algebraicas.

Son 19 lecciones con 90 ejercicios. Cada lección se lee en una página web
(`index.html`) y se practica completando demostraciones en archivos `.miz`
con VS Code. El recorrido sigue el manual de Freek Wiedijk
[*Writing a Mizar article in nine easy steps*](https://www.cs.ru.nl/~freek/mizar/mizman.pdf)
y cubre todos sus temas, adaptados a la versión actual de Mizar.

## Versiones

El tutorial se escribió y se verificó con:

| Componente | Versión |
|---|---|
| Mizar (verificador) | 8.1.15 (compilación para Darwin/FPC, mayo de 2025) |
| MML (biblioteca de Mizar) | 5.94.1493 |
| Visual Studio Code | 1.145.2 |
| Extensión de VS Code *Mizar extension* (`fpsbpkm.mizar-extension`) | 0.6.3 |
| Python | 3.9 (cualquier Python 3 sirve) |

Sistema: macOS en un procesador Intel (x86_64).

Con otras versiones de Mizar o de la MML casi todo debería funcionar, pero
algunos teoremas citados pueden haber cambiado de número o de artículo.

## Instalación

### 1. Mizar

1. Descarga la distribución para tu sistema desde la página oficial:
   <https://mizar.uwb.edu.pl/system/> (también en <http://mizar.org/system/>).
   Hay versiones para Linux, macOS y Windows.
2. En Linux y macOS, descomprime el archivo y ejecuta el instalador:

   ```sh
   tar -xf mizar-*.tar
   ./install.sh
   ```

   El instalador pregunta tres carpetas: los programas (por omisión
   `/usr/local/bin`), los archivos compartidos con la biblioteca (por omisión
   `/usr/local/share/mizar`) y la documentación. Puedes elegir carpetas de tu
   usuario si no quieres instalar en `/usr/local`.
3. Define la variable `MIZFILES` con la carpeta de archivos compartidos y
   agrega la de los programas al `PATH`. Por ejemplo, en `~/.zshenv` (macOS) o
   en `~/.bashrc` / `~/.profile` (Linux):

   ```sh
   export MIZFILES=/usr/local/share/mizar
   export PATH=/usr/local/bin:$PATH
   ```

4. Abre una terminal nueva y comprueba que todo responde:

   ```sh
   echo $MIZFILES     # debe mostrar la carpeta de archivos compartidos
   verifier           # debe mostrar la versión de Mizar
   ```

En Windows, el instalador de la distribución hace el trabajo equivalente;
la variable `MIZFILES` se define en *Configuración del sistema → Variables de
entorno*. Los scripts `verificar.sh` y `mml.py` de este repositorio están
pensados para Linux y macOS (en Windows funcionan desde WSL o Git Bash).

### 2. VS Code y la extensión de Mizar

1. Instala [Visual Studio Code](https://code.visualstudio.com/).
2. En la vista de extensiones (`Ctrl+Shift+X`; en macOS, `⇧⌘X`) busca
   **Mizar extension** (publicada por *fpsbpkm*) e instálala.
3. La extensión lee `MIZFILES` y el `PATH` del entorno con que se abrió VS Code.
   Si al compilar avisa *You have to set environment variable "MIZFILES"*,
   abre VS Code desde una terminal donde las variables estén definidas:

   ```sh
   code tutorial-mizar
   ```

### 3. Python 3

Lo usan `verificar.sh` (para mostrar los errores con su explicación) y
`mml.py`. Viene instalado en macOS y en casi todas las distribuciones de Linux.

## Uso

1. Clona el repositorio y abre la carpeta en VS Code:

   ```sh
   git clone https://github.com/aureus123/tutorial-mizar.git
   code tutorial-mizar
   ```

2. Abre `index.html` en el navegador y empieza por *Preparación*.
3. Para cada lección, abre en VS Code el archivo de `text/` que indica la
   página, ejecuta **Mizar Compile** (botón ▷ arriba a la derecha, o desde la
   paleta de comandos) y completa los renglones marcados con
   `:: EJERCICIO n:` hasta que no quede ningún error.

Desde la terminal, en la carpeta del repositorio:

```sh
./verificar.sh t01_hola          # compila text/t01_hola.miz y explica los errores
./verificar.sh -s t01_hola       # lo mismo con soluciones/t01_hola.miz
./verificar.sh -s -t             # verifica todas las soluciones
./mml.py XREAL_1:63              # muestra un teorema de la MML
./mml.py -g 'sqrt.*<=' SQUARE_1  # busca teoremas por expresión regular
```

`soluciones/t18_uso.miz` usa otro artículo del tutorial como biblioteca local:
antes de compilarlo hay que ejecutar `miz2prel text/t18_bib` (lo explica la
lección 18).

## Contenido

```
tutorial-mizar/
├── index.html      la página del tutorial (autocontenida, funciona sin conexión)
├── text/           los artículos con huecos: aquí se trabaja
├── soluciones/     los mismos artículos, completos y verificados
├── dict/           vocabularios (símbolos nuevos) de los artículos
├── verificar.sh    compila un artículo y lista los errores con su explicación
├── mml.py          busca teoremas, definiciones y esquemas en la MML
├── _fuentes/       fuentes desde las que se generan index.html, text/ y soluciones/
└── LICENSE         licencia GPLv3
```

Para modificar ejercicios o lecciones, consulta `_fuentes/LEEME.md`.

## Licencia

Este tutorial se distribuye bajo la licencia GNU General Public License,
versión 3 (GPLv3). El texto completo está en [`LICENSE`](LICENSE).
