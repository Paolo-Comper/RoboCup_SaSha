class Punto:
    def __init__(self, x, y): 
        self.__x = int(x)
        self.__y = int(y)

    def getX(self):
        return self.__x
    
    def setX(self, x):
        self.__x = int(x)

    def getY(self):
        return self.__y

    def setY(self, y):
        self.__y = int(y)

    def setAll(self, x, y):
        self.__x = int(x)
        self.__y = int(y)

    def __str__(self):
        return f"Punto(x={self.__x}, y={self.__y})"