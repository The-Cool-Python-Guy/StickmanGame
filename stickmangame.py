import tkinter
import time
import os

def resize_image(image):
    return image.zoom(10, 10).subsample(31, 31)

def image(name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, name)
    return resize_image(tkinter.PhotoImage(file=image_path))

class Coords:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def within_x(co1, co2):
    if (co1.x1 > co2.x1 and co1.x1 < co2.x2)\
        or (co1.x2 > co2.x1 and co1.x2 < co2.x2)\
        or (co2.x1 > co1.x1 and co2.x1 < co1.x2)\
        or (co2.x2 > co1.x1 and co2.x2 < co1.x2):
        return True
    else:
        return False

def within_y(co1, co2):
    if (co1.y1 > co2.y1 and co1.y1 < co2.y2)\
        or (co1.y2 > co2.y1 and co1.y2 < co2.y2)\
        or (co2.y1 > co1.y1 and co2.y1 < co1.y2)\
        or (co2.y2 > co1.y1 and co2.y2 < co1.y2):
        return True
    else:
        return False

def collided_left(co1, co2):
    if within_y(co1, co2):
        if co1.x1 >= co2.x1 and co1.x1 <= co2.x2:
            return True
    return False
def collided_right(co1, co2):
    if within_y(co1, co2):
        if co1.x2 >= co2.x1 and co1.x2 <= co2.x2:
            return True
    return False

def collided_top(co1, co2):
    if within_x(co1, co2):
        if co1.y1 >= co2.y1 and co1.y1 <= co2.y2:
            return True
    return False

def collided_bottom(y, co1, co2):
    if within_x(co1, co2):
        y_calc = co1.y2 + y
        if y_calc >= co2.y1 and y_calc <= co2.y2:
            return True
    return False

class Sprite:
    def __init__(self, game):
        self.game = game
        self.endgame = False
        self.coordinates = None
    def move(self):
        pass
    def coords(self):
        return self.coordinates

class PlatformSprite(Sprite):
    def __init__(self, game, photo_image, x, y, width, height):
        Sprite.__init__(self, game)
        self.photo_image = photo_image
        self.image = game.canvas.create_image(x, y,
                image=self.photo_image, anchor="nw")
        self.coordinates = Coords(x, y, x + width, y + height)

class StickFigureSprite(Sprite):
    def __init__(self, game):
        Sprite.__init__(self, game)
        self.images_left = [
            image("figure-l1.gif"),
            image("figure-l2.gif"),
            image("figure-l3.gif")
            ]
        self.images_right = [
            image("figure-r1.gif"),
            image("figure-r2.gif"),
            image("figure-r3.gif")
            ]
        self.image = game.canvas.create_image(200, 470,
                image=self.images_left[0], anchor="nw")
        self.x = -2
        self.y = 0
        self.current_image = 0
        self.current_image_add = 1
        self.jump_count = 0
        self.last_time = time.time()
        self.coordinates = Coords()
        game.canvas.bind_all("<KeyPress-Left>", self.turn_left)
        game.canvas.bind_all("<a>", self.turn_left)
        game.canvas.bind_all("<KeyPress-Right>", self.turn_right)
        game.canvas.bind_all("<d>", self.turn_right)
        game.canvas.bind_all("<space>", self.jump)
        game.canvas.bind_all("<KeyPress-Up>", self.jump)
        game.canvas.bind_all("<w>", self.jump)
    def turn_left(self, evt):
        if self.y == 0:
            self.x = -2
    def turn_right(self, evt):
        if self.y == 0:
            self.x = 2
    def jump(self, evt):
        if self.y == 0:
            self.y = -4
            self.jump_count = 0
    def animate(self):
        if self.x != 0 and self.y == 0:
            if time.time() - self.last_time > 0.1:
                self.last_time = time.time()
                self.current_image += self.current_image_add
                if self.current_image >= 2:
                    self.current_image_add = -1
                if self.current_image <= 0:
                    self.current_image_add = 1
        if self.x < 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image,
                        image=self.images_left[2])
            else:
                self.game.canvas.itemconfig(self.image,
                        image=self.images_left[self.current_image])
        elif self.x > 0:
            if self.y != 0:
                self.game.canvas.itemconfig(self.image,
                        image=self.images_right[2])
            else:
                self.game.canvas.itemconfig(self.image,
                        image=self.images_right[self.current_image])
    def coords(self):
        xy = self.game.canvas.coords(self.image)
        self.coordinates.x1 = xy[0]
        self.coordinates.y1 = xy[1]
        self.coordinates.x2 = xy[0] + 27
        self.coordinates.y2 = xy[1] + 30
        return self.coordinates
    def move(self):
        self.animate()
        if self.y < 0:
            self.jump_count += 1
            if self.jump_count > 20:
                self.y = 4
        if self.y > 0:
            self.jump_count -= 1
        co = self.coords()
        left = True
        right = True
        top = True
        bottom = True
        falling = True
        if self.y > 0 and co.y2 >= self.game.canvas_height:
            self.y = 0
            bottom = False
        elif self.y < 0 and co.y1 <= 0:
            self.y = 0
            top = False
        if self.x > 0 and co.x2 >= self.game.canvas_width:
            self.x = 0
            right = False
        elif self.x < 0 and co.x1 <= 0:
            self.x = 0
            left = False
        for sprite in self.game.sprites:
            if sprite == self:
                continue
            sprite_co = sprite.coords()
            if top and self.y < 0 and collided_top(co, sprite_co):
                self.y = -self.y
                top = False
            if bottom and self.y > 0 and collided_bottom(self.y,
                    co, sprite_co):
                self.y = sprite_co.y1 - co.y2
                if self.y < 0:
                    self.y = 0
                bottom = False
                top = False
            if bottom and falling and self.y == 0 \
                    and co.y2 < self.game.canvas_height \
                    and collided_bottom(1, co, sprite_co):
                falling = False
            if left and self.x < 0 and collided_left(co, sprite_co):
                self.x = 0
                left = False
                if sprite.endgame:
                    self.game.running = 1
            if right and self.x > 0 and collided_right(co, sprite_co):
                self.x = 0
                right = False
                if sprite.endgame:
                    self.game.running = 1
        if falling and bottom and self.y == 0 \
                and co.y2 < self.game.canvas_height:
            self.y = 4
        self.game.canvas.move(self.image, self.x, self.y)
    def hide(self):
        self.game.canvas.itemconfig(self.image, state="hidden")

