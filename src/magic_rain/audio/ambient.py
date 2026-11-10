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
        self._channel: pygame.mixer.Channel | None = None

    def start(self) -> None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, allowedchanges=0)
            sound = pygame.sndarray.make_sound(rain_loop(22050))
            sound.set_volume(0.22)
            self._channel = sound.play(loops=-1, fade_ms=2000)
        except pygame.error:
            pygame.mixer.quit()

    def volume(self, level: float) -> None:
        if self._channel is not None:
            self._channel.set_volume(level)

    def stop(self) -> None:
        pygame.mixer.quit()
        self._channel = None
