class PuntoReal:
    def __init__(self, tupla):
        self.__x = float(tupla[0])
        self.__y = float(tupla[1])

    def getX(self):
        return self.__x
    
    def setX(self, x):
        self.__x = float(x)

    def getY(self):
        return self.__y

    def setY(self, y):
        self.__y = float(y)

    def setAll(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    def __str__(self):
        return f"PuntoReal(x={self.__x}, y={self.__y})"