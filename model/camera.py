# model/camera.py
import logging

class Camera:
    def __init__(self, pitch=0, yaw=0, roll=0, x=0, y=0, z=0):
        self._pitch = 0
        self._yaw = 0
        self._roll = 0
        self._x = 0
        self._y = 0
        self._z = 0
        self.update(pitch, yaw, roll, x, y, z)

    def update(self, pitch=None, yaw=None, roll=None, x=None, y=None, z=None):
        if pitch is not None:
            self._pitch = round(self._clamp(pitch, -180, 180), 2)
        if yaw is not None:
            self._yaw = round(self._clamp(yaw, -180, 180), 2)
        if roll is not None:
            self._roll = round(self._clamp(roll, -180, 180), 2)
        if x is not None:
            self._x = round(self._clamp(x, -100, 100), 2)
        if y is not None:
            self._y = round(self._clamp(y, -100, 100), 2)
        if z is not None:
            self._z = round(self._clamp(z, -100, 100), 2)

        logging.debug(f"Update Camera : {self}")

    def get_data(self):
        return self._pitch, self._yaw, self._roll, self._x, self._y, self._z

    def _clamp(self, value, min_val, max_val):
        return max(min(value, max_val), min_val)

    def __getattr__(self, attr):
        return getattr(self, f"_{attr}")

    def __setattr__(self, attr, value):
        if attr in {"_pitch", "_yaw", "_roll"}:
            value = self._clamp(value, -180, 180)
        elif attr in {"_x", "_y", "_z"}:
            value = self._clamp(value, -100, 100)
        super().__setattr__(attr, round(value, 2))
