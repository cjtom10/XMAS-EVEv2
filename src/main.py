from distutils.spawn import spawn
from enum import auto
from multiprocessing.connection import wait
from pickle import NONE
from turtle import left, right
from gltf.converter import collections
from numpy import True_
from panda3d.core import *
from panda3d.bullet import *
import math


from panda3d.direct import CMotionTrail

from direct import showbase
from direct.showbase.ShowBase import ShowBase
#set up a loading screen
from direct.gui.OnscreenText import OnscreenText,TextNode
from pandac.PandaModules import loadPrcFileData

from gpadinput import GamepadInput

loadPrcFileData("", "win-size 1280 768")
loadPrcFileData("", "sync-video t")
import sys
import time
import direct.directbase.DirectStart
loadingText=OnscreenText("Loading...",1,fg=(0.03,0.6,0.4,1),pos=(0,0),align=TextNode.ACenter,scale=0.25,mayChange=1)
base.graphicsEngine.renderFrame() #render a frame otherwise the screen will remain black
base.graphicsEngine.renderFrame() #idem dito
base.graphicsEngine.renderFrame() #you need to do this because you didn't yet call run()
base.graphicsEngine.renderFrame() #run() automatically renders the frames for you

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

import simplepbr
import gltf
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
from direct.directutil import Mopath
from direct.interval.MopathInterval import *
from mouseLook import MouseLook

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner

import itertools

base.disableMouse()
ml = MouseLook()
ml.setMouseModeRelative(False)
ml.setCursorHidden(True)
ml.centerMouse = True
ml.mouseLookMode = ml.MLMOrbit
ml.enable()
# ml.disable()

# props = WindowProperties()
# props.setCursorHidden(True)
# props.setMouseMode(WindowProperties.M_relative)
# base.win.requestProperties(props)

# To revert to normal mode:


#~ base.accept("mouse2", ml.enable)
#~ base.accept("mouse2-up", ml.disable)
base.accept("wheel_up", ml.moveCamera, extraArgs = [Vec3(0, 1, 0)])
base.accept("wheel_down", ml.moveCamera, extraArgs = [Vec3(0, -1, 0)])

base.cam.node().getLens().setFov(70.0)

globalClock.setMode(globalClock.MLimited) 
globalClock.setFrameRate(120.0)

from player import Player
from enemies import *
from kcc import PandaBulletCharacterController
from anims import Anims
from keyboardinput import KeyboardInput
from gpadinput import GamepadInput
from lvl import Level, HealthBar
from events import Events
from Config import Config
from fx import Fx   

Dodgetime = 3
jumpheight = 3
startpos = (0, 0, 10)
enemystartpos  = (0, -50, 0)

