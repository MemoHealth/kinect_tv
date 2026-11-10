import numpy as np
import pygame


def rain_loop(sample_rate: int) -> np.ndarray:
    rng = np.random.default_rng(7)
    samples = rng.normal(size=sample_rate * 4)
    spectrum = np.fft.rfft(samples)
    frequencies = np.fft.rfftfreq(samples.size, 1 / sample_rate)
    band = (frequencies / (frequencies + 130)) / (1 + (frequencies / 900) ** 2)
    filtered = np.fft.irfft(spectrum * band, n=samples.size)
    return np.round(1700 * np.clip(filtered, -1, 1)).astype(np.int16)


class AmbientRain:
    def __init__(self) -> None:
        self._sound: pygame.mixer.Sound | None = None

    def start(self) -> None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, allowedchanges=0)
            self._sound = pygame.sndarray.make_sound(rain_loop(22050))
            self._sound.set_volume(0)
            self._sound.play(loops=-1, fade_ms=2000)
        except pygame.error:
            pygame.mixer.quit()
            self._sound = None

    def volume(self, level: float) -> None:
        if self._sound is not None:
            self._sound.set_volume(0.22 * level)

    def stop(self) -> None:
        pygame.mixer.quit()
        self._sound = None
