import math
import random
import pygame

from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene
from scenes.drones import DronesScene


class ElectricScene(Scene):
    """
    MINIJUEGO 1
    Sistema eléctrico y fantasmas.

    Matemática:
        Cada selección = ensayo de Bernoulli.
        Éxito = fusible correcto.
        Fracaso = fusible incorrecto.

        Después de 5 intentos:
            X ~ Binomial(n=5, p=1/3)

    Objetivo:
        Conseguir 3 éxitos para restaurar la iluminación.
    """

    TOTAL_INTENTOS = 5
    EXITOS_NECESARIOS = 3
    CANTIDAD_FUSIBLES = 3

    # 1 fusible correcto de 3
    PROBABILIDAD_EXITO = 1 / CANTIDAD_FUSIBLES

    def __init__(self, manager, state, audio):
        super().__init__(manager)

        self.state = state
        self.audio = audio

        # -----------------------------------------
        # FUENTES
        # -----------------------------------------

        self.font_title = pygame.font.SysFont(
            "arial", 34, bold=True
        )

        self.font = pygame.font.SysFont(
            "arial", 22
        )

        self.font_small = pygame.font.SysFont(
            "arial", 17
        )

        self.font_big = pygame.font.SysFont(
            "arial", 28, bold=True
        )

        # -----------------------------------------
        # ESTADO
        # -----------------------------------------

        self.intentos = 0
        self.exitos = 0
        self.fallos = 0

        self.fusible_correcto = random.randint(
            0,
            self.CANTIDAD_FUSIBLES - 1
        )

        self.mensaje = (
            "La zona está a oscuras..."
        )

        self.terminado = False
        self.luces_encendidas = False

        # -----------------------------------------
        # FANTASMA
        # -----------------------------------------

        self.fantasma_visible = False

        # Posición inicial
        self.fantasma_x = WIDTH + 50

        # -----------------------------------------
        # EFECTOS
        # -----------------------------------------

        self.parpadeo_luz = 0
        self.electricidad = 0

        # -----------------------------------------
        # TEMPORIZADORES
        # -----------------------------------------

        self.temporizador_final = None
        self.mostrar_resultado = False

        # -----------------------------------------
        # BOTONES / FUSIBLES
        # -----------------------------------------

        self.fusibles = [
            pygame.Rect(
                105 + i * 255,
                275,
                190,
                105
            )
            for i in range(self.CANTIDAD_FUSIBLES)
        ]

        # -----------------------------------------
        # GAME STATE
        # -----------------------------------------

        self.state.stats["fusibles_intentados"] = 0
        self.state.stats["fusibles_correctos"] = 0
        self.state.stats["fusibles_incorrectos"] = 0

        self.state.flags["luces_restauradas"] = False
        self.state.flags["fantasmas_ahuyentados"] = False

    # =====================================================
    # ENTRAR
    # =====================================================

    def on_enter(self):

        # Evita que el clic que nos trajo hasta aquí
        # seleccione inmediatamente un fusible.
        self.input_cooldown = 0.4

    # =====================================================
    # PROBABILIDAD BINOMIAL
    # =====================================================

    def calcular_binomial(self, k):

        n = self.TOTAL_INTENTOS
        p = self.PROBABILIDAD_EXITO

        combinaciones = math.comb(n, k)

        probabilidad = (
            combinaciones
            * (p ** k)
            * ((1 - p) ** (n - k))
        )

        return probabilidad

    # =====================================================
    # ELEGIR FUSIBLE
    # =====================================================

    def elegir_fusible(self, numero):

        if self.terminado:
            return

        if self.intentos >= self.TOTAL_INTENTOS:
            return

        # -----------------------------------------
        # ENSAYO DE BERNOULLI
        # -----------------------------------------

        self.intentos += 1

        self.state.stats[
            "fusibles_intentados"
        ] = self.intentos

        # -----------------------------------------
        # ÉXITO
        # -----------------------------------------

        if numero == self.fusible_correcto:

            self.exitos += 1

            self.state.stats[
                "fusibles_correctos"
            ] = self.exitos

            self.mensaje = (
                "✓ ¡Éxito! La corriente vuelve a circular."
            )

            # Electricidad
            self.electricidad = 1

            # El fantasma retrocede
            self.fantasma_visible = False

            self.fantasma_x += 120

        # -----------------------------------------
        # FRACASO
        # -----------------------------------------

        else:

            self.fallos += 1

            self.state.stats[
                "fusibles_incorrectos"
            ] = self.fallos

            self.mensaje = (
                "✗ ¡Fallo! Un fantasma se acerca..."
            )

            self.fantasma_visible = True

            # El fantasma se acerca
            self.fantasma_x -= 80

        # -----------------------------------------
        # ¿GANAMOS?
        # -----------------------------------------

        if self.exitos >= self.EXITOS_NECESARIOS:

            self.terminado = True

            self.luces_encendidas = True

            self.state.flags[
                "luces_restauradas"
            ] = True

            self.state.flags[
                "fantasmas_ahuyentados"
            ] = True

            self.mensaje = (
                "¡La electricidad fue restaurada!"
            )

            self.temporizador_final = 4

            self.mostrar_resultado = True

        # -----------------------------------------
        # ¿PERDIMOS?
        # -----------------------------------------

        elif self.intentos >= self.TOTAL_INTENTOS:

            self.terminado = True

            self.mensaje = (
                "La energía no fue suficiente."
            )

            self.mostrar_resultado = True

        # -----------------------------------------
        # SIGUIENTE RONDA
        # -----------------------------------------

        else:

            self.fusible_correcto = random.randint(
                0,
                self.CANTIDAD_FUSIBLES - 1
            )

    # =====================================================
    # REINICIAR
    # =====================================================

    def reiniciar(self):

        self.intentos = 0
        self.exitos = 0
        self.fallos = 0

        self.fusible_correcto = random.randint(
            0,
            self.CANTIDAD_FUSIBLES - 1
        )

        self.terminado = False
        self.luces_encendidas = False

        self.fantasma_visible = False
        self.fantasma_x = WIDTH + 50

        self.parpadeo_luz = 0
        self.electricidad = 0

        self.temporizador_final = None
        self.mostrar_resultado = False

        self.mensaje = (
            "Sistema reiniciado. Elegí un fusible."
        )

        self.state.stats[
            "fusibles_intentados"
        ] = 0

        self.state.stats[
            "fusibles_correctos"
        ] = 0

        self.state.stats[
            "fusibles_incorrectos"
        ] = 0

        self.state.flags[
            "luces_restauradas"
        ] = False

        self.state.flags[
            "fantasmas_ahuyentados"
        ] = False

    # =====================================================
    # EVENTOS
    # =====================================================

    def handle_event(self, event):

        if self.input_cooldown > 0:
            return

        # -------------------------
        # TECLADO
        # -------------------------

        if event.type == pygame.KEYDOWN:

            # Reiniciar después de perder
            if (
                event.key == pygame.K_r
                and self.terminado
                and not self.luces_encendidas
            ):

                self.reiniciar()

        # -------------------------
        # MOUSE
        # -------------------------

        if (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
        ):

            if self.terminado:
                return

            for i, rect in enumerate(
                self.fusibles
            ):

                if rect.collidepoint(
                    event.pos
                ):

                    if self.audio:
                        self.audio.play_click()

                    self.elegir_fusible(i)

                    break

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        # -----------------------------------------
        # ELECTRICIDAD
        # -----------------------------------------

        if self.electricidad > 0:

            self.electricidad -= dt

        # -----------------------------------------
        # PARPADEO
        # -----------------------------------------

        if self.luces_encendidas:

            self.parpadeo_luz += dt

        # -----------------------------------------
        # FANTASMA
        # -----------------------------------------

        if self.fantasma_visible:

            self.fantasma_x -= 15 * dt

            if self.fantasma_x < WIDTH - 280:

                self.fantasma_x = WIDTH - 150

        # -----------------------------------------
        # PASAR AL FINAL
        # -----------------------------------------

        if self.temporizador_final is not None:

            self.temporizador_final -= dt

            if self.temporizador_final <= 0:

                self.manager.replace(
                  DronesScene(
                  self.manager,
                  self.state,
                  self.audio
                )
)

                self.temporizador_final = None

    # =====================================================
    # DIBUJAR FANTASMA
    # =====================================================

    def dibujar_fantasma(self, pantalla):

        if not self.fantasma_visible:
            return

        x = int(self.fantasma_x)
        y = 155

        # Sombra
        pygame.draw.ellipse(
            pantalla,
            (10, 12, 18),
            (
                x - 50,
                y + 55,
                100,
                20
            )
        )

        # Cabeza
        pygame.draw.circle(
            pantalla,
            (190, 200, 220),
            (x, y),
            42
        )

        # Cuerpo
        puntos = [
            (x - 42, y + 5),
            (x - 30, y + 65),
            (x - 10, y + 45),
            (x, y + 70),
            (x + 15, y + 45),
            (x + 30, y + 65),
            (x + 42, y + 5)
        ]

        pygame.draw.polygon(
            pantalla,
            (190, 200, 220),
            puntos
        )

        # Ojos
        pygame.draw.circle(
            pantalla,
            (35, 40, 50),
            (x - 14, y),
            6
        )

        pygame.draw.circle(
            pantalla,
            (35, 40, 50),
            (x + 14, y),
            6
        )

        # Boca
        pygame.draw.arc(
            pantalla,
            (50, 55, 65),
            (
                x - 12,
                y + 8,
                24,
                18
            ),
            0,
            math.pi,
            2
        )

    # =====================================================
    # DIBUJAR FUSIBLE
    # =====================================================

    def dibujar_fusible(
        self,
        pantalla,
        rect,
        numero
    ):

        # Color base
        if self.luces_encendidas:

            color = (110, 155, 145)

        else:

            color = (65, 75, 90)

        # Rectángulo
        pygame.draw.rect(
            pantalla,
            color,
            rect,
            border_radius=16
        )

        pygame.draw.rect(
            pantalla,
            (245, 245, 245),
            rect
)

        # Cable
        pygame.draw.line(
            pantalla,
            (235, 230, 205),
            (
                rect.centerx - 35,
                rect.centery
            ),
            (
                rect.centerx + 35,
                rect.centery
            ),
            8
        )

        # Terminales
        pygame.draw.circle(
            pantalla,
            (235, 230, 205),
            (
                rect.centerx - 35,
                rect.centery
            ),
            12
        )

        pygame.draw.circle(
            pantalla,
            (235, 230, 205),
            (
                rect.centerx + 35,
                rect.centery
            ),
            12
        )

        # Nombre
        texto = self.font_big.render(
            f"Fusible {numero + 1}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto,
            texto.get_rect(
                center=(
                    rect.centerx,
                    rect.bottom - 25
                )
            )
        )

    # =====================================================
    # DIBUJAR PANTALLA DE RESULTADO
    # =====================================================

    def dibujar_resultado(self, pantalla):

        # Panel semitransparente
        panel = pygame.Surface(
            (650, 360),
            pygame.SRCALPHA
        )

        panel.fill(
            (20, 25, 35, 235)
        )

        panel_rect = panel.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2
            )
        )

        pantalla.blit(
            panel,
            panel_rect
        )

        # Título
        if self.luces_encendidas:

            titulo = "¡SISTEMA RESTAURADO!"

        else:

            titulo = "SISTEMA SIN ENERGÍA"

        texto = self.font_title.render(
            titulo,
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto,
            texto.get_rect(
                center=(
                    WIDTH // 2,
                    125
                )
            )
        )

        # Resultado
        resultado = self.font.render(
            f"Éxitos: {self.exitos} / {self.intentos}",
            True,
            (230, 235, 240)
        )

        pantalla.blit(
            resultado,
            resultado.get_rect(
                center=(
                    WIDTH // 2,
                    180
                )
            )
        )

        # Probabilidad binomial
        probabilidad = self.calcular_binomial(
            self.exitos
        )

        binomial = self.font_small.render(
            f"P(X={self.exitos}) = "
            f"{probabilidad * 100:.1f}%",
            True,
            (215, 225, 230)
        )

        pantalla.blit(
            binomial,
            binomial.get_rect(
                center=(
                    WIDTH // 2,
                    220
                )
            )
        )

        # Explicación
        linea1 = self.font_small.render(
            "Cada selección fue un ensayo de Bernoulli:",
            True,
            (210, 220, 230)
        )

        pantalla.blit(
            linea1,
            linea1.get_rect(
                center=(
                    WIDTH // 2,
                    265
                )
            )
        )

        linea2 = self.font_small.render(
            "éxito = fusible correcto / "
            "fracaso = fusible incorrecto",
            True,
            (210, 220, 230)
        )

        pantalla.blit(
            linea2,
            linea2.get_rect(
                center=(
                    WIDTH // 2,
                    292
                )
            )
        )

        # Mensaje final
        if self.luces_encendidas:

            final = (
                "La luz ahuyentó a los fantasmas."
            )

        else:

            final = (
                "Presioná R para volver a intentarlo."
            )

        texto_final = self.font.render(
            final,
            True,
            (245, 225, 160)
        )

        pantalla.blit(
            texto_final,
            texto_final.get_rect(
                center=(
                    WIDTH // 2,
                    335
                )
            )
        )

    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        pantalla = self.manager.screen

        # -----------------------------------------
        # FONDO
        # -----------------------------------------

        if self.luces_encendidas:

            pantalla.fill(
                (205, 216, 201)
            )

        else:

            pantalla.fill(
                (23, 28, 38)
            )

        # -----------------------------------------
        # PANEL ELÉCTRICO
        # -----------------------------------------

        pygame.draw.rect(
            pantalla,
            (42, 49, 62),
            (
                60,
                70,
                WIDTH - 120,
                120
            ),
            border_radius=18
        )

        # -----------------------------------------
        # CABLE PRINCIPAL
        # -----------------------------------------

        pygame.draw.line(
            pantalla,
            (100, 110, 125),
            (100, 130),
            (WIDTH - 100, 130),
            5
        )

        # -----------------------------------------
        # BOMBILLAS
        # -----------------------------------------

        for i in range(5):

            x = 180 + i * 150

            if self.luces_encendidas:

                # Efecto de parpadeo
                intensidad = int(
                    210
                    + 35
                    * math.sin(
                        self.parpadeo_luz * 8
                    )
                )

                color = (
                    255,
                    intensidad,
                    100
                )

            else:

                color = (
                    70,
                    73,
                    80
                )

            pygame.draw.circle(
                pantalla,
                color,
                (x, 130),
                18
            )

        # -----------------------------------------
        # TÍTULO
        # -----------------------------------------

        titulo_color = (
            (245, 245, 245)
            if self.luces_encendidas
            else (235, 240, 245)
        )

        titulo = self.font_title.render(
            "Sistema eléctrico",
            True,
            titulo_color
        )

        pantalla.blit(
            titulo,
            (50, 25)
        )

        # -----------------------------------------
        # INSTRUCCIÓN
        # -----------------------------------------

        instruccion = self.font.render(
            "Elegí el fusible correcto para recuperar la iluminación.",
            True,
            titulo_color
        )

        pantalla.blit(
            instruccion,
            (50, 200)
        )

        # -----------------------------------------
        # FUSIBLES
        # -----------------------------------------

        for i, rect in enumerate(
            self.fusibles
        ):

            self.dibujar_fusible(
                pantalla,
                rect,
                i
            )

        # -----------------------------------------
        # ESTADÍSTICAS
        # -----------------------------------------

        estadisticas = self.font.render(
            f"Intentos: {self.intentos}/"
            f"{self.TOTAL_INTENTOS}    "
            f"Éxitos: {self.exitos}    "
            f"Fallos: {self.fallos}",
            True,
            titulo_color
        )

        pantalla.blit(
            estadisticas,
            (50, 405)
        )

        # -----------------------------------------
        # DATOS MATEMÁTICOS
        # -----------------------------------------

        probabilidad = self.calcular_binomial(
            self.exitos
        )

        matematicas = self.font_small.render(
            f"Bernoulli: éxito/fallo   |   "
            f"P(X={self.exitos}) = "
            f"{probabilidad * 100:.1f}%   |   "
            f"n=5, p=1/3",
            True,
            titulo_color
        )

        pantalla.blit(
            matematicas,
            (50, 435)
        )

        # -----------------------------------------
        # MENSAJE
        # -----------------------------------------

        mensaje_color = (
            (50, 65, 55)
            if self.luces_encendidas
            else (240, 220, 170)
        )

        mensaje = self.font.render(
            self.mensaje,
            True,
            mensaje_color
        )

        pantalla.blit(
            mensaje,
            (50, 470)
        )

        # -----------------------------------------
        # FANTASMA
        # -----------------------------------------

        self.dibujar_fantasma(
            pantalla
        )

        # -----------------------------------------
        # RESULTADO
        # -----------------------------------------

        if self.mostrar_resultado:

            self.dibujar_resultado(
                pantalla
            )