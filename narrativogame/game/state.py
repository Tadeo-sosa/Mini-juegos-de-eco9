class GameState:
    """Estado global del juego: estadísticas que afectan la historia."""
    def __init__(self):
        self.stats = {
            "bondad": 0,
            "curiosidad": 0,
        }
        self.flags = {
            "vio_mariposa": False,
        }

    def add(self, key, value=1):
        self.stats[key] = self.stats.get(key, 0) + value

    def set_flag(self, key, value=True):
        self.flags[key] = value