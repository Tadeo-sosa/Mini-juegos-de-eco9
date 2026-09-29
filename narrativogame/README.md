# Pequeña Fortuna (demo) – Skeleton Pygame
Estructura mínima para un juego point-and-click *cozy*, con narrador y finales múltiples.

## Requisitos instalar dentro de un entorno virtual
- virtualenv env
- /env/Scripts/activate.bat
- 
- Python 3.10+
- `pip install pygame`

## Ejecutar
```bash
python main.py
```

## Estructura
```
little_misfortune_like/
  main.py
  settings.py
  engine/
    scene_manager.py
    narrator.py
    audio.py
    ui.py
  game/
    state.py
  scenes/
    title.py
    forest.py
    ending.py
  narrative/
    script.json
  assets/
    images/
    audio/
      narrator_beep.wav
      ui_click.wav
      ambience_loop.wav
    fonts/
```

## Qué incluye
Qué incluye

Gestor de escenas (engine/scene_manager.py): Title → Forest → Ending.

Narrador externo (engine/narrator.py): subtítulos + “beep” placeholder (reemplazable por voces reales por línea).

Estado y estadísticas (game/state.py): bondad modifica el final.

Puzzles simples / hotspots: escena Forest con “brillo” clickeable y zona de salida.

Audio (engine/audio.py): ambiente en loop + SFX de clic (generados como placeholder).

UI (engine/ui.py): botón “Comenzar”.

Guion (narrative/script.json): líneas del narrador y finales.

Estilo cozy: paleta suave, fondo tranquilo; listo para reemplazar por tus ilustraciones 2D.

## Próximos pasos
- Añadir *arte 2D* (fondos y elementos).
- Integrar **parallax** leve para dar sensación *side-scrolling* en algunas escenas anchas.
- Cargar **voz real** por línea (por ejemplo `narrative/voice/title_01.wav`).
- Sistema de **puzzles**: definir hotspots con condiciones y feedback.
- Guardado/carga de partidas (JSON).
- Árbol de decisiones (por ejemplo `narrative/graph.yaml`).

> Nota: El loop de ambiente y los *beeps* son tonos generados solo como placeholder, eso significa que deben ser sobrescritos luego.
