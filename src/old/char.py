from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
import random
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.showbase.InputStateGlobal import inputState

class Character():

    def __init__(self): 
    
        # Input

        self.actor = Nodepath('actor')


        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnLeft', 'q')
        inputState.watchWithModifiers('turnRight', 'e')

        self.actorNP = Actor(
                            '../models/guy.bam', {
                            'run' : '../models/guy_Idle.bam',
                            'idle' : '../models/guy_walk.bam',})

        self.actorNP.enable_blend
        self.actorNP.setScale(7) # 1ft = 0.3048m
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 1, -5)
        self.actorNP.setBlend(frameBlend = True) 
        self.actorNP.loop('idle')

        self.actorNP. reparentTo(self.actor)

        taskMgr.add(self.updatechar, "updateCharacter") 
    
    def updatechar(self, task):
        
        #update anims

        dt = globalClock.getDt()        
        self.isIdle=True
        anim=self.actorNP.getCurrentAnim()
        if anim not in ("walk","idle", "run", None):
            return task.cont
               



        if inputState.isSet('forward'): 
            self.isIdle = False
            self.actorNP.setPlayRate(1.0, "run")
            if(anim!="run"):
                self.actorNP.loop("run")             


        if self.isIdle:  
            if(anim!="idle"):
                self.actorNP.loop("idle")   
