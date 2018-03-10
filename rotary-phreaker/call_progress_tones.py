#!/usr/bin/env python3

import pyaudio
import numpy as np
from abc import ABC, abstractmethod


class Tone:
    def __init__(self, frequency, duration, volume):
        self.fs = 44100  # sampling rate, Hz, must be integer
        self.frequency = frequency
        self.duration = duration
        self.volume = volume

    def gen_samples(self):
        # generate samples, note conversion to float32 array
        return (np.sin(2 * np.pi * np.arange(self.fs * self.duration)
                       * self.frequency / self.fs)).astype(np.float32) * self.volume

    def play(self):
        p = pyaudio.PyAudio()
        samples = self.gen_samples()

        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=self.fs,
                        output=True)

        # play. May repeat with different volume values (if done interactively)
        stream.write(samples.tobytes())

        stream.stop_stream()
        stream.close()

        p.terminate()


class Silence(Tone):
    def __init__(self, duration):
        super().__init__(0, duration, 0)


class CallProgressTone(ABC):
    """Represent an abstract skeleton for call progress tones.

    Follow the definition in the
    "Technische Beschreibung der analogen Wählanschlüsse am T-Net/ISDN der T-Com (1TR110-1)"."""
    @abstractmethod
    def __init__(self, new_patterns):
        self.patterns = new_patterns

    def _first(self):
        res = []
        for tone in self.patterns[0]:
            res.append(tone.gen_samples())
        return res

    def _second(self):
        res = []
        for tone in self.patterns[-1]:
            res.append(tone.gen_samples())
        return res

    def play_endlessly(self):
        p = pyaudio.PyAudio()
        fs = 44100  # sampling rate, Hz, must be integer
        #  for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)

        fl = self._first()
        sl = self._second()

        for sample in fl:
            stream.write(sample.tobytes())

        # fixme replace the outer for loop with something like self.run and let the class inherit from Thread
        for i in range(15):
            for sample in sl:
                stream.write(sample.tobytes())

        stream.stop_stream()
        stream.close()

        p.terminate()


class Waehlton(CallProgressTone):
    """1 TR 110-1, Kap. 8.1"""
    def __init__(self):
        super().__init__([[Tone(425, 1, 1.0)]])


class Freiton(CallProgressTone):
    """1 TR 110-1, Kap. 8.3"""
    def __init__(self):
        super().__init__([[Tone(425, 1, 1.0), Silence(4)]])


class Teilnehmerbesetztton(CallProgressTone):
    """1 TR 110-1, Kap. 8.4"""
    def __init__(self):
        super().__init__([[Tone(425, 0.48, 1.0), Silence(0.48)]])


class Gassenbesetztton(CallProgressTone):
    """1 TR 110-1, Kap. 8.5"""
    def __init__(self):
        super().__init__([[Tone(425, 0.24, 1.0), Silence(0.24)]])


class Aufschaltzeichen(CallProgressTone):
    """1 TR 110-1, Kap. 8.6"""
    def __init__(self):
        super().__init__([[Tone(425, 0.24, 1.0), Silence(0.24), Tone(425, 0.24, 1.0), Silence(1.28)]])


class Anklopfton(CallProgressTone):
    """1 TR 110-1, Kap. 8.7"""
    def __init__(self):
        super().__init__([[Tone(425, 0.2, 1.0), Silence(0.2), Tone(425, 0.2, 1.0), Silence(1)],
                          [Tone(425, 0.2, 1.0), Silence(0.2), Tone(425, 0.2, 1.0), Silence(5)]])


class Hinweiston(CallProgressTone):
    """1 TR 110-1, Kap. 8.8"""
    def __init__(self):
        super().__init__([[Tone(950, 0.33, 0.3), Tone(1400, 0.33, 0.3), Tone(1800, 0.33, 0.3), Silence(1)]])