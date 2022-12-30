# from lib2to3.pgen2.token import BACKQUOTElash
from pdb import Restart
from tracemalloc import start
from turtle import left
from unicodedata import name
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.ActorInterval import ActorInterval, LerpAnimInterval
import logging

from math import sqrt, pow, sin, cos
from math import pi as M_PI
M_PI_2 = M_PI * 2

from numpy import true_divide

# from numpy import float256

from keyboardinput import KeyboardInput
import time

from panda3d.bullet import *
from panda3d.core import *
class Anims:


######takes character movemenbt states and decides which aNIMATIONS should play

    def __init__(self):
        #walk is run walking is walk lol
        self.walktimer = None
        # self.wheel = loader.loadModel('../models/sword.glb')
        # self.wheel.reparentTo(self.charM)

        self.atkwalk = False
        self.current_animations = []
        self.Idle = 'idle'
        self.Walk = 'walk'
        self.Walking = 'walking'
        self.Dodge = 'dodge'
        self.Land = 'land'
        self.Jump = 'jump'
        self.Fall = 'falling'
        self.airDodge = 'airdodge'

        self.attackanims = ['kick1', 'kick2', 'kick3']
        self.priorityanims = ['vaultend', 'recoil1', 'recoil2', 'blending']#lnand
        self.animspecial = False

        self.blendoutAtk = None
        # self.priorityanims=[]
        # self.easeinATX = []
        # self.easeoutATX = [self.createEaseOut('kick1')]
        # for x in range(len(self.attackanims)):
        #     self.easeinATX[x] = self.createEaseIn(self.attackanims[x])
        # for x in range(2):
        #     self.easeoutATX[x] = self.createEaseOut(self.attackanims[x])
        # def __init__(self):
        self.dodgetimer=None
        self.blendtimer = None
        self.blending=False
        self.current_seq = None

        self.animseq = None
        self.walkseq = None
       
        self.deflectFrames=None
        self.deflectinterval=None

        self.mechFX = NodePath('mechfx')

        self.currentGrapple = None
# #------------------FX here        
#         self.dodgeframes = self.charM.getNumFrames('dodge')
#         self.dodgeposeground = loader.loadModel('../models/dodgepose.glb')
#         # self.dodgeposeground.setShader(self.shader)
#         self.dodgeposeground.setTransparency(True)
#         self.dodgeposeground.setH(180)
#         self.dodgeposeair= loader.loadModel('../models/dodgeposeair.glb')
#         self.dodgetrail = []
#         self.dodgetraileffect = False#if the copied nodes are visible        
#         self.dodgetrailair = []
#=------------
        # coral = loader.loadModel('../models/coral.glb')
        # coral.reparentTo(self.worldNP)
        # coral.setPos(0,-115,0)
     
        for i in range(self.dodgeframes ): #self.dodgetrail[i] == None:
            self.dodgetrail.append(NodePath(f"dtrail{i}"))
            self.dodgeposeground.instanceTo(self.dodgetrail[i])

        # self.ease_in_idle = self.createEaseIn('idle')
        # self.ease_out_idle = self.createEaseOut('idle')

        # self.ease_in_walk = self.createEaseIn('walk')
        # self.ease_out_walk = self.createEaseOut('walk')

        # self.ease_in_walking = self.createEaseIn('walking')
        # self.ease_out_walking = self.createEaseOut('walking')

        # self.ease_in_land = self.createEaseIn('land')
        # self.ease_out_land = self.createEaseOut('land')

        # self.ease_in_dodge = self.createEaseIn('dodge')
        # self.ease_out_dodge = self.createEaseOut('dodge')

        # self.ease_in_jump = self.createEaseIn('jump')
        # self.ease_out_jump = self.createEaseOut('jump')

        # self.ease_in_fall = self.createEaseIn('falling')
        # self.ease_out_fall = self.createEaseOut('falling')
        self.ganimstarted = False# to start grapple anim

        self.currentAtk = ['kick1', 30] # current attack + end frame

        self.groundstates = [None]
        self.animFilter = {            
            "idle": ["idle2walk",
                     "idle2dodge"],
            "idle2walk": ["walking"],
            "idle2dodge": ["dodging"],
            "walking": ["walk2idle",
                        "walk2dodge"],
            "walk2idle": [],
            "walk2dodge": [],
            "dodging": [],
            "landing": [],
            "land2idle": [],
            "land2walk": []
        }

        self.airstates  = [None]

        self.dodge2fall = False
        

    def attachblade(self, blade):
        
        self.blade = blade

        
        self.forearm = self.charM.expose_joint(None, 'modelRoot', 'forarm.L')# self.blade.reparentTo(self.charM)
        self.leftfoot = self.charM.expose_joint(None, 'modelRoot', 'foot.L')
        self.rightfoot = self.charM.expose_joint(None, 'modelRoot', 'foot.R')
        self.blade.reparentTo(self.leftfoot)  
        copy =self.rightfoot.attachNewNode('copy')
        self.blade.instanceTo(copy)
        
    def timer(self,  task):
        return task.cont
        # if task.time<time
    def updateAnimMech(self):
        #Control the tilt with joystick
        self.mechanim = self.charM.getCurrentAnim()
        if self.character.movementState == 'dodging':
            self.dodgetrailfx()
            return
        # if self.isGrappling == True