class Game(DirectObject, KeyboardInput, Anims, GamepadInput, Level, Events):

    ####3Collision maskse: 0-environment 1-characters 2-hitboxes 3-environmental ghosts (grindrail, jump pad etx)

    def __init__(self):
        # Config.__init__(self, '../config.json')
        self.shader = Shader.load(Shader.SL_GLSL, "../shaders/vert.vert", "../shaders/frag.frag")
        loadingText.cleanup()
        
        super().__init__()
        KeyboardInput.__init__(self)
        GamepadInput.__init__(self)
        gltf.patch_loader(loader)
        
        # Level.__init__(self)

        pipeline = simplepbr.init()
        pipeline.use_normal_maps = True
        pipeline.use_occlusion_maps = True


        self.setup()
        # Anims.__init__(self)
        
        Fx.__init__(self)
        self.lvl = Level(self.worldNP, self.world)
        self.enemySetup()
        # add_device_listener(
        # assigner=SinglePlayerAssigner(),
        # )
        Events.__init__(self)
        render.clearLight()
        
        self.startpos = (0,-20,0,)
        self.enemystartpos=(0,0,0)
    # now, x and y can be considered relative movements

        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)
        from direct.showbase.OnScreenDebug import OnScreenDebug
        self.osd = OnScreenDebug()
        self.osd.enabled = True
        self.osd.append("Debug OSD\n")
        self.osd.append("Keys:\n")
        # self.osd.append("escape        - Quit\n")
        # self.osd.append("gamepad start - Quit\n")
        # self.osd.append("F1            - Toggle Debug Mode\n")
        # self.osd.append("F2            - Toggle Camera Mode\n")
        # self.osd.append("R             - Reset Player\n")
        # self.osd.append("P             - Toggle Pause\n")
        self.osd.load()
        self.osd.render()
        
        self.footstep = loader.loadSfx('../sounds/footstep.wav')
        self.hitsfx =  loader.loadSfx('../sounds/hit.wav')
        self.slash1sfx = loader.loadSfx('../sounds/slash.wav')
        self.slash2sfx = loader.loadSfx('../sounds/slash1.wav')
        self.preKicksfx = loader.loadSfx('../sounds/prekick.wav')
        self.deflectsfx = loader.loadSfx('../sounds/deflect1.wav')
        self.bg = loader.loadSfx('../sounds/pa2.wav')
        # self.bg.play()

              #2d display region for huyd
        dr = base.win.makeDisplayRegion()
        dr.sort = 20
        myCamera2d = NodePath(Camera('myCam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        myCamera2d.node().setLens(lens)

        render2d = NodePath('myRender2d')
        render2d.setDepthTest(False)
        render2d.setDepthWrite(False)
        render2d.setTransparency(1)
        myCamera2d.reparentTo(render2d)
        dr.setCamera(myCamera2d)

        # aspect2d.setTransparency(1)
        # self.playerhealth = HealthBar(pos=(-.9, .9, .5, .7))
        # self.PAgauge = HealthBar(pos=(-.9, .9, .35, .45))
        self.hud = TextNode('node name')
        self.hud.setText(f"HP{self.player.health}PA{self.player.plotArmour}")
        self.hudNP = aspect2d.attachNewNode(self.hud)
        self.hudNP.setScale(0.07)
        self.hudNP.setPos(-1.5,0,-.8)

        self.text =  TextNode('observePA')
        self.textNP = aspect2d.attachNewNode(self.text)
        self.textNP.setScale(.08)
        self.textNP.setPos(-.9,0,-.6)
        self.observing = False
        self.observeRange = False
        self.observe2 = False
        # hudmo = loader.loadModel('../models/hudBlank.glb')
        # hudmo.reparentTo(render2d)
        # hudmo.setShader(self.shader)
        # hudmo.setTransparency(TransparencyAttrib.MAlpha)
        # # self.playerhealth.reparentTo(render2d)
        # # self.PAgauge.reparentTo(render2d)
        # hudmo.setZ(.85)
         
        # hudmo.setX(-.57)
        # hudmo.setScale(.5,0,0)
        # hudmo.setScale(.2)

        ml.resolveMouse()

        self.lt=False
        self.rt=False
        self.position1 = None

        self.nextTurretPos = 0
        self.occupiedTurretPos = {}
        # HACK: starts at 3, then on switch2mech, unlocks the upper level spawnpoints
        self.numTurretPos = 3

        # self.accept('t',self.spawnEnemy,extraArgs= [self.dummy2])
        # base.camera.lookAt(self.turret1.NP)
        
#######Anim names
        self.Idle = 'idle'
        self.Walk = 'walk'
        # self.angle =0# character faces this way with gamepad
        #not grinding
        # self.grindseq = Sequence()
        self.lerpCam = None

        

        # Task
        #plane so nothing falls eternal


        taskMgr.add(self.update, 'updateWorld')
        # taskMgr.add(self.updateAnim, 'animtask')
        taskMgr.add(self.debugOSDUpdater, "update OSD")
        taskMgr.doMethodLater(2, self.spawnEnemy, 'spawn enemies')

        # self.isIdle=False
        # self.isWalking = False
        # self.leftjoystick = False
        # self.idleDirection = 0
        self.lockedOn = False
        self.playerTakingHit = False
        self.lookatTurret = False

        # self.camtarg = NodePath('cam target')
        self.camtarg = loader.loadModel('../models/norm.glb')
        self.lockonPos = NodePath('lockon pos')
        # self.camtarg.reparentTo(self.worldNP)

        # self.grindseq = None
 
#         traverser = CollisionTraverser('collider')
#         base.cTrav = traverser

#         # base.cTrav = CollisionTraverser()
#         # self.accept('control', self.turret1.fire)
        

#         # Initialize the handler.
#         self.collqueue = CollisionHandlerQueue()
#         self.collHandEvent = CollisionHandlerEvent()
#         self.collHandEvent.addInPattern('%fn-into-%in')

#         self.collHandEvent.addOutPattern('%fn-out-%(tag)ih')
# ######player
#         traverser.addCollider(self.player.atkNode, self.collHandEvent)
#         traverser.addCollider(self.player.GatkNode, self.collHandEvent)
#         traverser.addCollider(self.player.parryNode, self.collHandEvent)
#         # traverser.addCollider(self.player.parryNode, self.collqueue)

        

#         traverser.traverse(render)


# #######enemies aTK HITBOXES
#         # if self.enemies:
#         for enemies in self.enemies:
#             traverser.addCollider(enemies.atkNode, self.collHandEvent)

#         for turret in self.turrets:
#             traverser.addCollider(turret.HB, self.collHandEvent)
#             traverser.addCollider(turret.atkNodeL, self.collHandEvent)
#             traverser.addCollider(turret.atkNodeR, self.collHandEvent)
           
           
#             for bullet in turret.bullets:
#                 traverser.addCollider(bullet.cNP, self.collqueue)
#                 traverser.addCollider(bullet.cNP, self.collHandEvent)
                
#                 # self.accept(f'{hb.name}-into-arena', self.bullethitwall)
#                 # traverser.addCollider(hb, queue)
#             # for key, value in turret.bullets.items():
#             #     traverser.addCollider(key.cNP, self.collHandEvent)
#         # list(self.bullets.keys())[2]

# #Events for ur guy taking hits
#         # if self.playerTakingHit ==False:
#         # if self.enemies:

#         # for geom in lvl.arenaGeoms:

#         # self.accept(f'parry-into-geom{n}', self.bullethitwall)
       

# ####3##Player takes hits
#         for bodypart in self.player.HB: 
#             for enemy in self.enemies:
#                 self.accept(f'{enemy.NP.name}attack-into-{bodypart.name}', self.takeHit, extraArgs=[bodypart.name, enemy, 0.1]) #FIX should oinly takle one hit at a time
#                 self.accept(f'{enemy.NP.name}attack-into-pdodgecheck', self.pdodge,  extraArgs=[True])
#                 self.accept(f'{enemy.NP.name}attack-out-pdodgecheck', self.pdodge,  extraArgs=[False])
#                 for bullet in turret.bullets:
#                     self.accept(f'{bullet.cNP.name}-into-{bodypart.name}', self.getShot, extraArgs=[bodypart.name, bullet, 0.1])

#             for turret in self.turrets:
#                 self.accept(f'{turret.NP.name}attackL-into-{bodypart.name}', self.takeHit, extraArgs=[bodypart.name,turret, .15])
#                 self.accept(f'{turret.NP.name}attackR-into-{bodypart.name}', self.takeHit, extraArgs=[bodypart.name,turret,.15])
                
#                 # self.accept(f'{turret.NP.name}attackL-into-parry', self.parryTurret, extraArgs=[turret, "R"])
#                 # self.accept(f'{turret.NP.name}attackR-into-parry', self.parryTurret, extraArgs=[turret, "L"])
# ########enemy takesa hits
#         for enemy in self.enemies:
#             # if enemy.isHit==True:
#             #         continue# disables multiple hits on single animation
#             # else:    
#             self.accept(f'{enemy.NP.name}attack-into-parry', self.deflectcontact, extraArgs=[enemy])
#             for bodypart in enemy.Hitbox: 
#                 # if self.player.isGrapplingGround==True:
#                 #     pass
#                 # if self.player.isGrapplingAir==True:
#                 #     pass
#                 # else:
#                     self.accept(f'attack-into-{bodypart.name}', self.hitEnemy, extraArgs=[enemy, bodypart.name])
#                     self.accept(f'Gattack-into-{bodypart.name}', self.grappleStrike, extraArgs=[enemy, bodypart.name]) #FIX should oinly takle one hit at a time
#                 # self.accept(f'parry-into-{enemy.NP.name}attack', self.deflectcontact, extraArgs=[enemy])

#         for turret in self.turrets:
#             self.accept(f'attack-into-{turret.name}hb', self.hitTurret, extraArgs=[turret])
#             self.accept(f'parry-into-{turret.NP.name}attackL', self.parryTurret, extraArgs=[turret, "R"])
#             self.accept(f'parry-into-{turret.NP.name}attackL', self.parryTurret, extraArgs=[turret, "L"])
#             for bullet in turret.bullets:
#                 # print('bullet hb name!', bullet.cNP.name)
#                 for n in range(self.lvl.geomcount):
#                     self.accept(f'{bullet.cNP.name}-into-geom{n}', self.bullethitwall,extraArgs=[bullet])
#             # # for n in 
#             #     f'bullet{n}HB'
#             #     for x in lvl.arenaGeoms:
#             #         self.accept(f'attack-into-{turret.name}hb', self.hitTurret, extraArgs=[turret])
#                 # child.ls()
                


#         ##character speed
#         # self.speed = Vec3(0, 0, 0)
#         # _____HANDLER_____
#  # shrink = LerpScaleInterval(self.worldNP, 3, .3)
# #####Collision events   
# # =   
#     def hitEnemy(self,enemy,part,entry):#actor
#         if enemy.isHit==True:
#             print(enemy.NP.name,'is already hit')
#             return
#         print(f'{enemy.NP.name} gets hit at ', part)
#         # print(entry)
#         # self.attached = False
#         # self.hitcontact = True
#         # self.atkNode.node().clearSolids()
#         enemy.isHit = True
#         self.hitsfx.play()
#         enemy.health-=.25
    
#         # for node in enemy.Hitbox:
#         #     node.node().clearSolids()
#             # print('clear', node)
#         # enemy.solidsCleared = True    

#         def twitch(p):
#             #TODO add an anim instead of this
#             torso=enemy.model.controlJoint(None, "modelRoot", "torso")
#             torso.setP(p)
#         def end():
#             self.hitcontact=False
#        #stop = Func(enemy.model.stop())#enemy anim stop
#         a = Func(twitch, 30)
#         b = Func(twitch, 0)
#         p = Func(self.player.animseq.pause)#### player hitstopping
#         r = Func(self.player.animseq.resume)
#         e =Func(end)
        
#         hitseq = Sequence(a, p, Wait(.1),b, r,e).start()
#         if enemy.health<=0:
#             self.enemydeath(enemy)
#             self.player.gainPlotArmor(.05)
#         # shrink.start()
#     def grappleStrike(self, enemy, part, entry):
#         print('grapple strake', enemy,'at', part)

#     def parryTurret(self, turret, side, entry):
#         print(f'successfuluy parried {turret.name}. it is stagger now')
#         turret.staggered(side)
#     def hitTurret(self, turret, entry):
#         # print('hit',turret.name)
#         # turret.health -= .25
#         # if turret.health<=0:
#         #     # self.enemydeath(turret)
#         #     turret.dieSeq()
#         self.hitsfx.play()

#         if turret.isHit==True:
#             print(turret.NP.name,'is already hit')
#             return
#         print(f'{turret.NP.name} gets hit')
#         # print(entry)
#         # self.attached = False
#         # self.hitcontact = True
#         # self.atkNode.node().clearSolids()
#         turret.isHit = True
#         self.hitsfx.play()
#         turret.health-=.25
    
#         # for node in enemy.Hitbox:
#         #     node.node().clearSolids()
#             # print('clear', node)
#         # enemy.solidsCleared = True    

#         def twitch(p):
#             #TODO add an anim instead of this
#             # torso=enemy.model.controlJoint(None, "modelRoot", "torso")
#             turret.model.setP(p)
#         def end():
#             self.hitcontact=False
#             turret.isHit = False
#        #stop = Func(enemy.model.stop())#enemy anim stop
#         a = Func(twitch, 30)
#         b = Func(twitch, 0)
#         p = Func(self.player.animseq.pause)#### player hitstopping
#         r = Func(self.player.animseq.resume)
#         e =Func(end)
        
#         hitseq = Sequence(a, p, Wait(.1),b, r,e).start()
#         if turret.health<=0 and not turret.isDying:
#             turret.dieSeq()
#             self.player.gainPlotArmor(.1)

#     def bullethitwall(self,bullet, entry):
#         # print(bullet.name, 'hits wall')
#         # bullet.cNP.node().clearSolids()
#         # bullet.HBattached = False
#         bullet.hit()
#         # turret_name = str(entry).split('/')[2]
#         # turret = [t for t in self.turrets if t.name == turret_name][0]
#         # turret.reset_bullet(entry)
        
#         # print("i found turret", turret.name)


#     def getShot(self,name,bullet,  amt, entry):
#         # if self.player.isStunned
#         bullet.hit()
#         # self.player.iframes()
       
#         def twitch(p):           
#             torso=self.player.charM.controlJoint(None, "modelRoot", "torso")
#             torso.setP(p)
#         def end():
#             # torso.removeNode()
#             self.player.charM.releaseJoint("modelRoot", "torso")
#         #     self.hitcontact=False
#        #stop = Func(enemy.model.stop())#enemy anim stop
#         a = Func(twitch, 30)
#         b = Func(twitch, 0)
#         # p = Func(self.player.animseq.pause)#### player hitstopping
#         # r = Func(self.player.animseq.resume)
#         e =Func(end)
        
#         hitseq = Sequence(a,  Wait(.1),b,e).start()
#         print('plaayrr gets shot. Oh no!', name)

#     def takeHit(self, name, enemy,amt, entry):
#         """amt is the amount opf damage, varies from enemy + attack"""
#         if enemy!=None:
#             if enemy.hasHit ==True:
#                 print('im alrteady hit gd')
#                 return
#             self.player.takeHit()
#             # enemy.atkNode.node().clearSolids()
#             enemy.hasHit=True 
#             print(  enemy.name, 'hits players', name)
#         # self.player.takeHit()
#         netDmg = amt - self.player.plotArmour

#         if self.player.plotArmour > 0:
#             self.player.plotArmour -= amt
#             if amt> self.player.plotArmour:
#                 self.player.health -= netDmg
#         else:
#             self.player.health -= amt        
#         print(f'player take {amt} damage', 'hp-', netDmg)
            
#         # print(entry)
#         # self.dummy2.atkNode.node().clearSolids()
        
#         # if self.player.health<=0:
#         #     self.doExit()
#         #add hitstopping,for enemy, sfx, etc
#         ####Nered to add poise check then see whether or not character gets stunned
       

#     def deflectcontact(self,enemy, entry):
#         print(f'player defelects {enemy.name}', 'enemyposture:',enemy.posture)
#         if enemy.hasHit ==True:
#                 print('im alrteady hit parrued')
#                 return
#         enemy.hasHit = True
#         #pause anims opn enemy/p[layer, play recoil anims]
#         #deplete posture from enemy, if posture -== 0 enemy enters stun
#         self.player.parryNode.node().clearSolids()
#         enemy.atkNode.node().clearSolids()
#         # self.player.iframes
#         self.deflectsfx.play()

#         self.deflected('recoil1',enemy)

#     def pdodge(self,x, entry):
#         self.character.perfectDodge = x
#         print('pdodge',self.character.perfectDodge)
#####camera
    def resetCam(self):
        # base.camera.removeNode()
        
        initcamPos = Point3(0,-15, 5)
        base.camera.setPos(startpos)
        base.camera.setPos(initcamPos)
        
        # print('cam reset onfoot')
        # base.camera.s

    def recenterCam(self):
        if self.player.character.state == "mech":
            # print('recenter cam not valid for mech')
            return
            # direction = self.character.char.getH()
        # if self.player.character.state =="mech":
        direction = self.character.movementParent.getH()
        targ = self.charM.getHpr(render)
        # base.camera.setHpr(self.charM, 0,0,0)
        i = LerpHprInterval(base.camera, .2,targ ).start()
        # if self.character.movementState=='wallgrab' or self.character.movementState == 'wallgrab':
        #     print('wall run recenter cam')
        #     self.wallruncam=True
    def doExit(self):
        self.cleanup()
        sys.exit(1)
    # def AUp(self):
    #     ####end vaulting
    #     if self.character.vaulting!=True:
    #         return
    #     else:
    #         self.character.endVault()
####3Character actions
    def checkposition(self):
        self.position1=self.character.getPos(render)
    def deltapos(self):
        p2= (self.character.getPos(render)-self.position1).length()
        print('length:', p2)



    def actionStickEvent(self):
        if self.player.pauseframe==True or self.player.buffer == True:
            print('do a little flip in this direction', 'X',self.leftX, 'Y', self.leftY)
        self.stickEvent=False
        self.stickEventTriggered=True
    def actionlb(self):
        if self.character.movementState in self.character.airstates:
            self.player.doDeflect(state='air')
        self.player.doDeflect()
    def actionrb(self):
        # print('p2e',self.p2e)
        # self.bicepbreak(self.dummy2)closest
        # ml.disable()
        # self.recenterCam()
        self.lockOn()

    def lockOn(self):
        # self.resetCam()
        if self.p2e>10:
                    self.lockedOn = False
                    print('no enemies', self.p2e)
                    return
        self.lockedOn^= True
        if self.lockedOn==True:
            # print('endlockon')
            if self.lerpCam!=None:
                self.lerpCam.pause()
            self.lerpCam = None
    def actionX(self):
        # self.finisherCheck()
        # print('closest enemy: ', self.closest)
        # if self.player.isGrappling == True:
        #     self.player.endGrapple()


            # return
        # self.finisher(self.dummy3)
        # return
        self.player.doSlashatk()

        

        # if self.atx!=None and len(self.atx) >=4:
        #             print('combo limit')
        #             return
        # if self.character.movementState =="dodging":
        #     print('dodge attack x')
        #     return
        # if self.character.movementState in self.character.airstates:# also if air attacking
        #     print('air attack x')
        #     self.smashAttack()
        # if self.character.isAttacking == True and self.attackqueue>0:
        #     # if self.attackQueued==True:
        #     #     print('attack already queued')
        #     if self.attackQueued ==False:
        #         # print('queue attack x- do slash # ', self.attackqueue+1)
        #         self.qdatk = 'slash'
        #         self.attackQueued=True
        # else:
        #     # print('shouldnt get here if ur dodging....')
        #     self.slashAttack()
        #AIR SL;ASH ATTACK HERE
    def actionA(self):
        print('actionA')

        if self.character.movementState == 'grappling':
            print('cant jump, grappliung')
            return


        # if self.player.state =='OF':
        #     if self.observeRange == True:
        #         # if self.observing == False:
        #         self.observePilotArmor()
          
        self.player.doJump()
    def actionB(self):
        print('actionb')
        if self.player.state == 'OF':
            self.player.evade()
        if self.player.state == 'mech':
            self.player.mechevade()
    def actionY(self): 
        self.player.doStabatk()
        # if self.atx!=None and len(self.atx) >=4:
        #             print('combo limit')
        #             return
        # #make enemies hitable again
        # # for enemy in self.enemies: 

        # if self.character.movementState =="dodging":
        #     print('dodge attack y')
        #     return
        # if self.character.movementState in self.character.airstates:# also if air attacking
        #     print('air attack y')  
        # if self.character.isAttacking == True and self.attackqueue>0:
        #     # if self.attackQueued==True:
        #     #     print('attack already queued')
        #     if self.attackQueued ==False:
        #         print('queue attack x- do slash # ', self.attackqueue+1)
        #         self.attackQueued=True   
        #         self.qdatk = 'stab'  
        # else:
        #     self.stabattack()
    def actionRT(self, value):
        self.rt = True
        # print('action rt', value)
    def actionLT(self, value):
        print('current grapple:', self.player.currentGrapple,'last:', self.player.lastGrapple )
        if self.player.currentGrapple!=None:
            # print('already grapple', self.player.currentGrapple)
            return
        self.lt = True
    
        
        if self.GPcheck()[0] ==0 :
            print('no points')
            return
        self.player.currentGrapple = self.GPcheck()[0]
        # print('curr g', self.player.currentGrapple)
        
        # self.player.currentGrapple = self.lvl.grapplePoints[0] #TESTING
        self.player.doGrapple(self.player.currentGrapple, ground=self.GPcheck()[1])
        # self.player.processGrapple()
    def LTUp(self):
        self.lt = False
        # if self.player.currentGrapple!=None:
        if self.player.isPerched:
            self.player.endGrapple(jump = True)
        if self.player.isGrapplingGround == True or self.player.isGrapplingAir == True:
            self.player.endGrapple(jump = False)
    def RTUp(self):
        self.rt = False

    def doCrouch(self):
        self.character.startCrouch()
    
    def stopCrouch(self):
        self.character.stopCrouch()
    
    def startFly(self):
        self.character.startFly()
    
    def stopFly(self):
        self.character.stopFly()
    def switch2mech(self):
        self.player.state = 'mech'
        # self.player.character.setPos(self.lvl.staticMech.getPos(render))
        self.lvl.staticMech.detachNode()
        # HACK: add new viable turret positions
        self.numTurretPos = 5
        self.player.setUpMech()
######Tasks here    
    def timer(self,  task):
        return task.cont
        # if task.time<time:
        #     return task.cont
        # else:
        #     return task.done

    def processInput(self, dt):
        
        self.speed = Vec3(0,0,0)
        omega = 0.0
        
        v = 24.0
        vx = .50
        vy = .50
        vz = .5
      
        # if inputState.isSet('run'): 
        #     v = 15.0
        # if self.character.movementState != "attacking":
        
        # if self.character.isAttacking ==False and self.character.isParrying ==False:
        # if self.character.movementState!="attacking":
########KEYBOARD
        # if self.character.movementState == "wallgrab":
        #     self.wallgrabInput()
        #     self.speed = 0
        #     return
        if inputState.isSet('forward'):
            self.speed.setY(v)
        if inputState.isSet('reverse'): 
            self.speed.setY(-v)
        if inputState.isSet('left'):    
            self.speed.setX(-v)
        if inputState.isSet('right'):   
            self.speed.setX(v)

########CONTROLLER
        if self.gamepad:
            # print('lt value', self.trigger_l.value)
            if self.trigger_l.value > .3 and self.lt == False:
                self.actionLT(self.trigger_l.value)
            if self.trigger_l.value<.3 and self.lt ==True:
                self.LTUp()
                
            if self.trigger_r.value > .3:
                self.actionRT(self.trigger_r.value)
            if self.trigger_r.value<.3 and self.rt ==True:
                self.RTUp()
            
            self.leftjoystick =False
            self.joystickwatch()
            def stickEventwatcher():
                if self.leftjoystick==False:
                    self.stickEventTriggered=False
                if self.stickEventTriggered==True:
                    return
                if self.stickEvent == True:
                    # print('stick eve4nt already happened')
                    return
                if self.leftjoystick==True:
                    print(self.leftjoystick)
                    self.stickEvent=True
                    self.actionStickEvent()
                    return
                elif self.leftjoystick == False:
                    self.stickEvent=False
            stickEventwatcher()
      
            x = self.player.leftX / 10
            y = self.player.leftY / 10
           
            # print(self.left_x.value, self.left_y.value)
            # h = math.atan2(-self.left_x.value, self.left_y.value )
            h = math.atan2(-x, y)
            self.player.angle = math.degrees(h) 
            # print(self.player.angle)
            # vx*= round(self.left_x.value) * 24 
            # vy*= round(self.left_y.value) * 24
            # if self.character.wallJump ==True and self.trigger_r.value > .1:
            #     self.character.movementState = "wallrun
            vx*= self.left_x.value * 24 
            vy*= self.left_y.value * 24
            vz*= (self.trigger_r.value - self.trigger_l.value) * 24
            if vz>0:
                self.character.ascending = True
            if vz <=0:
                self.character.ascending = False
            # print(self.leftX, self.leftY)
            if self.player.state == 'OF':
                if self.player.character.movementState == "jumping" or self.player.character.movementState == 'falling':
                    vx *=.2
                    vy *= .2


            self.speed.setX(vx)
            self.speed.setY(vy)
            if self.player.state == 'mech':
                if self.character.movementState == "dodging" or self.character.movementState == "finisher" :#or self.player.isStunned:
                    return
                self.speed.setZ(vz)
                self.character.mechVec = self.speed
                # print(self.trigger_r.value)
                # if self.trigger_r.value == 0:
                #     self.character.movementState = 'falling'
                # print('speed', self.speed, 'mechvec', self.character.mechVec)
                # print(self.speed)

        # if self.player.isStunned:
            
        # if self.character.movementState!="attacking" and self.character.movementState  not in self.character.nonInputStates:
        if self.player.character.movementState=="attacking" or self.player.character.movementState   in self.player.character.nonInputStates: #or self.player.isStunned:
            self.speed = Vec3(0,0,0)
            # self.character.setAngularMovement(omega)
            # self.character.setLinearMovement(self.speed, True)
        self.player.character.setAngularMovement(omega)
        self.player.character.setLinearMovement(self.speed, True)
    def wallgrabInput(self, dt):
        if self.gamepad:
            self.joystickwatch()
    def GPcheck(self, Ylimit = -10, Zlimit = 50, Dislimit = 100):
        """find closest grappleable point- give closest GP, is it obstructed, is it in  view of camera? show indicators for active"""
        #check for air/ground
        if self.character.movementState in self.character.airstates:
            ground = False 
        else:
            ground = True
            DisLimit = 200
            # print('z diff', )
        # find closest
        playerpos = self.charM.getPos(render)
        gps = []
        if self.player.lastGrapple!=None:
            filteredPoints = filter(lambda x: x != self.player.lastGrapple, self.lvl.grapplePoints)
        else:
            filteredPoints = self.lvl.grapplePoints
        # for i in self.lvl.grapplePoints:
        for i in filteredPoints:
            #point is invalid if it is 1) behind cam, or z dis > 20
            relY = i.getY(base.camera)
            relZ = i.getZ(base.camera)

            if relY<Ylimit:
                continue
            if abs(relZ)>Zlimit:
                continue
            if ground == True and relZ > 10: #should be able to ground grapple p[oints too high]
                continue
            dis = (playerpos-i.getPos(render)).length()
            if dis > Dislimit:
                continue

            gps.append(dis)
        if not gps:
            print('no points')
            return [0,False]
        closest = min(gps)

######3check if closest matches the previous point
        

####matche closest to grapple point
        for x in self.lvl.grapplePoints:
         
            dis = (playerpos-x.getPos(render)).length()
            if closest == dis:
                gp = x

                # if gp == self.player.currentGrapple:
                #     closest = min
                # self.player.currentGrapple = x
                
        if not gp:
            print('no points except the opne u just grappled to')
            return [0,False]

        #check for obstructed path
        def sweep():
            mask = BitMask32.bit(2)
            fr = TransformState.makePos(self.charM.getPos(render))
            to = TransformState.makePos(gp.getPos(render))
            shape = BulletSphereShape(0.5)
            penetration = 0.0
            result = self.world.sweepTestClosest(shape, fr, to, mask)
            if result.hasHit():
                return True
        if sweep() == True:
            print('path obstructed')
            return [0,False]

        print('the grapple point:', gp)

        if gp not in [item.NP for item in self.enemies]:
            return [gp, ground]  
        print('enemy being grappled')
        # self.player.GatkNode.node().clearSolids()# maker sure u dont launch anyone twice
        enemymatch = self.findEnemy(gp)
     
        if enemymatch.launchSeq!=None:
            if enemymatch.launchSeq.isPlaying():
                enemymatch.launchSeq.pause()
                enemymatch.launchSeq = None
                print('pausing enemy')
        enemymatch.pause(pos = gp.getPos(render))
            
          

        return [gp, ground]   
    def findEnemy(self, gp):
        """match gp.NP to enemy in self.enemies"""
        enemy = next(item for item in self.enemies if item.NP == gp) 

        return enemy
            # else:
            #     print('no grapplepoints')
                # gp=x
                # print('x',x)
        # self.currentGrapple = gp
                # print('current grapple:', self.lvl.grapplePoints[0], 'gp', gp)
      

            
            # if self.left
    # def wallGrabcheck(self):
    #         #Need to add timer  here
    #         def end():
    #             print('end wallgrab or run')
    #             self.wallruncam = False
    #             self.character.movementState = "endaction"
    #             # self.character.wallRun[0] = None
    #             self.character.WGAngle = None
    #             self.character.wallray.reparentTo(render)
    #             self.character.wallray.setPos(self.charM, (0,20,20))

    #             # self.character.wallRunVec = 0
                
    #             # taskMgr.remove('wgtimer')
    #             # self.wallGrabTimer=None
    #         # print(self.character.wallJump, 'WC',self.character.wallContact)
            
    #         if self.character.wallContact == True and self.trigger_r.value > .1:
    #             self.wallJumpEnabled = True
    #         else:
    #             self.wallJumpEnabled = False
    #         if self.character.movementState == 'wallgrab':
    #             # if self.wallGrabTimer == None:
    #             #     self.wallGrabTimer = taskMgr.add(self.timer,'wgtimer')

                
    #             # print(self.character.WGAngle)
    #             # print(self.character.wallRun)
    #             # if self.wallruncam==False:
    #             #     self.recenterCam()
    #             if self.leftValue != 0:
    #                 self.character.wallRun[4] = 'wallrunning'
    #                 # self.character.wallray.reparentTo(self.charM)
    #             elif self.leftValue == 0:
    #                 self.character.wallRun[4] = 'wallgrabbing'

    #             # print('wg angle',self.character.WGAngle)
                
    #             if self.character.WGAngle == None:
    #                 self.character.WGAngle = self.character.wallRun[0]

    #             # if self.character.wallRun[0]== None:
    #             self.charM.setH(render, self.character.WGAngle)
    #             # self.character.movementParent.setH(render, self.character.WGAngle)
    #             self.character.wallspeed = self.leftValue * 3

    #         if self.character.wallJump == True:
    #             return
    #         # self.character.d2wall<2self.character.nearWall ==True
    #         if  self.character.wallContact == True and self.character.nearWall == True and self.trigger_r.value > .1:# and self.character.canWallGrab==True: #and self.character.canWallGrab ==True:
    #             if self.character.movepoints!=3:
    #                 self.character.movepoints = 3
    #             self.character.movementState = "wallgrab"
    #             # self.character.canWallGrab = False
                
    #         if self.character.movementState == "wallgrab": 
    #             if self.trigger_r.value <.1 or self.character.nearWall == False:#self.character.d2wall>2 :
    #                 print('its over')
    #                 end()

    def update(self, task):
        """Updates the character and listens for joystick-activated events"""
        if self.player.health<=0:
            print('ur dead')
            self.doExit()
        
        # def observe():
        #     o = self.lvl. observePA.getPos(render)
        #     e = self.lvl.enterPA. getZ(render)
        #     dis = abs((self.player.character.movementParent.getPos(render) - o).length())
        #     mechEvent = self.player.character.movementParent.getZ(render) -e
            


        #     if dis < 15:
                
        #             if self.observing == False:
        #                 self.observeRange = True
        #                 self.text.setText('press x')
        #     else:
        #         self.observing = False
        #         self.text.clearText()

        #     if mechEvent <0:
        #         if self.player.plotArmour== 1:
        #             self.switch2mech()
        #         elif self.player.dead == False:
        #             print(' ur dead bozo')
        #             self.player.death()

        # if self.player.state == 'OF':
        #     observe()
        #check for bullets hitting the arena
        # for entry in self.collqueue.entries:
        #     # print(entry.getFromNodePath().name)
        #     if (str(entry.getIntoNodePath()).split('/')[2]) =='arena':
        #         print(entry.getFromNodePath().name) 
        #         if 'bullethb' in entry.getFromNodePath().name:
        #             print(entry.getFromNodePath(),'contact w arena')
        #             self.bullethitwall(entry.getFromNodePath())
        #     # if entry.getFromNodePath().name
            # print('entry',entry)

        # queue = CollisionHandlerQueue()
        # # traverser.traverse(render)
        # print('q entries')
        # queue.getNumEntries()
        # queue = CollisionHandlerQueue()
        # for entry in queue.entries:
        #     print(entry)        
        # print(self.character.movementState)
        # print('attack queue', self.attackqueue, 'a/ttack queued', self.attackQueued)
        # print('jumpdir', self.character.jumpdir)
        
        # print('dodge dir', self.character.dodgedir, self.charM.getQuat().getForward())
        # print(self.character.movementState)
        # c = self.character.movementParent.getRelativeVector(self.charM, (0,1,0))
        # s = Vec3(self.leftX, self.leftY, 0 )
        # wr = self.character.wallray.getPos(self.character.movementParent)
        
        # print(c, s)

        # if self.character.enableVaulting==True and self.leftjoystick == True:
        #     self.vaultUp()
        # v = render.getRelativeVector(self.charM, (0,20,0))
        # print(v.x, v.y, 'I',self.leftX,self.leftY)
        # print(render.getRelativeVector(self.charM, (0,20,0)))
        # print(self.charM.getQuat(render).getForward() * 20, self.charM.getH(render))#self.character.dodgedir)
        # print('mvtstate',self.character.movementState, self.character.canWallGrab, self.character.d2wall)
        # print(self.trigger_r.value)
        # totaltime = round(ClockObject.getGlobalClock().getLongTime())
        # # print(self.dummy2.hasHit)
        # print('total time',totaltime)
        # print(self.trigger_l.value)
        # print('characterH', self.angle, 'camH', base.camera.getH(self.charM))
        # for enemy in self.enemies:
        #     print(enemy.name,'is hit?', enemy.isHit)
        # print('attached',self.attached, 'hit contact', self.hitcontact)
        # print('parrying', self.character.isParrying)#, 'attacking:,', self.character.isAttacking)
        ###Record enemyt positions for lock on
        # self.enemypos.append(self.dummy.NP.getPos())

        # print('self.angl;e', self.player.angle)
        # print('is atacking',self.character.isAttacking,'atk queue', self.attackqueue)
        # print('jumpdir:',self.character.jumpdir, 'grindvec', self.character.grindvec)
        # print(self.character.movementParent.getH())
        # print(self.character.movementState)# self.character.dodgedir)
        # print(self.angle)
        # print(self.character.smash1)
     
  ######USE THIS FOPR PERFECT DODGE   
        # result = self.world.contactTest(self.character.__crouchCapsuleNP.node())
        # for  contact in result.getContacts():
        #     node = contact.getNode0()
        #     print(node)

        dt = globalClock.getDt()
        # self.prevGroundState = self.groundstates
        # self.prevAirState = self.airstates
        # dont do this if wallgrab or deadzone
        # self.joystickwatch()
        # print(self.character.movementState)
        
        # if self.character.movementState not in self.character.nonInputStates:
        # if self.character.movementState !='wallgrab' or self.character.movementState !='vaulting':
        # if self.character.movementState == "finisher":
        #     return
        # print('m,mvmt state', self.character.movementState)
        self.processInput(dt)
        self.player.playerTask(dt)
            # print(self.inputDelay)
            # print('setting speed')
        # if self.character.movementState in self.character.nonInputStates:
        #     print('dont set speed')


        # if self.atx!=None:
        #     print(len(self.atx))        
#         oldCharPos = self.character.getPos(render)
#         if self.character.movementState != 'attacking': #and self.character.movementState != 'grinding':
#             self.character.setH(base.camera.getH(render))
#             # print('setting H')
# ########check state changes
#         self.previousState = self.character.movementState
#         self.character.update() # WIP
#         self.currentState = self.character.movementState
#         # print('curtrent state',self.character.movementState, 'prev',self.previousState)
#         if self.character.movementState == 'falling' and self.previousState == 'ground':
#             self.character.ground2fall(5)

# ########Character set character direction
#         if self.character.movementState == "landing":
#             self.idleDirection = self.charM.getH(render)

#         if self.previousState != self.currentState and self.character.isdodging == False and self.currentState == "ground" and self.previousState != "Falling":
#             self.enterIdle()

#         #             self.charM.stop()      
#         if self.character.movementState == "ground" or self.character.movementState =="attacking" and self.character.isAttacking ==False:
#             if self.character.isdodging == False:
#                 self.isIdle = False
#                 self.isWalking = False
#                 # self.attackWalking = False
            
#             if self.character.movementState!= "attacking":
#                 self.GroundStates()

#         if self.character.movementState == "jumping" or self.character.movementState == "falling":
#         # if self.character.movementState in self.character.airstates:
#             self.isIdle = False
#             self.isWalking = False
#             # self.attackWalking = False
#             self.AirStates()
          
#         # print('State:',self.character.movementState)
# ########FOR ANIMS
    
#         newCharPos = self.character.getPos(render)
#         self.delta = (newCharPos - oldCharPos) #+ 1
        
        self.world.doPhysics(dt, 4, 1./120.)
        
        # ml.orbitCenter = self.character.getPos(self.worldNP)
        # ml.orbitCenter = self.camtarg.getPos()

        # camDist = base.camera.getPos(self.character.movementParent)
        # camDistX = base.camera.getX(self.character.movementParent)
        # camDistY = base.camera.getY(self.character.movementParent)
        # camDistZ = base.camera.getZ(self.character.char) * 100
        # self.wallGrabcheck()

        # if self.character.movementState == "attacking" or self.character.movementState == "dodging":
        #     self.isWalking = False

        self.camtask()
        # self.updateAnim()

        self.closestEnemy()
        # self.playerhealth.setHealth(self.player.health)
        self.hud.setText(f"HP{round(self.player.health*100)}\nPA{round(self.player.plotArmour*100)}")

        self.targetNode.setPos(self.character.movementParent.getPos(render))
        
        return task.cont

        # self.charM.setH(render, self.direction)
    def camtask(self):#, task):###move camera stuff here
        #straighten cam
        # self.lvl.arenaSensorcheck(self.lvl.sensor1)
        #     return
        #     if 100> base.camera.getH(self.charM) <80:
        #         print('ml x += .5')
        if self.player.animspecial==True:
            return
        ml.orbitCenter = self.player.character.getPos(self.worldNP)
        cambuffer = NodePath('cambufffer')
        camPos = base.camera.getPos(render)
        cambuffer.setPos(self.player.character.getPos(render))
        cambuffer.reparentTo(self.player.character.movementParent)
        # if ur in hallwayu
        if self.lookatTurret == True:
            # base.camera.setZ(8)
            base.camera.lookAt(self.turret1.NP)
            
        # if ml.disabled == True and self.character.movementState != "grinding":
        #     ml.enable()
        #     ml.disabled =False
            # print('enable mouse')

        ######Lock on cam:

        def moveCam(node):

            node.setPos(camPos + self.player.delta)
        
        moveCam(base.camera)
        # #use triggers torotate
         #####Gamepad camera control
        if self.gamepad:
            ##invert
            # if ml.toplimited !=True: 
            #     ml.camY = - round(self.right_y.value)
            # if ml.toplimited is True and ml.camY > 0:
            #     ml.camY = 0
            # else:
            self.trigger_l = self.gamepad.findAxis(InputDevice.Axis.left_trigger)
            self.trigger_r = self.gamepad.findAxis(InputDevice.Axis.right_trigger)
            
            ml.camY = - round(self.right_y.value)
            ml.camX = round(self.right_x.value) 
            camh =base.camera.getH(self.player.charM)
            #straighten cam here
            # if self.player.isWalking ==True:
            #     # print(abs(self.right_x.value))
            #     if abs(self.right_x.value) < .2:
            #     # print(ml.camX, ml.camY,'cam h', base.camera.getH(self.charM))
            #         if 60 < camh <120: #
            #             ml.camX += .8
            #         if -120 < camh <-60: #
            #             ml.camX -= .8
        
        moveCam(base.camera)  
  
        mp = self.player.character.movementParent.getPos(render)
        # self.camtarg.setY(self.charM, 0)
        targ = self.camtarg.getPos(render)
        base.camera.setPos(targ)
        if self.character.movementState =="falling":
            # base.camera.setPos(camPos)
            # base.camera.lookAt(self.character.movementParent)
            ml.camY += .1
        dis = (mp - targ).length()
        t = .2# / (dis+1)#*dis#/ math.dist
        # print(t)
        # if self.character.movementState != 'grinding':
        camlimit = base.camera.getP(self.character.movementParent) 
        # print(camlimit)
        if camlimit < -70:
            ml.toplimited = True
        elif camlimit > 6:
            ml.bottomlimited = True
        else: 
            ml.toplimited = False
            ml.bottomlimited = False

        if self.lerpCam!=None:
            if self.lerpCam.isPlaying():
                return    
    #####LOCK ON CAM
        if self.lockedOn==True:

            direction = self.character.movementParent.getH()
            targ = self.charM.getHpr(render)
            # base.camera.setHpr(self.charM, 0,0,0)
            
    

              # base.camera.lookAt(self.camtarg)
            self.camtarg.setH(self.charM.getH(render))
            base.camera.setY(-5)
            # self.lockonPos.reparentTo(self.charM)
            # self.lockonPos.setY(-5)
            # base.camera.setH(self.charM.getH())
            self.camtarg.setPos(self.midpoint)
            base.camera.setY(base.camera, -(self.p2e))
            # base.camera.reparentTo(self.charM)
            # base.camera.setPos(self.lockonPos.getPos(render))
            # print('player2enemy',self.p2e)
            
            if self.lerpCam==None:
                self.lerpCam =Sequence(LerpPosInterval(self.camtarg, 0.2, self.midpoint, name='lockoncam')).start()
                # self.lerpCam
            
            return# task.cont
              
        
######### FIX THE JITTERS HERE BRO V
        if dis > 2 and self.lerpCam == None: #and self.isIdle == False:

            self.lerpCam = Sequence(LerpPosInterval(self.camtarg, t, mp)).start()
            # self.lerpCam.start()
            return #task.contmovetarget

        if dis <2 and self.lerpCam != None: #and self.isIdle == True:
            
            self.lerpCam.pause()
            self.lerpCam = None
            return #task.cont
        
        # print(base.camera.getH())
        return# task.cont
        # if self.character.movementState == "falling"
    def updateEnemies(self, task):
        # print('acitve enemies', self.enemies)
        # print('dummy current behavior', self.dummy.currentBehavior)

        if self.enemies:
            for enemy in self.enemies:
                # if enemy.active ==True:   
                if enemy.type == 'Basic':
                    enemy.updateBasic()

    
        
        et = task.time
        turretDT = globalClock.dt
        # frametime = globalClock.getFrameTime()
        for turret in self.turrets:
            if turret.isSpawning or turret.isDying:
                continue
            if not turret.active:
                self.spawnTurret(turret)
                continue
            turret.update(turretDT,et)
     #-0------for testing purposes-------\
     # need to mkae this update AUTomticallly
        # self.dummy2.moveTarget = self.enemyTargets[0].getPos(render)
        self.dummy.moveTarget = self.enemyTargets[1].getPos(render)
        self.dummy3.moveTarget = self.enemyTargets[0].getPos(render)


        # print('dummy2 behaviour', self.dummy2.currentBehavior,self.dummy2.speed)
        # print(self.dummy2.d2p)
        # print('dummy1 behavior', self.dummy.currentBehavior)
        return task.cont       
    def closestEnemy(self):
            """find closestenemy for lock on"""
            # print('dist2enemy',self.p2e, 'closest enemy', self.closest)
            
            # print(self.activeEnemiesPos)
            playerpos = self.charM.getPos(render)
            ####enemies move to these points
            target1 = (playerpos.x, playerpos.y +2, playerpos.z)


            ##Have enemies track target
            if self.enemies:
                for enemy in self.enemies:
                    enemy.lookTarget = playerpos
            for turret in self.turrets:
                turret.lookTarget = playerpos
                
            # eif self.character.movementState!='dodging':
            #     self.dummy2.tracktarget()
            # self.dummy.lookTarget = playerpos
            # print(self.p2e)
            # print('closest eenemy', self.closest)




            if self.closest == None:
                v = self.activeEnemiesPos.values()
                closeval= min(v, key=lambda pt: (playerpos - pt).length())
                for key, value in self.activeEnemiesPos.items():
                        if closeval==value:
                            self.closest = key
            def updateEnemypos():
                
                for name in self.activeEnemiesPos:
                    self.activeEnemiesPos.update({name:name.getPos(render)})
                if self.closest!=None:
                    pos = self.activeEnemiesPos.get(self.closest)
                    self.p2e = abs((playerpos-pos).length())
                    self.midpoint = Point3((playerpos.x+pos.x)/2,(playerpos.y+pos.y)/2,(playerpos.z+pos.z)/2)
                    
            updateEnemypos()
            
            if self.lockedOn ==True:
                if self.p2e>15:
                    self.lockedOn = False
                a = self.charM.getX(render) - self.closest.getX(render)
                b = self.charM.getY(render) - self.closest.getY(render)

                h = math.atan2(a,-b )
                angle = math.degrees(h) 

                # self.closest = closest
                self.player.charM.setH(render, angle)
                self.camtarg.setH(render, angle)
                # base.camera.setH(angle)

                self.crosshair.reparentTo(self.closest)
                self.crosshair.setPos(self.charM.getPos())
            else:
                self.crosshair.detachNode() 
                self.closest = None   
            return     

  
    
    def cleanup(self):
        self.world = None
        self.worldNP.removeNode()
        
    def setup(self):
        self.worldNP = render.attachNewNode('World')

        # World
        self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())



        
        # shape = BulletBoxShape(Vec3(1, 1, 2.5))
        # self.ghost = self.worldNP.attachNewNode(BulletGhostNode('Ghost'))
        # self.ghost.node().addShape(shape)
        # self.ghost.setPos(-5.0, 0, 10)
        # self.ghost.setCollideMask(BitMask32.allOn())
        # self.world.attachGhost(self.ghost.node())
        
        # taskMgr.add(self.checkGhost, 'checkGhost')

###########Char +_ enemoies here

        initcamPos = Point3(0,-15, 7)
        # self.character = PandaBulletCharacterController(self.world, self.worldNP, 4, 1.5,.5, 1,)
        self.enemies = []

        # startpos = (0,-200,0)
        startpos = (40,-20,0)
        startH = 90
        self.player = Player(self.world, self.worldNP, self.gamepad, self.enemies, 'OF')
        self.character = self.player.character
        ##
        # self.parryM.reparentTo(self.worldNP)
        self.charM =self.character.char
        
        self.player.character.setPos(render, startpos)
        base.camera.setPos(startpos)
        base.cam.setPos(initcamPos)
        # base.camera.setP(render, -90)

        self.player.character.setH(render, 90)
        base.camera.setH(-100)
        # base.cam.setPos(initcamPos)
        # base.camera.setP(render, -90)
        # # self.charlight = PointLight('character')
        # self.charlightNP = self.character.movementParent.attachNewNode(self.charlight)
        # self.charlight.setAttenuation((0.1, 0.04, 0.0))
        # render.setLight(self.charlightNP)
        # self.charM.setShaderAuto()
        # self.worldNP.setAttrib(LightRampAttrib.makeSingleThreshold(0, 0.5))


        # self.charhitbox(self.charM, self.character.HB, True,'player')

        # self.pdodgecheck = NodePath(CollisionNode('pdodgecheck'))
        # self.hb(self.charM,self.pdodgecheck,shape=CollisionCapsule(0,0,0,0,0,3,1.2),visible=False)
        # self.pdodgecheck.show()

        # self.scarfSetup()

        ####Nodes around player for enemies to wlk to
        self.enemyTargets = []
        self.targetNode = NodePath('target node')
        self.targetF = self.targetNode.attachNewNode('target front')
        self.targetF.setPos(0,4,0)
        self.targetR = self.targetNode.attachNewNode('target rear')
        self.targetR.setPos(0,-4,0)
        self.enemyTargets.append(self.targetF)
        self.enemyTargets.append(self.targetR)

        #for bicep anim
        # self.parryM = Actor('../models/parry.bam',
        #                     {"flex" : '../models/parry_bicepflex.bam'})
        # self.parryempties = loader.loadModel('../models/bicepempties.glb')
        # self.parryempties.reparentTo(self.charM)

    def enemySetup(self): #enemy):
        """sets up enemies, defaults to inactive. spawn enemy to add them to arena"""
    # def enemySetup(self, actor, startpos, ):
        # dummy = Actor('../models/enemies/enemies.bam',{
        #                   'slash' : '../models/enemies/enemies_slash.bam',
        #                   'idle' : '../models/enemies/enemies_idle.bam',
        #                   'SMASH' : '../models/enemies/enemies_SMASH.bam',
        #                     })
        turret1 = Actor('../models/enemies/turret.bam', {
                            'idle': '../models/enemies/turret_idle.bam',
                            'slash1': '../models/enemies/turret_slash1.bam',
                            'slash2': '../models/enemies/turret_slash1.bam',
                            'staggerL': '../models/enemies/turret_staggerL.bam',
                            'staggerR': '../models/enemies/turret_staggerR.bam',})
        turret2 = Actor('../models/enemies/turret.bam', {
                            'idle': '../models/enemies/turret_idle.bam',
                            'slash1': '../models/enemies/turret_slash1.bam',
                            'slash2': '../models/enemies/turret_slash1.bam',
                            'staggerL': '../models/enemies/turret_staggerL.bam',
                            'staggerR': '../models/enemies/turret_staggerR.bam',})
        # self.turret.reparentTo(self.worldNP)
        # self.turret.setPos(10,0,0)
        enemyM = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash1.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'bicepbreak' : '../models/enemies/enemy_bicepbreak.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'chargeup' : '../models/enemies/enemy_chargeup.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        enemy2 = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash1.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        enemy3 = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash1.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        enemy4 = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash1.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        enemy5 = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        enemy6 = Actor('../models/enemies/enemy.bam',{
                          'slash' : '../models/enemies/enemy_slash.bam',
                          'slash2' : '../models/enemies/enemy_slash2.bam',
                          'idle' : '../models/enemies/enemy_idle.002.bam',
                          'deflected' : '../models/enemies/enemy_deflected.bam',
                          'recoil1' : '../models/enemies/enemy_recoil1.bam',
                          'death' : '../models/enemies/enemy_death.bam',
                          'run' : '../models/enemies/enemy_walk.bam',
                          'staggered': '../models/enemies/enemy_staggered.bam',
                          'finished' : '../models/enemies/enemy_finished.bam'
                            })
        # dummy2 = Actor()
        # # dummy.instanceTo(dummy2)
        self.dummy = Enemy(self.world, 
                            self.worldNP,enemyM, startpos = self.lvl.inactiveenemypos[0],
                            posture= 2,
                            hbshader=self.shader,spawnpoint = self.lvl.enemyspawnpoints[0],
                            # initState='charging',
                            initState='stunned',
                            type = 'Basic',
                            name = 'dummy' )
        self.dummy2 = Enemy(self.world, self.worldNP,enemy2, startpos = self.lvl.inactiveenemypos[1],
                            posture=2,
                            hbshader=self.shader,
                            spawnpoint=self.lvl.enemyspawnpoints[1],
                            initState='stunned',
                            type = 'Basic',
                            name = 'dummy2'  ) 
        self.dummy3 = Enemy(self.world, self.worldNP,enemy3, startpos = self.lvl.inactiveenemypos[2],
                            posture=2,
                            hbshader=self.shader,
                            spawnpoint=self.lvl.enemyspawnpoints[2],
                            initState='stunned',
                            type = 'Basic',
                            name = 'dummy3'  ) 
                            # parrypos=loader.loadModel('../models/enemies/enemyparrypos.glb'), )
        self.turret1 = Turret(self.world, self.worldNP, turret1, self.lvl.inactiveenemypos[3], self.lvl.turretPos[1], 'turret1')
        self.turret2 = Turret(self.world, self.worldNP, turret2, self.lvl.inactiveenemypos[4],self.lvl.turretPos[2], 'turret2')

        
        self.turrets = [self.turret1, self.turret2]
        self.inactiveEnemies = []
        # self.enemies = []
        self.activeEnemiesPos = {}
        
        #Justr for now =3
        self.activeEnemiesPos.update({self.turret1.NP:self.turret1.NP.getPos()})

        # self.dummy.atkhb(self.dummy.model.expose_joint(None, 'modelRoot', 'blade'),
        #               CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        self.dummy2.attachWeapon(loader.loadModel('../models/sword.glb'),
                                 self.dummy2.model.exposeJoint(None, "modelRoot", "swordpos"))
        self.dummy.attachWeapon(loader.loadModel('../models/sword.glb'),
                                 self.dummy.model.exposeJoint(None, "modelRoot", "swordpos"))
        self.dummy3.attachWeapon(loader.loadModel('../models/sword.glb'),
                                 self.dummy3.model.exposeJoint(None, "modelRoot", "swordpos"))
        # self.dummy.atkhb(self.dummy2.model.exposeJoint(None, "modelRoot", "swordpos"),
        #               CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        # self.enemysword()
        # self.spawnEnemy(self.dummy2)
        self.enemies.append(self.dummy)
        self.enemies.append(self.dummy2)
        self.enemies.append(self.dummy3)
        self.activeEnemiesPos.update({self.dummy.NP:self.dummy.NP.getPos()})
        self.activeEnemiesPos.update({self.dummy2.NP:self.dummy2.NP.getPos()})
        self.activeEnemiesPos.update({self.dummy3.NP:self.dummy3.NP.getPos()})

        # if self.activeEnemies:
        for enemy in self.enemies:
                self.charhitbox(enemy.model, enemy.Hitbox,False, enemy.name)
                 
        taskMgr.add(self.updateEnemies, 'update enemies')

    def spawnEnemy(self, task):
        
        print('spawn no:',self.lvl.spawnNo, len(self.enemies))
        # enemy = self.dummy
        # for x in self.enemies:
        # # print(self.enemies[self.lvl.spawnNo].name)
        # print('spawn nom', self.lvl.spawnNo, len(self.enemies))
        # print('spawned', enemy.name)#, self.lvl.spawnNo)
        
        if self.lvl.spawnNo == (len(self.enemies)-1):
            # print('reset spawn no')
            self.lvl.spawnNo = -1
            # return task.again

        self.lvl.spawnNo += 1 # self.activeEnemies.append(enemy)
        # for enemy in self.enemies:
        enemy = self.enemies[self.lvl.spawnNo]
        if enemy.active == True:
            # print(enemy.name, 'is already spawned')
            return task.again
        else: 

            enemy.active = True
            enemy.NP.setPos(enemy.spawnPoint)####UPDATE
            self.activeEnemiesPos.update({enemy.NP:enemy.NP.getPos()})
            self.charhitbox(enemy.model, enemy.Hitbox,False, enemy.name)
            return task.again
        
        #teleport enemies from inactive to active, plays spawn animation
    def spawnTurret(self, turret):
        #update the spawn pos
        turret.health = .99
        
        # TODO: refactor into a class
        i = self.nextTurretPos
        occupied = set(self.occupiedTurretPos.values())
        while i in occupied:
            i = (i + 1) % self.numTurretPos
        self.occupiedTurretPos[turret.name] = i
        self.nextTurretPos = i
        turret.pos = self.lvl.turretPos[self.nextTurretPos]
        turret.spawnSeq()

    def enemydeath(self, enemy):
        print('death')
        if self.lockedOn==True:
            self.lockedOn = False
        self.inactiveEnemies.append(enemy)
        # self.enemies.remove(enemy)
        # play death anim, telport enemy aWay
        # enemy.model.play('death'

        def teleport():
            
            enemy.NP.setPos(enemy.startpos)
        die = enemy.model.actorInterval('death')
        tp = Func(teleport)# iterate thru the positions
        dieseq = Sequence(die, tp)
        dieseq.start()
        taskMgr.remove(f'{enemy.name}update')
    def turretDeath(self):
        #same as enemy death except spawn the turret elsewhere

        pass

    def toggleDebug(self):
        if self.debugNP.isHidden():
          self.debugNP.show()
        else:
          self.debugNP.hide()    
    def wireframe(self):
        base.wireframeOn()
    def debugOSDUpdater(self, task):
        """Update the OSD with constantly changing values"""
        self.osd.add("mvt state", "{}".format(self.character.movementState))
        # self.osd.add("previous mvt state", "{}".format(self.player.previousState)) 
        # self.osd.add("animstate ground", "{}".format(self.groundstates))
        # self.osd.add("currentanim", "{}".format(self.current_animations))
        # self.osd.add("currentseq", "{}".format(self.current_seq))
        self.osd.add("currentframe", "{}".format(self.charM.getCurrentFrame()))
        self.osd.add("movepoints", "{}".format(self.character.movepoints))
        # self.osd.add("movetimer?", "{}".format(self.character.movetimer))
        self.osd.add("attacking?", "{}".format(self.character.isAttacking))
        self.osd.add("parrying?", "{}".format(self.character.isParrying))
        self.osd.add("lockedon?", "{}".format(self.lockedOn))
        # self.osd.add("input chain:", "{}".format(self.atx))
        # self.osd.add("input tiume:", "{}".format(self.inputtime))
        # self.osd.add("walking seq?", "{}".format(self.walkseq))
        # self.osd.add("event queue", "{}".format(EventQeue.isQueueEmpty()))
        # self.osd.add("grindsequence")
        self.osd.render()
        return task.cont     
       
