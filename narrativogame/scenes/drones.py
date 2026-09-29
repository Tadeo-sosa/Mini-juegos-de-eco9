import math
import random
import pygame

from settings import WIDTH, HEIGHT, PALETTE
from engine.scene_manager import Scene
from scenes.ending import EndingScene
from scenes.valvulas import ValvulasScene

class DronesScene(Scene):
    """
    Minijuego 2:
    Control de drones autodestructivos.

    Conceptos matemáticos:
    - Ensayos de Bernoulli:
        cada intento de interceptación tiene éxito o fracaso.
    - Distribución binomial:
        contamos cuántos éxitos obtenemos en varias intercepciones.
    - Distribución binomial acumulada:
        calculamos P(X >= k).
    """

    TOTAL_RONDAS = 4
    DRONES_POR_RONDA = 3

    # Probabilidad de interceptar correctamente un drone.
    PROBABILIDAD_EXITO = 0.70

    # Cantidad de intercepciones exitosas necesarias.
    EXITOS_NECESARIOS = 7

    def __init__(self, manager, state, audio):
        super().__init__(manager)

        self.state = state
        self.audio = audio

        self.ronda = 1
        self.drones = []

        self.exitos = 0
        self.fracasos = 0
        self.intentos = 0

        self.mensaje = "¡Los drones están entrando!"
        self.color_mensaje = (245, 245, 245)

        self.finalizado = False
        self.gano = False

        self.crear_drones()

    # ---------------------------------------------------------
    # MATEMÁTICA
    # ---------------------------------------------------------

    def combinacion(self, n, k):
        if k < 0 or k > n:
            return 0

        return math.comb(n, k)

    def probabilidad_binomial(self, n, k, p):
        """
        P(X = k)

        X = cantidad de éxitos.
        n = cantidad de intentos.
        k = éxitos deseados.
        p = probabilidad de éxito.
        """

        return (
            self.combinacion(n, k)
            * (p ** k)
            * ((1 - p) ** (n - k))
        )

    def probabilidad_acumulada(self, n, k, p):
        """
        Calcula:

            P(X >= k)

        Es decir, la probabilidad de obtener
        al menos k éxitos.
        """

        resultado = 0

        for x in range(k, n + 1):
            resultado += self.probabilidad_binomial(n, x, p)

        return resultado

    # ---------------------------------------------------------
    # DRONES
    # ---------------------------------------------------------

    def crear_drones(self):
        self.drones = []

        ancho = 150
        espacio = 40

        inicio_x = (
            WIDTH
            - (
                self.DRONES_POR_RONDA * ancho
                + (self.DRONES_POR_RONDA - 1) * espacio
            )
        ) // 2

        for i in range(self.DRONES_POR_RONDA):
            x = inicio_x + i * (ancho + espacio)

            rect = pygame.Rect(
                x,
                190,
                ancho,
                100
            )

            self.drones.append({
                "rect": rect,
                "activo": True,
                "resultado": None
            })

    # ---------------------------------------------------------
    # INTERCEPCIÓN
    # ---------------------------------------------------------

    def interceptar_drone(self, indice):
        if self.finalizado:
            return

        if indice < 0 or indice >= len(self.drones):
            return

        drone = self.drones[indice]

        # Si ya fue interceptado, no hacemos nada.
        if not drone["activo"]:
            return

        drone["activo"] = False
        self.intentos += 1

        # Ensayo de Bernoulli.
        exito = random.random() < self.PROBABILIDAD_EXITO

        if exito:
            self.exitos += 1
            drone["resultado"] = "exito"

            self.mensaje = "¡Intercepción exitosa!"
            self.color_mensaje = (80, 220, 120)

        else:
            self.fracasos += 1
            drone["resultado"] = "fracaso"

            self.mensaje = "¡Fallo! El drone escapó."
            self.color_mensaje = (230, 90, 90)

        self.comprobar_estado()

    # ---------------------------------------------------------
    # ESTADO DEL JUEGO
    # ---------------------------------------------------------

    def comprobar_estado(self):

        # ¿Ya consiguió suficientes éxitos?
        if self.exitos >= self.EXITOS_NECESARIOS:
            self.finalizado = True
            self.gano = True

            self.mensaje = (
                "¡Excelente! Controlaste la amenaza."
            )

            self.state.add(
                "drones_interceptados",
                self.exitos
            )

            self.state.add(
                "drones_fallidos",
                self.fracasos
            )

            self.state.set_flag(
                "drones_controlados",
                True
            )

            return

        # Si todos los drones de la ronda fueron utilizados.
        todos_usados = all(
            not drone["activo"]
            for drone in self.drones
        )

        if todos_usados:

            if self.ronda >= self.TOTAL_RONDAS:

                self.finalizado = True
                self.gano = False

                self.mensaje = (
                    "Demasiados drones escaparon."
                )

                self.state.add(
                    "drones_interceptados",
                    self.exitos
                )

                self.state.add(
                    "drones_fallidos",
                    self.fracasos
                )

                self.state.set_flag(
                    "drones_controlados",
                    False
                )

            else:
                self.ronda += 1
                self.crear_drones()

                self.mensaje = (
                    f"Ronda {self.ronda}: "
                    "¡nuevos drones detectados!"
                )

    # ---------------------------------------------------------
    # REINICIO
    # ---------------------------------------------------------

    def reiniciar(self):
        self.ronda = 1

        self.exitos = 0
        self.fracasos = 0
        self.intentos = 0

        self.finalizado = False
        self.gano = False

        self.mensaje = "¡Los drones están entrando!"
        self.color_mensaje = (245, 245, 245)

        self.crear_drones()

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                self.reiniciar()
            
            if event.key == pygame.K_SPACE and self.finalizado:
               return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                pantalla.fill((25, 30, 40))

            if self.finalizado:
                return

            for i, drone in enumerate(self.drones):

                if drone["rect"].collidepoint(event.pos):
                    self.interceptar_drone(i)
                    break

    # ---------------------------------------------------------
    # ACTUALIZACIÓN
    # ---------------------------------------------------------

    def update(self, dt):
        pass

    # ---------------------------------------------------------
    # DIBUJAR DRONE
    # ---------------------------------------------------------

    def dibujar_drone(self, pantalla, drone, numero):

        rect = drone["rect"]

        if not drone["activo"]:

            if drone["resultado"] == "exito":
                color = (70, 180, 100)
            else:
                color = (190, 70, 70)

        else:
            color = (70, 100, 150)

        pygame.draw.rect(
            pantalla,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            pantalla,
            (245, 245, 245),
            rect,
            2,
            border_radius=12
        )

        # Cuerpo del drone.
        centro_x = rect.centerx
        centro_y = rect.centery

        pygame.draw.circle(
            pantalla,
            (245, 245, 245),
            (centro_x, centro_y),
            18
        )

        # Hélices.
        pygame.draw.line(
            pantalla,
            (245, 245, 245),
            (centro_x - 40, centro_y - 25),
            (centro_x - 10, centro_y),
            4
        )

        pygame.draw.line(
            pantalla,
            (245, 245, 245),
            (centro_x + 40, centro_y - 25),
            (centro_x + 10, centro_y),
            4
        )

        pygame.draw.line(
            pantalla,
            (245, 245, 245),
            (centro_x - 40, centro_y + 25),
            (centro_x - 10, centro_y),
            4
        )

        pygame.draw.line(
            pantalla,
            (245, 245, 245),
            (centro_x + 40, centro_y + 25),
            (centro_x + 10, centro_y),
            4
        )

        texto = pygame.font.Font(None, 30).render(
            f"DRONE {numero + 1}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto,
            (
                rect.centerx - texto.get_width() // 2,
                rect.bottom + 12
            )
        )

    # ---------------------------------------------------------
    # RESULTADO MATEMÁTICO
    # ---------------------------------------------------------

    def dibujar_estadisticas(self, pantalla):

        n = self.intentos
        p = self.PROBABILIDAD_EXITO

        if n > 0:

            probabilidad = self.probabilidad_acumulada(
                n,
                min(self.EXITOS_NECESARIOS, n),
                p
            )

        else:
            probabilidad = 0

        fuente = pygame.font.Font(None, 26)

        textos = [
            f"Intentos: {self.intentos}",
            f"Éxitos: {self.exitos}",
            f"Fallos: {self.fracasos}",
            f"Prob. de éxito por intento: {p * 100:.0f}%"
        ]

        if n > 0:
            textos.append(
                f"P(X >= {min(self.EXITOS_NECESARIOS, n)}): "
                f"{probabilidad * 100:.1f}%"
            )

        y = 380

        for texto in textos:

            superficie = fuente.render(
                texto,
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                superficie,
                (60, y)
            )

            y += 28

    # ---------------------------------------------------------
    # PANTALLA FINAL
    # ---------------------------------------------------------

    def dibujar_final(self, pantalla):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 190))

        pantalla.blit(
            overlay,
            (0, 0)
        )

        fuente_grande = pygame.font.Font(None, 54)
        fuente = pygame.font.Font(None, 30)

        if self.gano:
            titulo = "¡DRONES CONTROLADOS!"
        else:
            titulo = "MISIÓN FALLIDA"

        texto_titulo = fuente_grande.render(
            titulo,
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            texto_titulo,
            (
                WIDTH // 2
                - texto_titulo.get_width() // 2,
                150
            )
        )

        resultado = fuente.render(
            f"Éxitos: {self.exitos}    "
            f"Fallos: {self.fracasos}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            resultado,
            (
                WIDTH // 2
                - resultado.get_width() // 2,
                225
            )
        )

        if self.gano:

            prob = self.probabilidad_acumulada(
                self.TOTAL_RONDAS * self.DRONES_POR_RONDA,
                self.EXITOS_NECESARIOS,
                self.PROBABILIDAD_EXITO
            )

            texto_prob = fuente.render(
                f"P(X >= {self.EXITOS_NECESARIOS}) "
                f"teórica: {prob * 100:.1f}%",
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                texto_prob,
                (
                    WIDTH // 2
                    - texto_prob.get_width() // 2,
                    270
                )
            )

            continuar = fuente.render(
                "Presiona ESPACIO para continuar",
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                continuar,
                (
                    WIDTH // 2
                    - continuar.get_width() // 2,
                    330
                )
            )

        else:

            reinicio = fuente.render(
                "Presiona R para intentar nuevamente",
                True,
                (245, 245, 245)
            )

            pantalla.blit(
                reinicio,
                (
                    WIDTH // 2
                    - reinicio.get_width() // 2,
                    330
                )
            )

    # ---------------------------------------------------------
    # DIBUJAR
    # ---------------------------------------------------------

    def draw(self):

        pantalla = self.manager.screen

        pantalla.fill(
            (245, 245, 245)
        )

        fuente_titulo = pygame.font.Font(None, 46)
        fuente = pygame.font.Font(None, 28)

        titulo = fuente_titulo.render(
            "CONTROL DE DRONES",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            titulo,
            (
                WIDTH // 2 - titulo.get_width() // 2,
                40
            )
        )

        ronda = fuente.render(
            f"Ronda {self.ronda}/{self.TOTAL_RONDAS}",
            True,
            (245, 245, 245)
        )

        pantalla.blit(
            ronda,
            (60, 110)
        )

        mensaje = fuente.render(
            self.mensaje,
            True,
            self.color_mensaje
        )

        pantalla.blit(
            mensaje,
            (
                WIDTH // 2 - mensaje.get_width() // 2,
                120
            )
        )

        for i, drone in enumerate(self.drones):
            self.dibujar_drone(
                pantalla,
                drone,
                i
            )

        self.dibujar_estadisticas(
            pantalla
        )

        if self.finalizado:
            self.dibujar_final(
                pantalla
            )