#gamepad
        self.charM.setR(self.leftX * 10 )
        self.charM.setP(self.leftY* -10 )
        #bend legs 
        # if self.leftX>0:
        #     r
        r = self.leftX*75
        if self.leftX<0:
            self.mechThighL.setP(r)
            self.mechShinL.setH(-r)
        if self.leftX>0:
            self.mechThighR.setP(-r)
            self.mechShinR.setH(r)
                # self.mechThighL.setP(l)
        if self.character.movementState == 'attacking':
            self.charM.setBlend(animBlend = False)
            return
        if self.moving == False: #idle
            if (self.mechanim!="idle",):
                self.charM.loop('idle', partName='arms') 
            return

        if self.character.movementState == "flying":

            if (self.mechanim!="fly"):
                self.charM.loop('fly', partName='arms') 
                print('loop fly')

            print(self.dodgetimer)
        return

    def updateAnimOF(self):#, task): 
        # print(self.isIdle, self.isWalking)
        # print(self.character.vaulting)
        # print(self.current_seq) 
        # print(self.character.movementState)
        # print('blendtiumer',self.blendtimer)
        # if self.character.movementState == "endaction":
        #      print('blend out')
        # print('current atk', self.currentAtk)
        if self.dead == True:
            if self.anim!='die':
                self.charM.play('die')
            return
        if self.isWalking == False:
            self.charM.setBlend(animBlend = False)
        if self.character.movementState == "dodging":
            self.dodgetrailfx()    
        if self.current_seq!=None:
            # return
            self.endCurSeq()
        if self.animseq==None:
            self.anim=self.charM.getCurrentAnim()
        self.frame = self.charM.getCurrentFrame()   

        
        # print('anim',self.anim, 'frame', self.frame) 
        # print(self.animseq)
        # self.charM.disableBlend()
        # if self.character.movementState == 'endaction':
        #     print(self.anim, 'to idle')
        if self.anim in self.priorityanims:
            return #task.cont
        # if self.isPerched == True:
        #     print('anim perche')
        #     self.animPerch()
        
        if self.character.smashonground == True:
            self.endsmash()#lol
        if self.character.movementState == 'attacking':
            self.charM.setBlend(animBlend = False)
            return
        if self.blendoutAtk!=None:
            if self.blending==True:  #Fix dodge while blending 
                
                # self.land2Idle()
                if self.isIdle == True:
                    self.blendAnim(self.blendoutAtk[0],'idle',self.blendoutAtk[1],1)
                else:
                    self.blendAnim(self.blendoutAtk[0],'walk',self.blendoutAtk[1],1)
                #add land2walk here
            else:
                self.animBlendAtk()
            return

               
        if self.character.movementState == 'finisher':
            # self.animGrind()
            return



        if self.character.movementState == "airdodge":
            if self.blending == True:
                self.endBlend()
            self.animDodgeAir()
         
        if self.character.movementState == "exitdodge":
            self.cleanupdodge()

        if self.character.movementState == "ground":
            self.airstates  = [None]
  
            if self.character.isLanding ==True:
                # print(self.frame)
                if self.blending==True:
                    # self.land2Idle()
                    if self.isIdle == True:
                        self.blendAnim('land', 'idle', 5, 1)
                    else:
                        self.blendAnim('land', 'walk', 5, 1)
                else:
                    self.animLand()#start here
                return
                # print('landing', self.frame)


            # if self.character.isdodging:
            #     self.groundstates == 'grounDodge'

            # if self.character.isdodging == False and self.anim == 'dodge':
            #     self.charM.stop()
        ###LOOP IDLE 
            
            if self.isIdle ==True:# and self.anim !='parry' and self.anim not in self.priorityanims:
                self.groundstates = 'idle'
                self.animIdle()
                # if self.prevGroundState == 'landing':
                #     # l2i=Func(self.land2Idle)
                #     # i=Func(self.animIdle)
                #     # self.current_seq = Sequence(l2i,i)
                #     # self.current_seq.start()
                #     self.land2Idle()#>idle
                # if self.prevGroundState == 'walking':
                #     self.Walk2Idle()#>walk
                # if(self.anim!="idle" and self.anim!="dodge"):
                #     self.charM.loop('idle')
                
        ####LOOP WALK        
            if self.isWalking ==True:# and self.character.isdodging ==False and self.anim !='parry' and self.anim not in self.priorityanims:#and self.character.isLanding == False
                self.groundstates = 'walking'
                #TODO - add an 'enter walk' to blend into walking 
                self.animWalk()
  
            # if self.isWalking ==False:
            #     self.charM.setBlend(animBlend = False)
            #     self.charM.setControlEffect('walk', 0)
            #     self.charM.setControlEffect('walking',0)
        if self.character.movementState == "jumping" or self.character.movementState == 'falling':# and self.character.enableVaulting==False:#and self.character.isdodging ==False:
            self.groundstates  = [None]
            
            # print(self.airstates)
            # self.isIdle ==False
            # print(self.left_x.value * 10) #will use to control bones

            if self.character.movementState == "jumping":
                self.airstates == "jumping"
                self.animJump()
            
            if self.character.movementState == "falling" :
        
                self.airstates = 'falling'
                self.animFall()
        # if self.character.enableVaulting ==True:
        #     print('vault nim')
        #     self.animVault()
        if self.character.movementState =="wallgrab":
            self.animWallgrab()
        if self.character.movementState == "vaulting":
            # print('vaultinnit')
            self.animVault()
            # print('animvault')
            # if self.character.movementState == 'attacking':
            #     self.animattack()

            
        
        return #task.cont
    def getseqframe(self):
         pass    # getcurrent frame on interval

    def easeAnimation(self, t,  anim):
        self.charM.setControlEffect(anim, t)

    def createEaseIn(self, anim):
        return LerpFunc(
            self.easeAnimation,
            fromData=0,
            toData=1,
            blendType="easeIn",
            extraArgs=[anim])

    def createEaseOut(self, anim):
        return LerpFunc(
            self.easeAnimation,
            fromData=1,
            toData=0,
            blendType="easeOut",
            extraArgs=[anim])
    def startCurSeq(self, animFrom, animTo, easeIn, easeOut,n):
        if self.current_seq != None:
            self.current_seq.finish()
            
        self.current_seq = Sequence(
            Func(self.charM.enableBlend),
            Func(self.charM.play, animTo),#was loop
            Parallel(
                easeOut,
                easeIn),
            Func(self.charM.stop, animFrom),
            Func(self.charM.disableBlend),
            name=n)
        self.current_seq.start()

    def endCurSeq(self):
        if self.current_seq is not None:
            self.current_seq.finish()
            self.current_seq = None

