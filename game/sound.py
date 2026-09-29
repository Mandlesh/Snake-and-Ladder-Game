"""
Sound manager for Snake and Ladder.
Uses Python's built-in `winsound` on Windows for real hardware sound effects,
running on non-blocking daemon threads to prevent any UI stutter.
Gracefully handles environments without sound.
"""

import sys
import threading
import time

try:
    if sys.platform == "win32":
        import winsound
    else:
        winsound = None
except ImportError:
    winsound = None


class SoundManager:
    """Provides non-blocking audio feedback for game events."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and (winsound is not None)

    def _play_async(self, target, *args):
        if not self.enabled:
            return
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()

    def roll_dice(self):
        """Quick ticking sound for rolling dice."""
        def _sound():
            try:
                for freq in (300, 420, 560):
                    winsound.Beep(freq, 35)
                    time.sleep(0.02)
            except Exception:
                pass
        self._play_async(_sound)

    def step(self):
        """Soft pop for step movement."""
        def _sound():
            try:
                winsound.Beep(600, 30)
            except Exception:
                pass
        self._play_async(_sound)

    def ladder(self):
        """Joyful ascending fanfare for climbing ladder."""
        def _sound():
            try:
                for freq in [440, 554, 659, 880]:  # A major arpeggio
                    winsound.Beep(freq, 70)
                    time.sleep(0.015)
            except Exception:
                pass
        self._play_async(_sound)

    def snake(self):
        """Disappointing descending buzz for snake bite."""
        def _sound():
            try:
                for freq in [550, 420, 310, 200]:
                    winsound.Beep(freq, 80)
                    time.sleep(0.02)
            except Exception:
                pass
        self._play_async(_sound)

    def victory(self):
        """Celebratory victory fanfare."""
        def _sound():
            try:
                melody = [(523, 100), (659, 100), (784, 120), (1046, 350)]
                for freq, dur in melody:
                    winsound.Beep(freq, dur)
                    time.sleep(0.03)
            except Exception:
                pass
        self._play_async(_sound)
