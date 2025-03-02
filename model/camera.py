# camera.py
import logging

class Camera:
    def __init__(self, pitch=0, yaw=0, roll=0, x=0, y=0, z=0):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        self.x = x
        self.y = y
        self.z = z

    def update(self, pitch=None, yaw=None, roll=None, x=None, y=None, z=None):
        if pitch is not None:
            self.pitch = self._clamp(pitch, -180, 180)
        if yaw is not None:
            self.yaw = self._clamp(yaw, -180, 180)
        if roll is not None:
            self.roll = self._clamp(roll, -180, 180)
        if x is not None:
            self.x = self._clamp(x, -100, 100)
        if y is not None:
            self.y = self._clamp(y, -100, 100)
        if z is not None:
            self.z = self._clamp(z, -100, 100)

        print(f"Camera updated: pitch={self.pitch}, yaw={self.yaw}, roll={self.roll}, x={self.x}, y={self.y}, z={self.z}")  # Debug

    def get_data(self):
        return self.pitch, self.yaw, self.roll, self.x, self.y, self.z

    def _clamp(self, value, min_val, max_val):
        return max(min(value, max_val), min_val)
