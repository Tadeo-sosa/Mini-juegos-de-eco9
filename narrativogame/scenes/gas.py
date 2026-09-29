import random
import pygame

from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene


class ValvulasScene(Scene):

    TOTAL_TURNOS = 6

    # Presión inicial
    PRESION_INICIAL = 50

    # Límites del sistema
    PRESION_MINIMA = 30
    PRESION_MAXIMA = 70

    def __init__(self, manager, state, audio):
        super().__init__(manager)

        self.state = state
        self.audio = audio

        self.presion = self.PRESION_INICIAL
        self.turno = 1

        self.valvulas = [
            {
                "nombre": "Válvula A",
                "efecto": -8,
                "abierta": False,
                "probabilidad": 0.75,
            },
            {
                "nombre": "Válvula B",
                "efecto": 8,
                "abierta": False,
                "probabilidad": 0.65,
            },
            {
                "nombre": "Válvula C",
                "efecto": -4,
                "abierta": False,
                "probabilidad": 0.80,
            },
        ]

        self.mensaje = "Selecciona una válvula para modificar la presión."
        self.color_mensaje = (245, 245, 245)

        self.decisiones = []
        self.estable = 0
        self.inestables = 0

        self.finalizado = False
        self.gano = False

        self.boton_continuar = pygame.Rect(
            WIDTH // 2 - 130,
            HEIGHT - 85,
            260,
            55
        )

    # ---------------------------------------------------------
    # PROBABILIDAD CONDICIONAL
    # ---------------------------------------------------------

    def probabilidad_condicional(self, probabilidad_evento, probabilidad_decision):
        """
        Calcula P(A|B) usando:

        P(A|B) = P(A ∩ B) / P(B)

        En este juego usamos una simplificación:
        probabilidad_evento representa P(A ∩ B)
        y probabilidad_decision representa P(B).
        """

        if probabilidad_decision <= 0:
            return 0

        resultado = probabilidad_evento / probabilidad_decision

        return max(0, min(1, resultado))

    def calcular_probabilidad_estable(self, valvula):
        """
        Calcula la probabilidad de que la presión
        permanezca estable después de elegir una válvula.
        """

        prob_base = valvula["probabilidad"]

        # Mientras más cerca estemos del centro,
        # mayor es la posibilidad de estabilidad.
        distancia = abs(self.presion - 50)

        ajuste = distancia / 100

        probabilidad = prob_base - ajuste

        return max(0.10, min(0.95, probabilidad))

    # ---------------------------------------------------------
    # CONTROL DE VÁLVULAS
    # ---------------------------------------------------------

    def seleccionar_valvula(self, indice):

        if self.finalizado:
            return

        valvula = self.valvulas[indice]

        # Alternamos el estado
        valvula["abierta"] = not valvula["abierta"]

        if valvula["abierta"]:
            self.presion += valvula["efecto"]
            accion = "abierta"
        else:
            self.presion -= valvula["efecto"]
            accion = "cerrada"

        # Limitar presión para evitar valores absurdos
        self.presion = max(0, min(100, self.presion))

        prob_estable = self.calcular_probabilidad_estable(valvula)

        evento_estable = random.random() < prob_estable

        if evento_estable:
            self.estable += 1
            self.mensaje = (
                f"{valvula['nombre']} {accion}. "
                f"La presión se mantiene estable."
            )
            self.color_mensaje = (100, 220, 140)
        else:
            self.inestables += 1
            self.mensaje = (
                f"{valvula['nombre']} {accion}. "
                f"La presión presenta una variación."
            )
            self.color_mensaje = (240, 180, 90)

        self.decisiones.append({
            "valvula": valvula["nombre"],
            "accion": accion,
            "probabilidad": prob_estable,
            "estable": evento_estable,
        })

        self.comprobar_presion()

    # ---------------------------------------------------------
    # CONTROL DEL SISTEMA
    # ---------------------------------------------------------

    def comprobar_presion(self):

        if self.presion < self.PRESION_MINIMA:
            self.finalizado = True
            self.gano = False

            self.mensaje = (
                "La presión descendió demasiado. "
                "El sistema perdió estabilidad."
            )

            self.state.set_flag("valvulas_superadas", False)

            return

        if self.presion > self.PRESION_MAXIMA:
            self.finalizado = True
            self.gano = False

            self.mensaje = (
                "La presión aumentó demasiado. "
                "El sistema perdió estabilidad."
            )

            self.state.set_flag("valvulas_superadas", False)

            return

        if self.turno >= self.TOTAL_TURNOS:
            self.finalizado = True

            # Para ganar necesitamos que la mayoría
            # de los eventos hayan sido estables.
            if self.estable >= 4:
                self.gano = True
                self.state.set_flag("valvulas_superadas", True)
                self.state.add("curiosidad", 1)

                self.mensaje = (
                    "¡Sistema estabilizado correctamente!"
                )
            else:
                self.gano = False
                self.state.set_flag("valvulas_superadas", False)

                self.mensaje = (
                    "El sistema terminó, pero tuvo demasiadas "
                    "variaciones de presión."
                )

    # ---------------------------------------------------------
    # SIGUIENTE TURNO
    # ---------------------------------------------------------

    def siguiente_turno(self):

        if self.finalizado:
            return

        self.turno += 1

        self.mensaje = (
            "Selecciona otra válvula para continuar."
        )

        self.color_mensaje = (245, 245, 245)

    # ---------------------------------------------------------
    # REINICIAR
    # ---------------------------------------------------------

    def reiniciar(self):

        self.presion = self.PRESION_INICIAL
        self.turno = 1

        self.decisiones = []
        self.estable = 0
        self.inestables = 0

        self.finalizado = False
        self.gano = False

        for valvula in self.valvulas:
            valvula["abierta"] = False

        self.mensaje = (
            "Selecciona una válvula para modificar la presión."
        )

        self.color_mensaje = (245, 245, 245)

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                self.reiniciar()
                return

            if event.key == pygame.K_SPACE and self.finalizado:
                self.reiniciar()
                return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                return

            if self.finalizado:
                return

            for i, valvula in enumerate(self.valvulas):

                rect = pygame.Rect(
                    100 + i * 280,
                    230,
                    220,
                    150
                )

                if rect.collidepoint(event.pos):
                    self.seleccionar_valvula(i)
                    return

            # Botón para avanzar al siguiente turno
            if self.turno < self.TOTAL_TURNOS:

                if self.boton_continuar.collidepoint(event.pos):
                    self.siguiente_turno()

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self, dt):
        pass

    # ---------------------------------------------------------
    # BARRA DE PRESIÓN
    # ---------------------------------------------------------

    def dibujar_presion(self, pantalla):

        x = 180
        y = 120
        ancho = 600
        alto = 30

        pygame.draw.rect(
            pantalla,
            (50, 55, 65),
            (x, y, ancho, alto)
        )

        ancho_presion = int(
            ancho * (self.presion / 100)
        )

        if self.presion < self.PRESION_MINIMA:
            color = (220, 80, 80)

        elif self.presion > self.PRESION_MAXIMA:
            color = (220, 80, 80)

        elif self.presion < 40 or self.presion > 60:
            color = (240, 190, 80)

        else:
            color = (90, 210, 130)

        pygame.draw.rect(
            pantalla,
            color,
            (x, y, ancho_presion, alto)
        )

        fuente = pygame.font.SysFont(None, 28)

        texto = fuente.render(
            f"Presión: {self.presion:.0f}%",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto,
            (WIDTH // 2 - texto.get_width() // 2, 82)
        )

    # ---------------------------------------------------------
    # ESTADÍSTICAS
    # ---------------------------------------------------------

    def dibujar_estadisticas(self, pantalla):

        fuente = pygame.font.SysFont(None, 24)

        texto = fuente.render(
            f"Eventos estables: {self.estable}    "
            f"Variaciones: {self.inestables}",
            True,
            (210, 215, 225)
        )

        pantalla.blit(
            texto,
            (
                WIDTH // 2 - texto.get_width() // 2,
                170
            )
        )

    # ---------------------------------------------------------
    # RESULTADO
    # ---------------------------------------------------------

    def dibujar_final(self, pantalla):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 210))

        pantalla.blit(overlay, (0, 0))

        fuente_titulo = pygame.font.SysFont(
            None,
            48
        )

        fuente = pygame.font.SysFont(
            None,
            28
        )

        if self.gano:

            titulo = "¡SISTEMA ESTABILIZADO!"

        else:

            titulo = "SISTEMA INESTABLE"

        texto_titulo = fuente_titulo.render(
            titulo,
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto_titulo,
            (
                WIDTH // 2 -
                texto_titulo.get_width() // 2,
                110
            )
        )

        resultado = fuente.render(
            f"Eventos estables: {self.estable}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            resultado,
            (
                WIDTH // 2 -
                resultado.get_width() // 2,
                190
            )
        )

        variaciones = fuente.render(
            f"Variaciones: {self.inestables}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            variaciones,
            (
                WIDTH // 2 -
                variaciones.get_width() // 2,
                230
            )
        )

        # Probabilidad condicional final
        if self.decisiones:

            ultima = self.decisiones[-1]

            prob = ultima["probabilidad"]

            texto_prob = fuente.render(
                f"P(estable | decisión) = "
                f"{prob * 100:.1f}%",
                True,
                (120, 220, 160)
            )

            pantalla.blit(
                texto_prob,
                (
                    WIDTH // 2 -
                    texto_prob.get_width() // 2,
                    285
                )
            )

        instruccion = fuente.render(
            "Presiona ESPACIO para volver a intentar",
            True,
            (220, 220, 220)
        )

        pantalla.blit(
            instruccion,
            (
                WIDTH // 2 -
                instruccion.get_width() // 2,
                390
            )
        )

    # ---------------------------------------------------------
    # DIBUJAR
    # ---------------------------------------------------------

    def draw(self):

        pantalla = self.manager.screen

        pantalla.fill((25, 30, 40))

        fuente_titulo = pygame.font.SysFont(
            None,
            38
        )

        fuente = pygame.font.SysFont(
            None,
            25
        )

        titulo = fuente_titulo.render(
            "CONTROL DE VÁLVULAS",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            titulo,
            (
                WIDTH // 2 -
                titulo.get_width() // 2,
                20
            )
        )

        ronda = fuente.render(
            f"Turno {self.turno}/{self.TOTAL_TURNOS}",
            True,
            (190, 195, 205)
        )

        pantalla.blit(
            ronda,
            (25, 25)
        )

        self.dibujar_presion(pantalla)
        self.dibujar_estadisticas(pantalla)

        # -----------------------------------------------------
        # VÁLVULAS
        # -----------------------------------------------------

        for i, valvula in enumerate(self.valvulas):

            rect = pygame.Rect(
                100 + i * 280,
                230,
                220,
                150
            )

            if valvula["abierta"]:
                color = (70, 150, 100)
            else:
                color = (65, 70, 85)

            pygame.draw.rect(
                pantalla,
                color,
                rect,
                border_radius=12
            )

            pygame.draw.rect(
                pantalla,
                (150, 155, 165),
                rect,
                2,
                border_radius=12
            )

            nombre = fuente.render(
                valvula["nombre"],
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                nombre,
                (
                    rect.centerx -
                    nombre.get_width() // 2,
                    rect.y + 20
                )
            )

            estado = "ABIERTA" if valvula["abierta"] else "CERRADA"

            texto_estado = fuente.render(
                estado,
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                texto_estado,
                (
                    rect.centerx -
                    texto_estado.get_width() // 2,
                    rect.y + 60
                )
            )

            efecto = fuente.render(
                f"Efecto: {valvula['efecto']:+d}",
                True,
                (210, 215, 225)
            )

            pantalla.blit(
                efecto,
                (
                    rect.centerx -
                    efecto.get_width() // 2,
                    rect.y + 100
                )
            )

        # -----------------------------------------------------
        # MENSAJE
        # -----------------------------------------------------

        mensaje = fuente.render(
            self.mensaje,
            True,
            self.color_mensaje
        )

        pantalla.blit(
            mensaje,
            (
                WIDTH // 2 -
                mensaje.get_width() // 2,
                410
            )
        )

        # -----------------------------------------------------
        # BOTÓN
        # -----------------------------------------------------

        if not self.finalizado:

            pygame.draw.rect(
                pantalla,
                (70, 75, 90),
                self.boton_continuar,
                border_radius=10
            )

            texto_boton = fuente.render(
                "SIGUIENTE TURNO",
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                texto_boton,
                (
                    self.boton_continuar.centerx -
                    texto_boton.get_width() // 2,
                    self.boton_continuar.centery -
                    texto_boton.get_height() // 2
                )
            )

        # -----------------------------------------------------
        # FINAL
        # -----------------------------------------------------

        if self.finalizado:

            self.dibujar_final(pantalla)