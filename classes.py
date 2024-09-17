import pygame
import math

WIDTH = 0
HEIGHT = 0

def setDim(h, w):
    global HEIGHT, WIDTH
    HEIGHT, WIDTH = h, w

class Entity():
    def __init__(self, x, y, v, size, sprite, type):
        self.x = x
        self.y = y
        self.size = size
        self.v = v
        self.sprite = sprite
        self.type = type

    def talk(self):
        print(self.type)

class Projectile(Entity):
    def __init__(self, x, y, v, size, sprite, vx, vy, dmg):
        self.sprite = pygame.transform.scale(sprite, (size, size))
        super().__init__(x, y, v, size, self.sprite, "projectile")
        self.vx = vx
        self.vy = vy
        self.dmg = dmg

    def update(self):
        self.x += self.vx * self.v
        self.y += self.vy * self.v

    def checkCol(self, entities, bloque):
        if self.x > WIDTH or self.x < 0:
            return True
        if self.y > HEIGHT or self.y < 0:
            return True
        if bloque:
            return True
        for e in entities:
            if e.type == "enemy":
                ex , ey = e.coords()
                if abs( ex - self.x) <= e.size and abs(ey - self.y) <= e.size:
                    e.applyDmg(self.dmg)
                    return {"hit":{"enemy": e.id, "dmg": self.dmg}}
            
    def draw(self, screen, isHost):
        self.update()
        screen.blit(self.sprite,(self.x, self.y, self.size, self.size))

class Enemy(Entity):
    def __init__(self, x, y, v, size, sprite, vida, name, id):
        super().__init__(x, y, v, size, sprite, "enemy")
        self.name = name
        self.vida = vida
        self.id = id
        self.sprite = sprite
        self.cooldown = 0
    
    def applyDmg(self, dmg):
        if self.vida > 0 and not self.cooldown:
            self.vida -= math.trunc(dmg)
            self.cooldown = 5
        print(f"id:{self.id} vida:{ self.vida}")
        
    def coords(self):
        return self.x + self.size/2, self.y + self.size/2

    def draw(self, screen, isHost):
        if isHost:
            self. x+= 1 #para pruebas, eliminar desp
            screen.blit(self.sprite,(self.x, self.y, self.size, self.size))
            return {"enemy":{"x": self.x, "y": self.y, "id": self.id}}
        if self.cooldown > 0:
            self.cooldown -= 1
        screen.blit(self.sprite,(self.x, self.y, self.size, self.size))

