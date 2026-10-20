"""Small, deliberate 2.5D deformations in source coordinates."""
import math

import cv2
import numpy as np


def ease(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def oval(x, y, cx, cy, rx, ry):
    return np.exp(-2 * (((x-cx)/rx)**2 + ((y-cy)/ry)**2))


class Scene:
    def __init__(self, asset, path, size):
        self.asset = asset
        self.image = cv2.imread(str(path))
        if self.image is None:
            raise FileNotFoundError(path)
        self.height, self.width = self.image.shape[:2]
        self.outsize = size
        self.x, self.y = np.meshgrid(np.linspace(0, 1, 480, dtype=np.float32),
                                     np.linspace(0, 1, 270, dtype=np.float32))
        self.rng = np.random.default_rng(190102126)
        self.particles = self.rng.random((70, 4))

    def draw(self, camera, t, progress, energy):
        cx, cy, zoom = camera
        x = (self.x-.5)/zoom + cx
        y = (self.y-.5)/zoom + cy
        dx = np.zeros_like(x)
        dy = np.zeros_like(y)
        breathe = math.sin(t*1.2)
        drift = math.sin(t*.16)
        # Differential travel creates depth rather than a uniform still-image pan.
        depth = .22*y
        if self.asset in ("room", "reunion"):
            father = oval(x, y, .23, .36, .24, .33)
            daughter = oval(x, y, .76, .39, .22, .32)
            depth += .50*(father + daughter) + .15*ease((y-.55)/.3)
            dy += .0018*breathe*father + .0015*math.sin(t*1.1+.8)*daughter
            if self.asset == "reunion":
                # The offering and receiving hands move gently towards each other.
                reach = ease(progress)
                dx -= .008*reach*oval(x, y, .425, .46, .15, .12)
                dx += .006*reach*oval(x, y, .535, .48, .13, .10)
        elif self.asset == "window":
            depth += .60*oval(x, y, .27, .54, .36, .65)
            curtain = oval(x, y, .48, .30, .085, .43)
            dx += .0055*curtain*np.sin(y*9-t*1.4)
            dy += .0018*breathe*oval(x, y, .23, .60, .28, .45)
            plant = oval(x, y, .85, .76, .16, .27)
            dx += .003*plant*np.sin(y*11+t*1.1)
        elif self.asset == "flood":
            person = oval(x, y, .235, .52, .13, .48)
            depth += .65*person
            water = ease((y-.54)/.20)*(1-np.minimum(1, person*1.5))
            dx += .0035*water*np.sin(y*84-t*1.9)
            dy += .0015*water*np.sin(x*35+y*20-t*1.4)
            dy += .0011*breathe*person
        elif self.asset == "friends":
            depth += .50*(oval(x, y, .16, .50, .16, .48)+oval(x, y, .85, .50, .16, .48))
            cloth = oval(x, y, .31, .13, .15, .21)+oval(x, y, .73, .15, .15, .24)
            dx += .005*cloth*np.sin(y*13+t*1.3)
            dy += .0015*breathe*oval(x, y, .16, .45, .15, .30)
            dy += .0014*math.sin(t*1.05+1)*oval(x, y, .85, .45, .15, .30)
        elif self.asset == "hand":
            hand = oval(x, y, .51, .51, .46, .60)
            depth += .55*hand
            dy += .0024*breathe*hand
            paper = oval(x, y, .57, .36, .08, .10)
            dx += .0018*math.sin(t*1.8)*paper
            dy += .0022*math.sin(t*1.8)*paper
        elif self.asset == "reading":
            depth += .45*oval(x, y, .60, .49, .40, .38)
            page = oval(x, y, .64, .32, .13, .12)
            dy += .003*math.sin(t*1.4)*page
            dx += .0018*math.sin(t*1.4)*page
            dy += .0013*breathe*oval(x, y, .82, .58, .22, .27)
        dx += .006*drift*depth
        dy += .002*math.cos(t*.19)*depth
        maps = np.stack(((x+dx)*(self.width-1), (y+dy)*(self.height-1)), axis=-1).astype(np.float32)
        maps = cv2.resize(maps, self.outsize, interpolation=cv2.INTER_LINEAR)
        frame = cv2.remap(self.image, maps, None, cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT_101)
        # An extremely gentle exposure response follows musical energy, never flashes.
        frame = cv2.convertScaleAbs(frame, alpha=1.025 + .022*energy, beta=0)
        return self.atmosphere(frame, t, energy)

    def atmosphere(self, frame, t, energy):
        w, h = self.outsize
        if self.asset == "flood":
            layer = frame.copy()
            for a,b,c,d in self.particles:
                px = int(((a+t*(.009+c*.006))%1)*w)
                py = int(((b+t*(.38+d*.22))%1)*h)
                length = int((.010+c*.014)*h)
                cv2.line(layer, (px,py), (px+int(length*.20),py+length),
                         (178,170,155), 1, cv2.LINE_AA)
            frame = cv2.addWeighted(frame, .88, layer, .12, 0)
        elif self.asset in ("room", "reading", "window", "reunion"):
            layer = frame.copy()
            for a,b,c,d in self.particles[:16]:
                px = int(((a+t*(.002+c*.003))%1)*w)
                py = int(((b-t*(.003+d*.004))%1)*h)
                if .16*w < px < .88*w:
                    cv2.circle(layer, (px,py), 1 if c<.7 else 2,
                               (135,176,205), -1, cv2.LINE_AA)
            frame = cv2.addWeighted(frame, .86, layer, .14, 0)
        return frame
