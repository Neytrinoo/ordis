class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name + '(' + str(self.x) + ', ' + str(self.y) + ')'

    def __invert__(self):
        return Point(self.name, self.y, self.x)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_coords(self):
        coords = (self.x, self.y)
        return coords


class ColoredPoint(Point):
    def __init__(self, name, x, y, colors=(0, 0, 0)):
        self.colors = colors
        super().__init__(name, x, y)

    def __str__(self):
        return self.name + '(' + str(self.x) + ', ' + str(self.y) + ')'

    def __invert__(self):
        return ColoredPoint(self.name, self.y, self.x, (255 - self.colors[0],
                                                        255 - self.colors[1], 255 - self.colors[2]))

    def get_color(self):
        return self.colors

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_coords(self):
        coords = (self.x, self.y)
        return coords