# class Fx():
#         def __init__(self):
#                 """pre loads fx geometries"""
#                 #kick1 motiuontrail:

#                 self.ts0 = TextureStage('texstage0')
#                 self.ts0.setTexcoordName("0")
#                 self.ts0.setMode(TextureStage.MReplace)
#                 trailmat = Material("material")
#                 trailmat.setEmission((1,1,1,1))
#                 trailmat.setSpecular((1,1,1,0))
                
#                 self.ts0.setSort(0)
#                 uvtex = loader.loadTexture('../models/tex/testuv.png')
#                 tex = loader.loadTexture('../models/tex/transgradiet.png')
#                 ptex = loader.loadTexture('../models/tex/bb.png')
#                 brushtex = loader.loadTexture('../models/tex/watercolorstrike.png')
#                 self.slash1trail = loader.loadModel('../models/newslashtrail.glb')
                

#                 # self.slashfx = loader.loadModel('../models/slashfx.glb')
#                 self.slashfx = loader.loadModel('../models/slashfx.glb')
#                 self.slashfx.setMaterial(trailmat)
#                 self.slashfx.clearTexture()
#                 self.slashfx.setTransparency(True)
#                 self.slashfx.setTexture(self.ts0, brushtex,1)
#                 self.slashfx.setShader(self.shader)    