# ######ANIM STATES
#     def enterIdle(self):
#         # base.messenger.send(self.getConfig("audio_stop_walk_evt"))
#         self.current_animations = [self.IDLE]
#         if not self.getCurrentAnim() == self.IDLE:
#             self.loop(self.IDLE)
####Transition anims
    # def land2Idle(self):
    #     # print('land2idle')
    #     self.blending=True
    #     if self.blendtimer==None:
    #         self.blendtimer = taskMgr.add(self.timer, 'timer')
    #     dt = round(self.blendtimer.time, 2) * 10
    #     i = dt
    #     l = 1-i
    #     self.charM.enableBlend()
    #     self.charM.setControlEffect('idle', i)
    #     self.charM.setControlEffect('land', l)
    #     self.charM.pose('idle', 1)
    #     self.charM.pose('land', 5)
    #     # print('blend timer', self.blendtimer.time, self.frame, 'l', l)
    #     print('l',l, 'i', i)
    #     if l <=0 :
    #         self.charM.disableBlend()
    #         self.character.isLanding = False
    #         self.blending=False
    #         taskMgr.remove('timer')
    #         self.blendtimer =None
    #         print('done blending')
    #         return
    def easeLinear(self,p):#y=x
        return p
    def BackEaseOut(self,p):
        f = (1 - p)
        return 1 - (f * f * f - f * sin(f * M_PI))
    
    def blendAnim(self, animfrom, animto, framefrom, frameto):
        """look at animland to see correct implementation of this(needs to be called in task, and repeatedly called until self.blending = False)"""
        # print('blend', self.character.movementState) # NEED TO ADD DIFF BLEND TYPES

        self.blending=True
        if self.blendtimer==None:
            self.blendtimer = taskMgr.add(self.timer,'blendtimer')
        dt = round(self.blendtimer.time, 2) *10
        # i = dt
        i=self.easeLinear(dt)
        # i = self.BackEaseOut(dt)
        l = 1-i
        self.charM.setBlend(animBlend = True)
        self.charM.setControlEffect(animto, i)
        self.charM.setControlEffect(animfrom, l)
        self.charM.pose(animto, frameto)
        self.charM.pose(animfrom, framefrom)
        # print('blend timer', self.blendtimer.time, framefrom, 'l', l)
        # print('l',l, 'i', i)
        if l <=0 :
            self.endBlend()
            # self.charM.setBlend(animBlend = False)
            # self.character.isLanding = False
            # self.blending=False
            # taskMgr.remove('timer')
            # self.blendtimer =None
            
            # self.blendoutAtk = None
            # if self.character.movementState == "attacking":
            #     print('blend out of attack')
            #     self.character.movementState = "endaction"
            print('done blending')
            return
    def endBlend(self):
            print('endblend')
            self.charM.setBlend(animBlend = False)
            self.character.isLanding = False
            self.blending=False
            taskMgr.remove('blendtimer')
            self.blendtimer =None
            
            self.blendoutAtk = None
            # self.enterWalk = False

