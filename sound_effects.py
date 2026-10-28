"""
Módulo de Gestión de Audio (Efectos de Sonido y Música de Fondo) para el Memotest.
Permite reproducir música de fondo en bucle (menú y juego principal), efectos de sonido
desde archivos MP3 (acierto y fallo) y efectos procedimentales (flip, inválido, victoria, derrota).
Incluye control completo de volumen y silenciamiento (mute).
"""

import io
import math
import os
import struct
import wave
from typing import Dict, Optional
import pygame


def find_audio_file(filename: str) -> Optional[str]:
    """Busca un archivo de audio tanto en assets/musica como directamente en assets."""
    candidates = [
        os.path.join("assets", "musica", filename),
        os.path.join("assets", filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


class SoundManager:
    """Manejador integral de música y efectos de sonido."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.music_volume: float = 0.5  # 0.0 a 1.0
        self.sfx_volume: float = 0.7    # 0.0 a 1.0
        self.music_muted: bool = False
        self.sfx_muted: bool = False

        self.current_track: Optional[str] = None  # 'menu', 'game', o None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        self.menu_music_path = find_audio_file("menu_principal.mp3")
        self.game_music_path = find_audio_file("juego_principal.mp3")

        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._generate_sounds()
            self._load_mp3_sounds()
            self._apply_volumes()
        except Exception as e:
            print(f"Aviso: No se pudo inicializar el sistema de audio: {e}")
            self.enabled = False

    def _load_mp3_sounds(self):
        """Carga los efectos de sonido provistos en MP3."""
        if not self.enabled:
            return

        # 1. Acierto
        path_acierto = find_audio_file("acierto.mp3")
        if path_acierto:
            try:
                self.sounds["match"] = pygame.mixer.Sound(path_acierto)
                self.sounds["acierto"] = self.sounds["match"]
            except Exception as e:
                print(f"Error cargando acierto.mp3: {e}")

        # 2. Fallo
        path_fallo = find_audio_file("fallo.mp3")
        if path_fallo:
            try:
                self.sounds["error"] = pygame.mixer.Sound(path_fallo)
                self.sounds["fallo"] = self.sounds["error"]
            except Exception as e:
                print(f"Error cargando fallo.mp3: {e}")

    def _create_wav_sound(self, generator_fn, duration: float, volume: float = 0.3) -> pygame.mixer.Sound:
        rate = 44100
        n_samples = int(rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            data = bytearray()
            for i in range(n_samples):
                t = i / rate
                raw_val = generator_fn(t, duration)
                clamped = max(-1.0, min(1.0, raw_val * volume))
                int_val = int(clamped * 32767)
                data.extend(struct.pack("<h", int_val))
            wf.writeframes(data)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _generate_sounds(self):
        """Genera efectos procedurales para complementar el juego (flip, inválido, fin)."""
        if not self.enabled:
            return

        try:
            # Flip de carta (click percusivo)
            def flip_gen(t, dur):
                decay = math.exp(-25 * t)
                f = 700 - 300 * (t / dur)
                return math.sin(2 * math.pi * f * t) * decay

            self.sounds["flip"] = self._create_wav_sound(flip_gen, duration=0.08, volume=0.25)

            # Jugada Inválida ('x'): doble chasquido
            def invalid_gen(t, dur):
                decay = math.exp(-30 * (t % 0.06))
                return math.sin(2 * math.pi * 380 * t) * decay

            self.sounds["invalid"] = self._create_wav_sound(invalid_gen, duration=0.12, volume=0.25)

            # Victoria (fanfarria)
            def win_gen(t, dur):
                notes = [523.25, 659.25, 783.99, 1046.50]
                idx = min(3, int(t / 0.12))
                freq = notes[idx]
                note_t = t - (idx * 0.12)
                decay = math.exp(-4 * note_t)
                return math.sin(2 * math.pi * freq * note_t) * decay

            self.sounds["win"] = self._create_wav_sound(win_gen, duration=0.6, volume=0.35)

            # Derrota (secuencia descendente)
            def lose_gen(t, dur):
                notes = [392.00, 349.23, 293.66, 220.00]
                idx = min(3, int(t / 0.15))
                freq = notes[idx]
                note_t = t - (idx * 0.15)
                decay = math.exp(-5 * note_t)
                return math.sin(2 * math.pi * freq * note_t) * decay

            self.sounds["lose"] = self._create_wav_sound(lose_gen, duration=0.7, volume=0.35)

        except Exception:
            pass

    def _apply_volumes(self):
        """Aplica los volúmenes configurados a la música y a cada efecto de sonido."""
        if not self.enabled:
            return

        # Volumen de música
        effective_music_vol = 0.0 if self.music_muted else self.music_volume
        try:
            pygame.mixer.music.set_volume(effective_music_vol)
        except Exception:
            pass

        # Volumen de efectos
        effective_sfx_vol = 0.0 if self.sfx_muted else self.sfx_volume
        for snd in self.sounds.values():
            try:
                snd.set_volume(effective_sfx_vol)
            except Exception:
                pass

    # ==================== CONTROL DE MÚSICA ====================

    def play_menu_music(self):
        """Inicia la reproducción de la música del menú principal."""
        if not self.enabled or not self.menu_music_path:
            return

        if self.current_track == "menu" and pygame.mixer.music.get_busy():
            return  # Ya está sonando

        try:
            pygame.mixer.music.load(self.menu_music_path)
            self._apply_volumes()
            pygame.mixer.music.play(-1)  # Bucle infinito
            self.current_track = "menu"
        except Exception as e:
            print(f"Error reproduciendo menu_principal.mp3: {e}")

    def play_game_music(self):
        """Inicia la reproducción de la música durante la partida."""
        if not self.enabled or not self.game_music_path:
            return

        if self.current_track == "game" and pygame.mixer.music.get_busy():
            return  # Ya está sonando

        try:
            pygame.mixer.music.load(self.game_music_path)
            self._apply_volumes()
            pygame.mixer.music.play(-1)  # Bucle infinito
            self.current_track = "game"
        except Exception as e:
            print(f"Error reproduciendo juego_principal.mp3: {e}")

    def stop_music(self):
        """Detiene la música de fondo."""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
            self.current_track = None
        except Exception:
            pass

    def set_music_volume(self, vol: float):
        """Establece el volumen de música (0.0 a 1.0)."""
        self.music_volume = max(0.0, min(1.0, round(vol, 2)))
        self._apply_volumes()

    def set_sfx_volume(self, vol: float):
        """Establece el volumen de efectos de sonido (0.0 a 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, round(vol, 2)))
        self._apply_volumes()

    def change_music_volume(self, delta: float):
        """Aumenta o disminuye el volumen de música en un paso (ej: +0.1 o -0.1)."""
        new_vol = self.music_volume + delta
        self.set_music_volume(new_vol)
        if self.music_muted and delta > 0:
            self.music_muted = False
            self._apply_volumes()

    def change_sfx_volume(self, delta: float):
        """Aumenta o disminuye el volumen de efectos en un paso."""
        new_vol = self.sfx_volume + delta
        self.set_sfx_volume(new_vol)
        if self.sfx_muted and delta > 0:
            self.sfx_muted = False
            self._apply_volumes()

    def toggle_music_mute(self) -> bool:
        """Alterna el silencio de la música."""
        self.music_muted = not self.music_muted
        self._apply_volumes()
        return self.music_muted

    def toggle_sfx_mute(self) -> bool:
        """Alterna el silencio de los efectos de sonido."""
        self.sfx_muted = not self.sfx_muted
        self._apply_volumes()
        return self.sfx_muted

    # ==================== CONTROL DE EFECTOS (SFX) ====================

    def play(self, sound_name: str):
        """Reproduce un efecto de sonido si no está silenciado."""
        if not self.enabled or self.sfx_muted:
            return

        snd = self.sounds.get(sound_name)
        if snd:
            try:
                # Si es un fallo largo anterior, podemos detenerlo para que no se superpongan
                if sound_name in {"error", "fallo"}:
                    snd.stop()
                snd.play()
            except Exception:
                pass