#                 self.slash1trail.setMaterial(trailmat)
#                 self.slash1trail.clearTexture()
#                 self.slash1trail.setTransparency(True)
#                 self.slash1trail.setTexture(self.ts0, brushtex,1)
#                 self.slash1trail.setShader(self.shader)
#                 # self.slash1trail.setH(180)
#                 # self.slash1trail.replaceTexture(oldtex, tex)
#                 # self.slash1trail.setDepthWrite(False)
#                 # print(self.slash1trail.findAllTextures())
#                 # self.slash1trail.ls()

#                 self.slash2trail = loader.loadModel('../models/slashkick2trail.glb')
#                 self.slash2trail.setMaterial(trailmat)
#                 self.slash2trail.setShader(self.shader)
#                 # self.slash2trail.reparentTo(self.worldNP)
#                 # self.slashtrail2.setPos(0, -115, -10)
#                 self.slash2trail.setTransparency(True)
#                 self.slash2trail.setTexture(self.ts0, brushtex,1)
#                 # self.slash2trail.setH(180)

#                 self.slash3trail = loader.loadModel('../models/slashkick3trail.glb')
#                 self.slash3trail.setMaterial(trailmat)
#                 self.slash3trail.setTransparency(True)
#                 self.slash3trail.setTexture(self.ts0, tex,1)
#                 self.slash3trail.setShader(self.shader)