####anim loops
    def animIdle(self):
        self.current_animations = [self.Idle]
        self.charM.setBlend(animBlend = False)
        # if self.current_seq != None:
        #     self.current_seq.finish()
        #     self.current_seq =None
        self.charM.setPlayRate(1, 'idle')
        if (self.anim!="idle" and self.anim!="land"):
            self.charM.loop('idle')    
        # idle = self.charM.actorInterval('idle',loop = 1, startFrame=0, endFrame = 100)    
        
        # self.current_seq = Sequence(idle, name='idle')
        # self.current_seq.start()
        # print(idle.getCurrentFrame())
    def animPerch(self):
        print(';perch')
        self.charM.setPlayRate(1, 'perched')
        if (self.anim!="perched"):
            self.charM.play('perched')  
 
    def animWalk(self):
        
        # print('anim walk', self.charM.getCurrentAnim())
        
        # if self.current_seq != None:
        #         self.current_seq.finish()
        # if self.blending==True:
        # self.endBlend() ## need to call this only once
        wa1 = True
        if self.lockedOn ==False:
            self.blending=True
            x = self.leftValue / 10 
            # print(x)
            tR = 0.5 + (x / 2) #run playrate
            tW = 1.0 + x #walk playrate
            # self.charM.setBlend(animBlend = True)
            # self.charM.setPlayRate(tR, "walk")   
            # self.charM.setPlayRate(tW, "walking")  
            # self.charM.setControlEffect('walk', x)
            # self.charM.setControlEffect('walking', 1-x)

            # walkControl = self.charM.getAnimControl("walking")
            # if not walkControl.isPlaying():
            #     self.charM.loop("walking")

            # runControl = self.charM.getAnimControl("walk")
            # if not runControl.isPlaying():# and x!=1.0:
            #     self.charM.loop("walk")
        
            #placceholder
            self.charM.setPlayRate(x, "walk")  
            if self.anim!='walk':
                print('walk')
                self.charM.loop("walk")
                

            # if self.anim!="walking":    
            #     print('walking')
            #     self.charM.loop("walking")
                    
                    


###blend between walk/reun here --- TODO - disable blend when not walking
            

