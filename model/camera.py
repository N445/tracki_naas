# model/camera.py
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
            self.pitch = pitch
        if yaw is not None:
            self.yaw = yaw
        if roll is not None:
            self.roll = roll
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z

    def get_data(self):
        return self.pitch, self.yaw, self.roll, self.x, self.y, self.z