#                 self.dodgeframes = self.charM.getNumFrames('dodge')
#                 self.dodgeposeground = loader.loadModel('../models/dodgepose.glb')
#                 self.dodgeposeground.setShader(self.shader)
#                 self.dodgeposeground.setTransparency(True)
#                 self.dodgeposeground.setH(180)
#                 self.dodgeposeair= loader.loadModel('../models/dodgeposeair.glb')
#                 self.dodgetrail = []
#                 self.dodgetraileffect = False#if the copied nodes are visible        
#                 self.dodgetrailair = []

#                 # coral = loader.loadModel('../models/coral.glb')
#                 # coral.reparentTo(self.worldNP)
#                 # coral.setPos(0,-115,0)
     
#                 for i in range(self.dodgeframes ): #self.dodgetrail[i] == None:
#                     self.dodgetrail.append(NodePath(f"dtrail{i}"))
#                     self.dodgeposeground.instanceTo(self.dodgetrail[i])

#                 # self.crosshair = loader.loadModel('../models/crosshair.glb')
#                 self.crosshair = loader.loadModel('../models/lockonicon.glb')
#                 self.crosshair.set_depth_write(False)
#                 self.crosshair.set_depth_test(False)
#                 self.crosshair.setCompass(base.camera)        




game = Game()
run()