class DoorSprite(Sprite):
    def __init__(self, game, x, y, width, height):
        Sprite.__init__(self, game)
        self.closed_image = image("door1.gif")
        self.opened_image = image("door2.gif")
        self.image = game.canvas.create_image(x, y,
                image=self.closed_image, anchor="nw")
        self.coordinates = Coords(x, y, x + (width/2), y + height)
        self.endgame = True
    def opendoor(self):
        self.game.canvas.itemconfig(self.image, image=self.opened_image)
    def closedoor(self):
        self.game.canvas.itemconfig(self.image, image=self.closed_image)

class Game:
    def __init__(self):
        self.tk = tkinter.Tk()
        self.tk.title("Mr. Stickman Races for the Exit")
        self.tk.resizable(0, 0)
        self.tk.wm_attributes("-topmost", 1)
        self.canvas = tkinter.Canvas(self.tk, width=500, height=500, highlightthickness=0)
        
        self.canvas.pack()
        self.tk.update()
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.bg = image("background2.gif")
        w = self.bg.width()
        h = self.bg.height()
        for x in range(0, 5):
            for y in range(0, 5):
                self.canvas.create_image(x * w, y * h, image=self.bg, anchor="nw")
        self.sprites = []
        self.running = -1

    def mainloop(self):
        self.start_text = self.canvas.create_text(250, 250, text="Click to Start", font=("Impact", 30), fill="lime")
        self.canvas.bind_all("<Button-1>", self.start)
        while True:
            if self.running == 0:
                for sprite in self.sprites:
                    sprite.move()
            elif self.running == 1:
                door.opendoor()
                self.running = 2
                time.sleep(0.5)
            elif self.running == 2:
                sf.hide()
                self.running = 3
                time.sleep(0.5)
            elif self.running == 3:
                door.closedoor()
                self.running = 4
                time.sleep(0.5)
            elif self.running == 4:
                time.sleep(0.5)
                break
            self.tk.update_idletasks()
            self.tk.update()
            time.sleep(0.01)
    def start(self, evt):
        self.running = 0
        self.canvas.delete(self.start_text)

g = Game()
platform1 = PlatformSprite(g, image("platform1.gif"),
                           0, 480, 100, 10)
platform2 = PlatformSprite(g, image("platform1.gif"),
                           150, 440, 100, 10)
platform3 = PlatformSprite(g, image("platform1.gif"),
                           300, 400, 100, 10)
platform4 = PlatformSprite(g, image("platform1.gif"),
                           300, 160, 100, 10)
platform5 = PlatformSprite(g, image("platform2.gif"),
                           175, 350, 66, 10)
platform6 = PlatformSprite(g, image("platform2.gif"),
                           50, 300, 66, 10)
platform7 = PlatformSprite(g, image("platform2.gif"),
                           170, 120, 66, 10)
platform8 = PlatformSprite(g, image("platform2.gif"),
                           45, 60, 66, 10)
platform9 = PlatformSprite(g, image("platform3.gif"),
                           170, 250, 32, 10)
platform10 = PlatformSprite(g, image("platform3.gif"),
                           230, 200, 32, 10)

g.sprites.append(platform1)
g.sprites.append(platform2)
g.sprites.append(platform3)
g.sprites.append(platform4)
g.sprites.append(platform5) 
g.sprites.append(platform6)
g.sprites.append(platform7)
g.sprites.append(platform8)
g.sprites.append(platform9)
g.sprites.append(platform10)

door = DoorSprite(g, 45, 30, 40, 35)
g.sprites.append(door)

sf = StickFigureSprite(g)
g.sprites.append(sf)

g.mainloop()