# Classic Art Archive - Web Specifications

## 1. Concepto y Estilo
- **Tema:** Galería de arte clásico curada (Pintura renacentista, barroca, romanticismo, etc.).
- **Estética:** Minimalista, elegante, editorial, fondo oscuro o crema (#0f0f10 o #fcfbf9), tipografía serif refinada (Playfair Display o Cormorant Garamond).
- **Objetivo:** Catálogo visual de obras, enlaces a los posts de Instagram, biografía y formulario/enlace de newsletter o contacto.

## 2. Stack Técnico
- **Backend:** Python (FastAPI o Flask).
- **Frontend:** Jinja2 templates + Tailwind CSS (vía CDN para máxima rapidez).
- **Datos de las obras:** Archivo `artworks.json` o base de datos SQLite para facilitar añadir/editar obras en segundos.
- **Estructura de páginas:**
  1. `/` (Galería / Feed principal con filtros por época/artista y vista modal de detalle).
  2. `/about` (Historia del archivo, manifiesto y enlace directo al perfil de Instagram).
  3. `/archive` (Lista cronológica / índice alfabético).