#
        if self.lockedOn ==True:
            if self.anim!="atackwalk":
                self.charM.setPlayRate(2, 'attackwalk')
                self.charM.loop("atackwalk")
    def animattackwalk(self):
        # if self.anim not in self.attackanims:
        # if self.atkwalk ==True:
        if self.anim!="atackwalk":
                self.charM.loop("atackwalk")
    def animDodge(self):
        # if self.animseq !=None:
        #         self.animseq.finish()
        #         self.animseq = None
        def stateDodge():
            self.character.movementState = 'dodging'
        def stateEnd():
            self.character.dodgedir = 0

        self.charM.setBlend(animBlend = False)
        anim1 = self.charM.actorInterval('dodge',loop = 0, startFrame=0, endFrame = 10)
        anim2 = self.charM.actorInterval('dodge',loop = 0, startFrame=10, endFrame = 15)

        # self.dodgetrail = []
        #make trail

                    # se = Sequence(start, Wait(1), end).start()

        start=Func(stateDodge)
        mid=Func(stateEnd)
        end=Func(self.finish)
        self.animseq = Sequence(Parallel(start, anim1),Parallel(mid,anim2), end)
        self.animseq.start()            

        # self.current_animations = [self.Dodge]
        # if (self.anim!="dodge"):
        #     if self.anim == 'idle':
        #         self.Idle2Dodge()
        #     if self.anim == 'walk':
        #         self.Walk2Dodge()
        #         # print('idle2dodge')
        #     self.charM.play("dodge")
            # if self.character.isdodging == False:
            #     self.charM.stop()
        
    # def cleanupdodge(self):
    
    def dodgetrailfx(self):#, dt):
        if self.dodgetimer==None:
            self.dodgetimer = taskMgr.add(self.timer,'dodgetimer')

        if self.character.state == 'mech':
            # print('mech Strail')
        
            # t=round(self.dodgetimer.time *10)
            # print('dodgbeframe', t)
            fx = self.charM.instanceTo(self.mechFX)
            self.mechdodgefx[1].reparentTo(render)
            if self.FXset == False:
                self.mechdodgefx[1].setPos(self.charM.getPos(render))
                self.FXset = True
            # self.charM.pose()
            # fx.setPos(self.charM.getPos())
            # print('mech dodgetime:', self.dodgetimer.time)
                    # if round((dt%.3) * 100) == 1:
            # print('shooty buyllet', round((dt%.6) * 100))
            if self.dodgetimer.time>.5:
            # if self.dt > .5:
                taskMgr.remove('dodgetimer')
                self.dodgetimer = None
                self.finish()
            return        
        def dodtrail(i):
            #move models to dodge positions, then hide  

            self.dodgetrail[i].setPos(self.character.movementParent.getPos(render))
            self.dodgetrail[i].setH(self.charM.getH(render))
            self.dodgetrail[i].reparentTo(render)
            if self.dodgetrail[i].isHidden():
                self.dodgetrail[i].show()
        def cleartrail(i):
            self.dodgetrail[i].hide()
            # taskMgr.remove('dodgetimer')
            # self.dodgetimer=None
            self.FXset = False

        self.dodgetrailefect = True
        for o in range(self.dodgeframes):

            # if self.dodgetrail[i] == None:
            #     self.dodgetrail.append(render.attachNewNode(f"dtrail{i}"))
            #     self.dodgeposeground.instanceTo(self.dodgetrail[i])
            if self.frame !=None:
                # print('uwu')
                if self.frame > 5 and o == self.frame:
                    se = Sequence()
                    start = Func(dodtrail, o)
                    end = Func(cleartrail, o)
                    # dodtrail()
                    # cleartrail()
                    se.append(start)
                    se.append( Wait(.2))
                    se.append(end)
                    se.start() 

    def animLand(self):
        self.charM.setBlend(animBlend = False)
        
        if(self.anim!="land") and self.blending!=True:
            self.charM.setPlayRate(1, "land")
            self.charM.play("land")
            
        elif  self.frame ==5:
            print('end land')
            # self.character.isLanding = False
            if self.isIdle ==True:
                self.blendAnim('land', 'idle', 5, 1)
            else:
                self.blendAnim('land', 'walk', 5, 1)
            #     self.land2Idle()
                # if self.blendtimer==None:
                #     self.blendtimer = taskMgr.add(self.timer, 'timer')
                # if self.blendTimer==None:
                #     self.blendTimer=taskMgr.add(self.timer, 'timer')
                # print('land2idoeke')

    
            #transitrion to current anim
        # print('landing', self.frame)

        # self.charM.disableBlend()
        # if self.anim !="parry":
        #     self.charM.play("parry")

    def animBlendAtk(self):
        if self.isIdle == True:
            self.blendAnim(self.blendoutAtk[0],'idle',self.blendoutAtk[1],1)
            # self.blendAnim('kick1', 'idle', 30, 1)
        else:
            self.blendAnim(self.blendoutAtk[0],'walk',self.blendoutAtk[1],1)

    def animDodgeAir(self):
        self.charM.setBlend(animBlend = False)
        self.current_animations = [self.airDodge]
        # if(self.left_x.value * 10) < 0:
        self.dodgetrailefect = True
        # for o in range(self.dodgeframes):
        if (self.anim!="airdodgeF"):
            self.charM.play("airdodgeF")
                
        # if(self.left_x.value * 10) > 0:
            # if (self.anim!="airdodgeR"):
                # self.charM.play("airdodgeR")
        # if(self.left_y.value * 10) > 0:
            # if (self.anim!="airdodgeF"):
                # self.charM.play("airdodgeF")     
        # if(self.left_y.value * 10) < 0:
            # if (self.anim!="airdodgeB"):
                # self.charM.play("airdodgeB")     

    def animFall(self, fallanim = 'falling'):
        # fallanim = 'falling'
        # print(self.charM.listJoints())
        self.charM.setBlend(animBlend = False)
        if(self.anim!='falling'):
            self.charM.setPlayRate(1, "falling")
            self.charM.loop("falling", restart=10)
        
    def animJump(self):
        # if self.current_seq != None:
        #     self.current_seq.finish()
        # jump =self.charM.actorInterval('jump',loop = 0, startFrame=0, endFrame = 5)
        # self.current_seq = Sequence(jump,name='jump')
        # self.current_seq.start()
        if self.blending==True:
            self.endBlend()
        # self.charM.setBlend(animBlend = False)
        if(self.anim!='jump'):
            self.charM.setPlayRate(1, "jump")
            self.charM.play('jump')
            if self.anim == 'jump' and self.frame == 5:
                self.charM.loop('jump')
    def animWallgrab(self):
        anim = None
        if self.character.wallRun[4] == "wallgrabbing":
            if self.character.wallRun[1]== 'left':
                anim='wallgrabL'
            elif self.character.wallRun[1] == 'right':
                anim='wallgrabR'
        elif self.character.wallRun[4] == "wallrunning":
            if self.character.wallRun[1]== 'left':
                anim='wallrunL'
            elif self.character.wallRun[1] == 'right':
                anim='wallrunR'
        
        if(self.anim!=anim):
            self.charM.play(anim)
    def animVault(self):
        ####### Has guy grab ledge, is janky need to use rig with ledge grab bone
        # self.character.vaultcheckNode.wrtReparentTo(self.character.movementParent)
        # self.character.vaultcheckNode2.wrtReparentTo(self.character.movementParent)
        # pos = ((self.charM.getX(), self.charM.getY(), self.character.ledgegrab))
        # zint= LerpPosInterval(self.charM,.1,pos)
        # ain = ActorInterval(self.charM, 'vaultup', startFrame=0, endFrame=5)
        # zout=LerpPosInterval(self.charM,.1,(0,0,0))
        # aout = ActorInterval(self.charM, 'land', startFrame=4, endFrame=12)
        # self.character.vaultseq = Sequence(zint, ain,Parallel(zout,aout))
        ##########
        # print(self.charM.getCurrentFrame())
        if(self.anim!='vaultup'):
            self.charM.play('vaultup')
        #     self.character.vaultseq.start()
                # self.charM.setZ(self.character.getZ())
        
   ###atack section here
   
    def animStartGrapple(self, anim):
        self.ganimstarted = True
        if self.animseq !=None:
            
            if self.animseq.name == 'startGgrapple':
                if self.animseq.isPlaying():
                    return
        def stateGrapple():
            self.character.preGrapple = False
        def pre():
            self.character.preGrapple = True
        # self.dodgetrail = []
        #make trail

                    # se = Sequence(start, Wait(1), end).start()
        b4 = Func(pre)
        start=Func(stateGrapple)
        attachHB = Func(self.hb, self.charM, self.GatkNode, CollisionCapsule(0,0,0,0,0,3,1.2), visible = True)
        # mid=Func(stateEnd)
        end=Func(self.finish)

   
        anim1 = self.charM.actorInterval(anim,loop = 0, startFrame=0, endFrame = 16)
        # anim2 = self.charM.actorInterval('grappleGround',loop = 0, startFrame=10, endFrame = 15)
        grappling = self.charM.actorInterval(anim,loop = 1, startFrame=16, endFrame = 40)

        # self.dodgetrail = []
        #make trail

                    # se = Sequence(start, Wait(1), end).start()

        self.animseq = Sequence(Parallel(b4,anim1),Parallel(start,attachHB), grappling, name='startGgrapple')
        self.animseq.start() 
        

    def queueStage(self,x, qud):
        self.attackqueue = x 
        self.attackQueued = qud
        # if qud==True:
        #     self.attached = False
    def check4Queue(self):
        """if there is a queued attack, this will trigger it"""
        if self.attackQueued==True and self.attackqueue>0:
            # print('do queued attack',self.attackqueue+1)
            if self.qdatk == 'slash':
            # self.finish()
            # if type == 'slash':
                self.attached = False
                self.slashAttack() 
            if self.qdatk == 'stab':
                self.attached = False
                self.stabattack()
            # if type == 'stab':
            # self.stabattack()
        else:
            print('no queued atack')      
    def attach(self,foot):
       
        if self.attached == False: #and self.hitcontact==False:
            if self.character.state == "OF":
            
                self.hb(parent=foot, node = self.atkNode, shape=CollisionCapsule(0, .5, 0, 0, 0, 0, .5))
            if self.character.state == "mech":
                self.hb(parent=self.bladeL, node = self.atkNode, shape=CollisionCapsule(0, .5, 0, 0, 2, 0, 1))
                self.hb(parent=self.bladeR, node = self.atkNode, shape=CollisionCapsule(0, .5, 0, 0, 2, 0, 1))
    def attackingFalse(self):
        self.character.isAttacking = False
    def parryFalse(self):
        self.character.isParrying = False
        if self.leftjoystick==True: #is walking
            self.finish()
            # print('walk out of pary')
    def atkstage(self, buffer, pause):
        """this reads the frames of the attack anims"""
        self.buffer = buffer
        self.pauseframe = pause
    def detachtrail(self, node):
        # node.wrtReparentTo(self.worldNP)
        node.detachNode()
    
    def playSound(self, sfx):
        sfx.play()
    def animattackslash(self,order,foot):
        
        # def slashatk(anim,fx,fxtarget,n, activeframes=12, pauseframe=21, finalframe =30):
        def slashatk(anim,fx,fxtarget,n,sfx1, sfx2, aFramestart = 4,aFrameend=12, pauseframe=21, finalframe =30):
            """hit box is attached during aFramestart to aFrameend, pause added to combo chain at pauseframe
            Flips are acxcepted from pause frame to end
            Queued attacks are accepted from frame0  to aframeend"""
            # self.charM.setPlayRate(1, "slashkick1")
            # self.charM.play('slashkick1')
            
            self.currentAtk = [anim, finalframe]
            self.anim = anim
            # fx.reparentTo(self.charM)
            fx.reparentTo(fxtarget)
    
           
            k1 = self.charM.actorInterval(anim,loop = 0, startFrame=0, endFrame = aFramestart)
            acceptQueue = Func(self.queueStage, order, False)
            sound1 = Func(self.playSound, sfx1)
            hb = Func(self.attach, foot)
            k2 = self.charM.actorInterval(anim, loop = 0,startFrame=(aFramestart+1), endFrame = aFrameend)
            offsettex = LerpTexOffsetInterval(fx, .5,(1,0),(0,0), textureStage=self.ts0)
            k3= self.charM.actorInterval(anim, loop = 0,startFrame=(aFrameend+1), endFrame = pauseframe)
            k4 = self.charM.actorInterval(anim, loop = 0,startFrame=(pauseframe + 1), endFrame = finalframe)#attacking should be flase when animseq is buffer
            
            # fadeout = LerpTexOffsetInterval(self.slash1trail, 1,(1,0),(0,0), textureStage=self.ts0)
            detachfx = Func(self.detachtrail, fx)
            atkfalse = Func(self.attackingFalse)
            
            sound2 = Func(self.playSound, sfx2)
            
            
            endqueue = Func(self.queueStage, 0, None)
            qcheck = Func(self.check4Queue)
            # start = Func(self.readFrames, 'start')
            # pause = Func(self.readFrames, 'pause')
            # end =  Func(self.readFrames, 'end')
            
            atkfx = Sequence(offsettex, detachfx)
            # seqend = Sequence(Parallel(k2),Parallel(k3,  atkfalse))
            sequinp2=Sequence(Parallel(k2, hb,),
                            Parallel(atkfalse,qcheck, Func(self.atkstage, buffer = True, pause = False)),
                            Parallel(k3, endqueue),
                            Func(self.atkstage, buffer = True, pause = True),
                            k4,
                            Func(self.atkstage, buffer = False, pause = False))
            self.animseq =Sequence(Parallel(k1, sound1, acceptQueue),
                                  Parallel(sequinp2, sound2), name=n)
                                #   Func(self.atkstage, False, False)))
            self.animseq.start()
        if self.character.state == "OF":
            if order == 1:
                self.character.isAttacking = True
                # slashatk('kick1', self.slash1trail, 'slash1')
                slashatk('kick1', self.slash1trail,self.charM, 'slash1', self.preKicksfx, self.slash1sfx)
                
            if order == 2:
                self.character.isAttacking = True
                self.detachtrail(self.slashfx)
                slashatk('kick2', self.slash2trail,self.charM, 'slash2',self.preKicksfx, self.slash2sfx)
    
    
            if order == 3:
                self.character.isAttacking = True
                self.detachtrail(self.slash2trail)
                slashatk('kick3', self.slash3trail,self.charM, 'slash3',self.preKicksfx, self.slash1sfx)
            
    
            if order == 4:
    
                self.character.isAttacking = True
                self.detachtrail(self.slash3trail)
                slashatk('pausekick', self.slash3trail,self.charM,'pausekick',self.preKicksfx, self.slash1sfx,aFramestart = 15,aFrameend=30, pauseframe = 32, finalframe=35)#, pauseframe = 49, finalframe=51)
        if self.character.state == "mech":
            if order == 1:
                self.character.isAttacking = True
                # slashatk('kick1', self.slash1trail, 'slash1')
                slashatk('slash1', self.slash1trail,self.charM, 'slash1', self.preKicksfx, self.slash1sfx)
                
            if order == 2:
                self.character.isAttacking = True
                self.detachtrail(self.slashfx)
                slashatk('slash2', self.slash2trail,self.charM, 'slash2',self.preKicksfx, self.slash2sfx)
    
    
            if order == 3:
                self.character.isAttacking = True
                self.detachtrail(self.slash2trail)
                slashatk('slash3', self.slash3trail,self.charM, 'slash3',self.preKicksfx, self.slash1sfx)
            
    
            # if order == 4:
    
            #     self.character.isAttacking = True
            #     self.detachtrail(self.slash3trail)
            #     slashatk('pausekick', self.slash3trail,self.charM,'pausekick',self.preKicksfx, self.slash1sfx,aFramestart = 15,aFrameend=30, pauseframe = 32, finalframe=35)#, pauseframe = 49, finalframe=51)
            
    def animattackstab(self, order, foot):
        
        # def stabatk(anim,fx,fxtarget, n,activeframes=8, pauseframe=15, finalframe =20):
        def stabatk(anim,fx,fxtarget, n,aFramestart = 2, aFrameend = 8, pauseframe=15, finalframe =20):    
            self.anim=anim

            self.currentAtk = [anim, finalframe]
            # self.charM.setPlayRate(1, "slashkick1")
            # self.charM.play('slashkick1')
            fx.reparentTo(fxtarget) 
            k1 = self.charM.actorInterval(anim,loop = 0, startFrame=0, endFrame = aFramestart)
            acceptQueue = Func(self.queueStage, order, False)
            k2 = self.charM.actorInterval(anim, loop = 0,startFrame=5, endFrame = aFrameend)
            offsettex = LerpTexOffsetInterval(fx, 1,(0,0),(1,0), textureStage=self.ts0)
            k3= self.charM.actorInterval(anim, loop = 0,startFrame=(aFrameend+1), endFrame = pauseframe)
            k4 = self.charM.actorInterval(anim, loop = 0,startFrame=(pauseframe + 1), endFrame = finalframe)#attacking should be flase when animseq is buffer
            
            detach = Func(self.detachtrail, fx)
            atkfalse = Func(self.attackingFalse)
            hb = Func(self.attach, foot)

            endqueue = Func(self.queueStage, 0, None)
            qcheck = Func(self.check4Queue)
            
            atkfx = Sequence(offsettex, detach)
            seqend = Sequence(Parallel(k2),Parallel(k3,  atkfalse))
            sequin=Sequence(Parallel(k2,hb),
                            Parallel(atkfalse, qcheck,Func(self.atkstage, True, False)),
                            Parallel(k3,endqueue),
                            Func(self.atkstage, True, True),
                            k4,
                            Func(self.atkstage, False, False))
            self.animseq =Sequence(Parallel(k1,acceptQueue),
                                #   Parallel(sequin, atkfx), fx go here
                                  sequin,
                                  name=n)
            self.animseq.start()  
        
        if order == 1:
            self.character.isAttacking = True
            stabatk('stab1', self.slash1trail,self.blade,'stab1')
            self.slash2sfx.play()

        if order == 2:
            self.character.isAttacking = True
            self.detachtrail(self.slash1trail)
            stabatk('stab2', self.slash2trail,self.blade,'stab1')
            self.slash1sfx.play()
   
        if order == 3:
            self.character.isAttacking = True
            self.detachtrail(self.slash2trail)
            stabatk('stab3', self.slash3trail,self.blade,'stab1')
            self.slash2sfx.play()
    def animsmashattack(self):
        print('smash')
        self.anim = 'smash'
        def smashstage(x):
            self.character.smash1 = x
        stage1 = Func(smashstage, True)
        stage2 = Func(smashstage, False)
        s1 = self.charM.actorInterval('smash',loop = 0, startFrame=0, endFrame = 8)
        s2= self.charM.actorInterval('smash',loop = 0, startFrame=9, endFrame = 15)
        self.animseq = Sequence(Parallel(stage1,s1), Parallel(s2, stage2),name='SMASH!') 
        self.animseq.start()#$####need 2 end this
    def animDeflect(self):
        # if self.attached == False:
        #         self.hb(bone=self.forearm, node = self.parryNode)
        # if self.animseq !=None:
        #         self.animseq.finish()
        #         self.animseq = None
        self.currentAtk = ['parry', 25]
        self.anim='parry'
        self.character.isAttacking = True ## Hiotbox doesnt attach if ur parrying from an atk if this isnt true for some reason
        self.character.isParrying=True# isparrying used for both parry and deflect - sets mvt to 0
        def finpar():
            self.attached = False
            # self.character.isParrying = False
            # self.finish()
            # self.character.movementState = "endaction"
                # print('enmdparry')
            self.parryNode.node().clearSolids()
        
        fin=Func(self.finish)
        self.deflectinterval= self.charM.actorInterval('parry',loop = 0, startFrame=0, endFrame = 10)
        atkingfalse=Func(self.attackingFalse)
        clear = Func(finpar)
        pfalse = Func(self.parryFalse)

        finish=self.charM.actorInterval('parry',loop = 0, startFrame=10, endFrame = 25) #if recoil, replace this with recoil anim
        # finish = Func(self.charM.play, 'parry', fromFrame=10)
        self.animseq = Sequence(self.deflectinterval,Parallel(atkingfalse,clear, pfalse),finish, fin)
        self.animseq.start()

    # def animGrapple(self):
    #     self.charM.lookAt(self.currentGrapple)
    #     return

    # def animGrind(self):
    #     # if 'jump' not in self.animfilter[self.anim]:
    #     #     return
    #     if(self.anim!='grind'):
    #         self.charM.setPlayRate(1, "grind")
    #         self.charM.play('grind')
    #     leftfoot = self.charM.expose_joint(None, 'modelRoot', 'heelik.L')
    #     rightfoot = self.charM.expose_joint(None, 'modelRoot', 'heelik.R')
    #     hip = self.charM.expose_joint(None, 'modelRoot', 'pelvis')
    #     hip.setHpr(render,(0,0,0))
    #     # leftfoot.setZ(5)
    # def scarfSetup(self):
    #     info = self.world.getWorldInfo()
        
    #     info.setGravity(-9)
    #     info.setAirDensity(50000)
    #     info.setWaterDensity(0)
    #     info.setWaterOffset(10)
    #     info.setWaterNormal(Vec3(0, 0, -1))

    #     self.arm = self.charM.expose_joint(None, 'modelRoot', 'bicep.R')
        # self.pin = NodePath(BulletRigidBodyNode('pin')) 
        
        # self.pin.setPos(self.arm.getPos())
        
        # self.pin.setZ(-0.5)
        # resx = 31
        # resy = 31
        
        # self.p00 = Point3(-8, -8, 0)
        # p10 = Point3( 8, -8, 0)
        # p01 = Point3(-8,  8, 0)
        # p11 = Point3( 8,  8, 0)

        # fixeds = 1
        # gendiags = True

        # bodyNode = BulletSoftBodyNode.makePatch(info, self.p00, p10, p01, p11, resx, resy, fixeds, gendiags)
    
        # material = bodyNode.appendMaterial()
        # material.setLinearStiffness(0.4)
        # bodyNode.generateBendingConstraints(2, material)

        # bodyNode.setTotalMass(50.0)
        # bodyNode.getShape(0).setMargin(0.5)
        # self.bodyNP = self.worldNP.attachNewNode(bodyNode)
        # self.world.attachSoftBody(bodyNode)
        # self.bodyNP.reparentTo(self.charM)

        # self.pin = self.worldNP.attachNewNode(BulletRigidBodyNode('pin')) 
        # bodyNP.node().appendAnchor(bodyNode.node().getClosestNodeIndex(Vec3(11.91, -9.057, 30.947), True), self.pin.node())
       

        def make(p1):
            n = 16
            p2 = p1 + Vec3(5, 0, 0)

            bodyNode = BulletSoftBodyNode.makeRope(info, p1, p2, n, 0) 
            bodyNode.setTotalMass(5000)
            self.bodyNP = self.worldNP.attachNewNode(bodyNode)
            self.world.attachSoftBody(bodyNode)


            # force = Vec3(-5, 0, 0)
            # bodyNode.setVelocity(force)


            # Render option 1: Line geom
            # geom = BulletSoftBodyNode.makeGeomFromLinks(bodyNode)
            # bodyNode.linkGeom(geom)
            # visNode = GeomNode('')
            # visNode.addGeom(geom)
            # visNP = bodyNP.attachNewNode(visNode)

            # Render option 2: NURBS curve
            curve = NurbsCurveEvaluator()
            curve.reset(n + 2)
            bodyNode.linkCurve(curve)

            visNode = RopeNode('')
            visNode.setCurve(curve)
            visNode.setRenderMode(RopeNode.RMTube)
            visNode.setUvMode(RopeNode.UVParametric)
            visNode.setNumSubdiv(4)
            visNode.setNumSlices(16)
            visNode.setThickness(0.4)
            visNP = self.worldNP.attachNewNode(visNode)
            visNP.setTexture(loader.loadTexture('../models/concrete.jpg'))



            return self.bodyNP
        shape = BulletBoxShape(Vec3(2, 2, 6))

        # self.boxNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Box'))
        # self.boxNP.node().setMass(50.0)
        # self.boxNP.node().addShape(shape)
        # self.boxNP.setPos(10, 0, 8)
        # self.boxNP.setCollideMask(BitMask32.allOn())

        # self.world.attachRigidBody(self.boxNP.node())

        

        # self.np1 = make(self.pin.getPos())
        # self.np1 = make(Point3(0,0,0))
        # self.np1.reparentTo(self.charM) 
        # self.np1.node().appendAnchor(0, self.pin.node())
        # self.np1.node().appendAnchor(self.np1.node().getNumNodes() - 1, self.boxNP.node())
    # self.np1.reparentTo(self.boxNP)