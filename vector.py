import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y)

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def scale(self, scalar):
        return Vector(self.x*scalar, self.y*scalar)

    def dot(self, other):
        return self.x*other.x + self.y*other.y

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    def angle(self):
        return math.atan2(self.y, self.x)

    def turn(self, dtheta):
        dtheta = self.angle() + dtheta
        self.x = self.x*math.cos(dtheta)
        self.y = self.y*math.sin(dtheta)

    def normalise(self):
        self.x /= self.mag()
        self.y /= self.mag()




