"""Restrained motions tailored to 24 distinct painted scenes."""
import math
import cv2
import numpy as np


def ease(v):
    v = np.clip(v, 0, 1)
    return v*v*(3-2*v)


def oval(x, y, cx, cy, rx, ry):
    return np.exp(-2*(((x-cx)/rx)**2+((y-cy)/ry)**2))


class Scene:
    def __init__(self, asset, path, size):
        self.number = int(asset[1:])
        self.image = cv2.imread(str(path))
        if self.image is None:
            raise FileNotFoundError(path)
        self.h,self.w = self.image.shape[:2]
        self.size = size
        self.x,self.y = np.meshgrid(np.linspace(0,1,320,dtype=np.float32),np.linspace(0,1,180,dtype=np.float32))
        self.points = np.random.default_rng(190102126+self.number).random((36,4))

    def draw(self, camera, t, progress, energy):
        cx,cy,zoom = map(float,camera)
        x=(self.x-.5)/zoom+cx
        y=(self.y-.5)/zoom+cy
        dx=np.zeros_like(x);dy=np.zeros_like(y)
        n=self.number
        depth=.20*y
        breath=math.sin(t*1.15)
        if n in (1,5,7,13,19,21,22,24):
            leaves=oval(x,y,.13,.40,.25,.64)+oval(x,y,.90,.39,.16,.55)
            dx += .0035*leaves*np.sin(y*12-t*1.1)
            depth += .28*leaves
        if n in (2,6,8,9,11,12,15,18,19,22,24):
            person=oval(x,y,.28,.55,.25,.45)+oval(x,y,.73,.56,.23,.43)
            dy += .0015*breath*person
            depth += .35*person
        if n in (3,10,17,20,23):
            hands=oval(x,y,.49,.66,.40,.42)
            dy += .0014*breath*hands
            depth += .45*hands
            if n==10:
                dy += .003*float(ease(progress))*oval(x,y,.58,.64,.16,.16)
            if n==23:
                dx += .004*float(ease(progress))*oval(x,y,.37,.52,.24,.24)
                dx -= .004*float(ease(progress))*oval(x,y,.65,.52,.24,.24)
        if n==5:
            dx += .004*np.sin(y*10-t*1.5)*oval(x,y,.39,.35,.065,.45)
        if n==7:
            for px,py in ((.48,.09),(.71,.19),(.44,.44),(.81,.65)):
                paper=oval(x,y,px,py,.08,.10)
                dx += .004*math.sin(t*1.2+py)*paper
                dy += .003*math.cos(t*1.1+px)*paper
        if n in (13,14,21):
            water=ease((y-.66)/.22)
            dx += .0028*water*np.sin(y*75-t*1.4)
            dy += .0013*water*np.sin(x*28-t)
        if n==17:
            dy += .0025*math.sin(t*1.4)*oval(x,y,.62,.34,.17,.15)
        dx += .004*math.sin(t*.13)*depth
        dy += .0018*math.cos(t*.16)*depth
        maps=np.stack(((x+dx)*(self.w-1),(y+dy)*(self.h-1)),axis=-1).astype(np.float32)
        maps=cv2.resize(maps,self.size,interpolation=cv2.INTER_LINEAR)
        frame=cv2.remap(self.image,maps,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
        frame=cv2.convertScaleAbs(frame,alpha=1+.012*energy)
        if n in (11,14):
            layer=frame.copy();w,h=self.size
            for a,b,c,d in self.points:
                px=int(((a+t*.012)%1)*w);py=int(((b+t*(.20+c*.25))%1)*h)
                cv2.line(layer,(px,py),(px+3,py+int(h*(.008+d*.008))),(188,183,169),1,cv2.LINE_AA)
            frame=cv2.addWeighted(frame,.93,layer,.07,0)
        if n==4:
            # Transparent strands of steam rise from the bowl, with no flashing.
            w,h=self.size;layer=frame.copy()
            for i in range(3):
                pts=[]
                for j in range(28):
                    u=j/27
                    pts.append((int(w*(.53+i*.017+.007*math.sin(u*8-t*1.2+i))),int(h*(.51-u*.18))))
                cv2.polylines(layer,[np.array(pts,np.int32)],False,(207,213,216),2,cv2.LINE_AA)
            frame=cv2.addWeighted(frame,.94,layer,.06,0)
        return frame
