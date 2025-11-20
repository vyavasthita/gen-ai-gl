import numpy as np
import av

class AudioBuffer:
    def __init__(self):
        self.frames = []
        self.sample_rate = None

    def add_frame(self, frame: av.AudioFrame):
        if self.sample_rate is None:
            self.sample_rate = frame.sample_rate
        pcm = frame.to_ndarray().flatten().astype(np.float32) / 32768.0
        self.frames.append(pcm)

    def get_audio(self):
        if not self.frames:
            return None, self.sample_rate
        return np.concatenate(self.frames), self.sample_rate

    def reset(self):
        self.frames = []
        self.sample_rate = None
