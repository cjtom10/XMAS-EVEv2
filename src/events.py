# from codecs import charmap_builddef
from typing import Collection
from urllib.parse import ParseResultBytes
from panda3d.bullet import *
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from direct.interval.LerpInterval import *
from direct.interval.ActorInterval import ActorInterval, LerpAnimInterval
import math

class Events:

        def __init__(self):
            """contains events/interactions between player and enemies/world"""
        ##ats
            # self.animOveride = False# ensures that walking/idle/etc dont interfere with attack/ parry anims

            # self.attached = False#for hitbox
            # self.hitcontact = False
            # self.attackqueue = 0
            # self.attackQueued = False
            # self.qdatk = None # either stab or slash, lets u know what queued attack to do
            # self.attimer = False
            # self.itimer = None
            # self.atx = None
            # self.pause = False#for combos
            # self.inputtime = 1# delay between inputs
            # self.buffer = None#
            # self.pauseframe = None
            
            self.finisherSequence = None

            ###for lockon
            self.closest = None
            self.p2e=0
            self.midpoint = 0
            # self.atkframe = None#-read frame duyriung attacks

            self.foot = self.charM.expose_joint(None, 'modelRoot', 'foot.R')
            self.frame = self.charM.getCurrentFrame()
            self.anim=self.charM.getCurrentAnim()
            self.lblAction = None

            self.atkhb = CollisionCapsule(0, .5, 0, 0, 0, 0, .5)

            ###for consecuitive deflects
            self.deflectOrder =0
            
    # def lightAttack(self):
    #     # ml.disable()
    #     taskMgr.add(self.character.attacking)

            # ####Player col nodes
            # self.atkNode = NodePath(CollisionNode('attack'))
            # self.parryNode = NodePath(CollisionNode('parry'))
            

            ######Enemy collnodes
            

            # self.rightfootHB = self.worldNP.attachNewNode(BulletGhostNode('rightfoot'))
            # self.lockOnimg=OnscreenImage()
            # self.lockOnimg.setTransparency(True)
            # self.lockl
            # self.lockOnimg.setImage('../models/tex/lockon.png')
            # self.lockOnimg.setPos((0,0,0))
            # #collisions
            # self.traverser = CollisionTraverser('traverser')
            # base.cTrav = self.traverser
            # collhandler = CollisionHandlerEvent()
            # collhandler.addInPattern('%fn-into-%in')
            # collhandler.addOutPattern('%fn-out-%in')
            # self.traverser.addCollider(self.footHB, collhandler)
            # self.traverser.addCollider(self.dummyHB, collhandler)
            # self.accept('rightfoot-into-dummyhb',  self.hit)# extraArgs=[self.playercar])
            # self.accept('rightfoot-into-dummyhb',  self.hit)
        def charhitbox(self, actor, HBlist,visible,name):
            """set up hitbox for taking damage"""
            # print(self.charM.listJoints())
            self.head = actor.expose_joint(None, 'modelRoot', 'head')
            self.chest = actor.expose_joint(None, 'modelRoot', 'chest')
            rightbicep= actor.expose_joint(None, 'modelRoot', 'bicep.R')
            rightforearm= actor.expose_joint(None, 'modelRoot', 'forarm.R')
            rightthigh = actor.expose_joint(None, 'modelRoot', 'femur.R')
            rightshin = actor.expose_joint(None, 'modelRoot', 'shin.R')
            leftbicep= actor.expose_joint(None, 'modelRoot', 'bicep.L')
            leftforearm= actor.expose_joint(None, 'modelRoot', 'forarm.L')
            leftthigh = actor.expose_joint(None, 'modelRoot', 'femur.L')
            leftshin = actor.expose_joint(None, 'modelRoot', 'shin.L')

            # print(self.head.getPos(render))
            headHB = CollisionSphere(0,0,0, .1)
            chestHB= CollisionSphere(0,.2,0,.4)
            arm =  CollisionCapsule((0,-.2,0),(0,.8,0),0.07)
            leg =  CollisionCapsule((0,-.38,0),(0,1,0),0.1)
            # forearm =  CollisionCapsule((0,-.2,0),(0,.8,0),0.07)
            # self.characterHitB = self.character.movementParent.attachNewNode(CollisionNode('character'))

            # self.characterHB = []

            # self.headHB = self.characterHitB.attachNewNode(CollisionNode('head'))
            # self.headHB.reparentTo(self.characterHitB)
            # self.headHB.node().addSolid(headHB)       
            # self.headHB.show()
            # self.characterHB.append(self.headHB)
            # self.headHB.setCompass(self.head)
            # self.headHB.setPos(self.head, 0,0,7)
            # self.characterHitB.show()

            self.headHB = self.head.attachNewNode(CollisionNode(f'{name}head'))
            self.headHB.node().addSolid(headHB)
            self.headHB.setZ(-.2)
            # self.headHB.show()
            HBlist.append(self.headHB)
            # self.headHB.wrtReparentTo(self.characterHitB)

            

            self.chestHB = self.chest.attachNewNode(CollisionNode(f'{name}chest'))
            self.chestHB.node().addSolid(chestHB)
            self.chestHB.setY(-.2)
            # self.chestHB.show()
            HBlist.append(self.chestHB)
            # self.chestHB.reparentTo(self.characterHB)

            self.bicepR = rightbicep.attachNewNode(CollisionNode(f'{name}bicepr'))
            self.bicepR.node().addSolid(arm)
            # self.bicepR.show()
            HBlist.append(self.bicepR)

            self.forarmR = rightforearm.attachNewNode(CollisionNode(f'{name}forearmr'))
            self.forarmR.node().addSolid(arm)
            # self.forarmR.show()
            HBlist.append(self.forarmR)

            self.thighR = rightthigh.attachNewNode(CollisionNode(f'{name}thighr'))
            self.thighR.node().addSolid(leg)
            # self.thighR.show()
            HBlist.append(self.thighR)
            
            self.shinR = rightshin.attachNewNode(CollisionNode(f'{name}shinr'))
            self.shinR.node().addSolid(leg)
            # self.shinR.show()
            HBlist.append(self.shinR)

            self.bicepL = leftbicep.attachNewNode(CollisionNode(f'{name}bicepl'))
            self.bicepL.node().addSolid(arm)
            # self.bicepL.show()
            HBlist.append(self.bicepL)

            self.forarmL = leftforearm.attachNewNode(CollisionNode(f'{name}forearml'))
            self.forarmL.node().addSolid(arm)
            # self.forarmL.show()
            HBlist.append(self.forarmL)

            self.thighL = leftthigh.attachNewNode(CollisionNode(f'{name}thighl'))
            self.thighL.node().addSolid(leg)
            # self.thighL.show()
            HBlist.append(self.thighL)
            
            self.shinL = leftshin.attachNewNode(CollisionNode(f'{name}shinl'))
            self.shinL.node().addSolid(leg)
            # self.shinL.show()
            HBlist.append(self.shinL)

            if visible ==True:
                for node in HBlist:
                    node.show()
            # print('char hb', self.characterHB)

        # def hb(self, parent, node, shape, pos =(0,0,0), visible=True):
        #     """player hitboxes for attacks/parries"""
        #     # self.character.movementState = "attacking" 
            
        #     ##
        #     # print(self.speed)
        #     # self.footR = self.charM.expose_joint(None, 'modelRoot', 'foot.R')
        #     # self.footL = self.charM.expose_joint(None, 'modelRoot', 'foot.L')
        #     HitB = CollisionCapsule(0, .5, 0, 0, 0, 0, .5)
        #     # self.footHB = self.foot.attachNewNode(CollisionNode('rightfoot'))
        #     node.reparentTo(parent)
        #     node.node().addSolid(shape)
        #     # node.setZ(-.2)
        #     node.setPos(pos)
            
        #     self.attached = True
        #     if visible ==True:
        #         node.show()
            # self.speed /= 6
            # self.footHB.instanceTo(self.footL)

            # shape = BulletCapsuleShape(.5, 1)
            # self.rightfootHB.reparentTo(self.foot)
            # self.rightfootHB.setP(90)
            # self.rightfootHB.node().addShape(shape)
            # self.world.attachGhost(self.rightfootHB.node())

        def action(self, button, pos, first = True, pause = None):
        # Just show which button has been pressed.
            icons = loader.loadModel("../models/xbone-icons.egg")
            mgr = TextPropertiesManager.getGlobalPtr()
            if self.lblAction == None:
                self.lblAction = OnscreenText(
                                              fg=(-10,1,1,1),
                                              scale = .15)
            # self.lblAction = OnscreenImage()
            # self.lblAction = TextNode(f'{button}')      
            for name in ["face_a", "face_b", "face_x", "face_y", "ltrigger", "rtrigger", "lstick", "rstick"]:
                self.graphic = icons.find("**/" + name)
                self.graphic.setScale(1.5)
                mgr.setGraphic(name, self.graphic)
                self.graphic.setPos(pos)
                timespressed = int
            if first == False:
                new = NodePath('pause')
                self.graphic.instanceTo(new)
                # new.reparentTo(self.graphic)
                # new.setPos(pos)
            # self.lblAction.setImage( " \5%s\5" % button)    
            # self.lblAction.text = " \5%s\5" % button
            if pause == None:
                self.lblAction.appendText( " \5%s\5" % button)
            if pause == True:
                self.lblAction.appendText('-')
            # self.lblAction.flattenStrong()
            
            self.lblAction.show()    
        def actionUp(self):
        # Hide the label showing which button is pressed.
            # self.lblAction.ls()
            # self.lblAction.hide()    
            if self.lblAction !=None:
                self.lblAction.destroy()
                self.lblAction = None
                # self.graphic.destroy()
#####3TASKS here
        # # def closestEnemy(self):
        # #     """find closestenemy for lock on"""
        # #     # print('dist2enemy',self.p2e)
        # #     # print(self.enemiesPos)
        # #     playerpos = self.charM.getPos(render)
        # #     ####enemies move to these points
        # #     target1 = (playerpos.x, playerpos.y +2, playerpos.z)

        # #     self.dummy2.moveTarget = target1
        # #     self.dummy2.lookTarget = playerpos
        # #     # if self.character.movementState!='dodging':
        # #     #     self.dummy2.tracktarget()
        # #     # self.dummy.lookTarget = playerpos
        # #     def updateEnemypos():
                
        # #         for name in self.activeEnemiesPos:
        # #             self.activeEnemiesPos.update({name:name.getPos(render)})
        # #         if self.closest!=None:
        # #             pos = self.activeEnemiesPos.get(self.closest)
        # #             self.p2e = abs((playerpos-pos).length())
        # #             self.midpoint = Point3((playerpos.x+pos.x)/2,(playerpos.y+pos.y)/2,(playerpos.z+pos.z)/2)
                    
        # #     updateEnemypos()

        # #     if self.lockedOn ==True:
                
        # #         if self.closest == None:
                    
        # #             v = self.activeEnemiesPos.values()
                    
        # #             closeval= min(v, key=lambda pt: (playerpos - pt).length())
        # #             for key, value in self.activeEnemiesPos.items():
        # #                     if closeval==value:
        # #                         self.closest = key
                                
        # #             # self.p2e=(playerpos - closeval).length()

        # #         a = self.charM.getX(render) - self.closest.getX(render)
        # #         b = self.charM.getY(render) - self.closest.getY(render)

        # #         h = math.atan2(a,-b )
        # #         angle = math.degrees(h) 

        # #         # self.closest = closest
        # #         self.charM.setH(render, angle)
        # #         self.camtarg.setH(render, angle)
        # #         # base.camera.setH(angle)

        # #         self.crosshair.reparentTo(self.closest)
        # #         self.crosshair.setPos(self.charM.getPos())
        # #     if self.lockedOn ==False:
        # #         self.crosshair.detachNode() 
        # #         self.closest = None   
        # #     return

        # def inputtimer(self,task):## TOIDO=- air timer should have smaller window, use  time between inputs

        #     """Timer that starts betwen attacks to determine combo/animation. attacking during active frames
        #     adds hitbox etc, buffer is rest of the frmaes, and the pause frame indicates when  delay atacks can be done"""
        #     # print('frame:',self.charM.getCurrentFrame())
        #     #to do: delay time based on frame#
        #     # print(task.time)
        #     # self.itimer = True
        #     if self.character.isAttacking==False:#remove hb
        #         self.attached = False
        #         self.atkNode.node().clearSolids()
        #         self.parryNode.node().clearSolids()

        #     # if self.atkframe <13:
        #     ##correct method bAsed on fdrames
        #     if self.character.isAttacking ==True or self.buffer ==True and self.pauseframe==False:                  
        #         return task.cont
        #     # if self.buffer.getCurrentFrame() ==21:#pause
        #     if self.pauseframe == True and self.buffer ==True and self.character.isAttacking ==False:    
        #         # print('pauseframe')
        #         # if self.leftjoystick ==True:
        #         #     print('end attack by waY OF WALK')
        #         #     self.finish()
        #         #     return task.done
               
        #         if self.pause ==False and len(self.atx)!=0:
        #             self.action(None, (0,0,0), pause=True)
        #             self.atx.append('-')
        #             self.pause =True 
        #         # self.inputtime = task.time
        #         return task.cont

        #     if self.buffer == False:
            
        #         self.finish(blendOut=True)
        #         return task.done 

        #     # if self.atx!= None:
        #     #     if len(self.atx) >=6:
        #     #         print('combo limit')
        #     #         self.finish()

        # # def finish(self,blendOut = False):
        # #         """clear things up at the end of attack sequence or use to cancel out of attack sequence"""
        # #         if self.animseq!=None:
        # #             self.animseq.pause()
        # #         if self.atx!=None:
        # #             self.atx.clear()
        # #         self.character.movementState = "endaction"
        # #         self.character.jumpdir =  Vec3(0,0,0)
        # #         self.character.isAttacking=False
        # #         self.character.isParrying=False
        # #         self.hitcontact = False
        # #         self.atkNode.node().clearSolids()
        # #         # self.world.removeGhost(self.rightfootHB.node())
        # #         # self.slash1trail.detachNode()
                 
        # #         self.actionUp()   
        # #         self.pause = False
        # #         # if keeptimer==False:
        # #         self.attached = False
                
        # #         self.animseq = None
        # #         self.itimer = None

        # #         #letr enemies get hit again
        # #         for enemy in self.enemies:
        # #             enemy.isHit = False
        # #         #     if enemy.solidsCleared == True:
        # #         #         self.charhitbox(enemy.model, enemy.Hitbox, enemy.name)

        # #         ##blend back to idle/walking on ground
        # #         #TODO --- need to blend from end frmae to idle/walk
        # #         # print('fionish', self.character.movementState)
        # #         # print('isonground',self.character.isOnGround())

        # #         #Blend out to idle here TESTING PURPOSES----------=-
        # #         if blendOut==True:
        # #             # print('blendout')
        # #             # if self.character.isOnGround():
        # #             self.blendoutAtk = [self.currentAtk[0], self.currentAtk[1]]#blendout atk to change based on atack anim

        # def parrytask(self, task):
        #     # self.character.movementState ="attacking"
        #     if self.anim =='parry':
        #         if self.attached == False:
        #             self.hb(parent=self.forearm, node = self.parryNode, shape=self.atkhb)
        #         return task.cont
        #     else:
        #         self.character.movementState = "endaction"
        #         # print('enmdparry')
        #         self.parryNode.node().clearSolids()
        #         self.attached = False
        #         self.character.isParrying = False
        #         return task.done
        # def doDeflect(self, state='ground'):
        #     print('deflect order:', self.deflectOrder)
        #     self.deflectOrder+=1
            
        #     if self.character.movementState == "attacking":
        #         if self.character.isAttacking == True:
        #             print('cant deflect-attacking')
        #             return
        #         if self.character.isParrying == True:
        #             print('cant deflect-deflecting')
        #             return    
        #         else:
        #             self.finish()
        #     if state=='air':
        #         print('air deflect')
        #         return
        #     if self.attached == False:
        #         self.hb(parent=self.charM, node = self.parryNode, shape=CollisionSphere(0.5, 0.7, 2.3, 1))#, pos = (0,1,2))
        #     if self.animseq is not None:#end attack anim sequence
        #         if self.animseq.isPlaying():
        #                 self.animseq.pause()
        #     if self.itimer == True: 
        #         self.itimer == False
        #         taskMgr.remove('itimer')
        #         self.finish()
        #     if self.character.movementState!= "attacking":
        #         self.character.movementState = "attacking"            
            
        #     if self.lockedOn ==False:
        #         self.charM.setH(self.angle)
        
        #     self.animDeflect()
        def deflected(self, anim, enemy): #control enemie's recoil anim here too
            """event for when u succesfully deflect enemy- enemy loses one posture point and player recoils"""
            print('deflect!')
            enemy.atkNode.node().clearSolids()
            if self.player.animseq is not None:#end attack anim sequence
                if self.player.animseq.isPlaying():
                        self.player.animseq.pause()
            enemy.currentBehavior = 'deflected' #### Either this or stun
            # if enemy.seq.isPlaying():
            #     enemy.seq.pause()
            # enemy.posture+=.3
            enemy.posture -= 1
            # enemy.isAttacking =False
            #get rid of Hitboxes
            self.attached = False
            self.player.parryNode.node().clearSolids()
            # enemy.attached = False
            # enemy.atkNode.node().clearSolids()

            # enemy.play('recoil')
            # self.character.isAttacking=False >>>>move these later in the anim to prevent spam, or make the window smaller idkl
            # self.character.isParrying = False
            def finn():
                enemy.deflected = False
                enemy.currentBehavior = None

            recoil = self.charM.actorInterval(anim)
            # recoil = self.charM.actorInterval('recoil1')
            recoilE =  enemy.model.actorInterval('recoil1') ###3ENEMY STUN ANIMATion
            fin=Func(self.player.finish)
            Efin = Func(finn)
            self.player.animseq = Sequence(Wait(.1), recoil,Parallel(fin, Efin))
            #self.animseq = Sequence(Wait(.1), Parallel(recoil, recoilE),Parallel(fin, Efin))
            self.player.animseq.start()
        def processDeflect(self):
            pass
##### ATACKS START HERE
#         def slashAttack(self, activeframes = 16): #active frames and buffer frames and end frame
#             """hanbdles the timing/ combos for attack inputs, determines which slash attack to do"""
#             # if self.character.isAttacking ==True and 

#             if self.character.isAttacking == True:
#                 return
#             if self.character.isParrying == True:
#                 return

#             for enemy in self.enemies:
#                 enemy.isHit = False

#             if self.animseq is not None:#end attack anim sequence
#                 if self.animseq.isPlaying():
#                         self.animseq.pause()

#             if self.lockedOn ==False:
#                 self.charM.setH(self.angle)
#             if self.atx == None:
#                 self.atx = []
#             if self.atx!= None:
# ############   starts / adds to input chaine here
#                 if self.itimer == None:#first press. init the timer 
#                     self.itimer = taskMgr.add(self.inputtimer,'itimer')#, extraArgs=[activeframes,inputtime],appendTask = True )
#                     # if time > .6:
#                     # self.currentTimer = time
#                 if self.itimer !=None: ## 
#                     # self.charM.setH(self.angle)
#                     # self.itimer == False#restarts the timer
#                     self.inputtime = self.itimer.time#read time from last press

#                     taskMgr.remove('itimer')
#                     self.itimer = taskMgr.add(self.inputtimer,'itimer')#, extraArgs=[activeframes, self.inputtime],appendTask = True ) #delay = self.inputtime
#                 if self.character.movementState!= "attacking":
#                     self.character.movementState = "attacking"

#                 if self.character.isAttacking==True: #and self.charM.getCurrentFrame()<activeframes or self.character.movementState == "dodging":
#                     print('cant attaxcl')
#                     return ##allows buttopn mash, is this what we want?

#                 # if self.attached == False: #and self.hitcontact==False:
#                 #     self.hb(parent=self.rightfoot, node = self.atkNode, shape=CollisionCapsule(0, .5, 0, 0, 0, 0, .5))

#                 order = len(self.atx) +1

#                 self.action("face_x", (0,0,0))
#                 self.atx.append('X')
# ##############   This part determines which anim to do
#                 if order == 1  or order == 5 : 
#                     self.animattackslash(1)

#                 if order == 2 or order ==6 or order == 3 and self.atx[2]=='-':   
#                     self.animattackslash(2)

#                 if order == 3 and self.atx[2]!='-':
#                     self.animattackslash(3)
#                 if order ==4:
#                     if self.atx[2] == '-':
#                         activeframes = 28
#                         self.animattackslash(4)
#                         print('SPIN KICK')
#                     else:
#                         self.animattackslash(3)
#                 # print('len slash', len(self.atx))
#         def slideAttack(self):
#             print('slide attack')# finish the dodge do slide atack anim

#         def stabattack(self, activeframes = 5):

#             if self.character.isAttacking == True:
#                 return
#             if self.character.isParrying == True:
#                 return 

#             #make enemies hitable again
#             for enemy in self.enemies:
#                 enemy.isHit = False
#             if self.animseq is not None:#end attack anim sequence
#                 if self.animseq.isPlaying():
#                         self.animseq.pause()
#             if self.lockedOn ==False:
#                 self.charM.setH(self.angle)
#             # self.action("face_y", (-10,0,0))
#             if self.atx == None:
#                  self.atx = []
#             if self.atx!= None:
         
           
#                 self.action("face_y", (0,0,0))
#                 self.atx.append('Y')
#                 if self.attached == False and self.hitcontact==False:
#                     self.hb(parent=self.leftfoot, node=self.atkNode,shape=CollisionCapsule(0, .5, 0, 0, 0, 0, .5))
#                 if self.itimer == None:
#                     self.itimer =taskMgr.add(self.inputtimer,'itimer')#, extraArgs=[activeframes, 1],appendTask = True ) 
#                 if self.itimer!=None:
#                     # self.itimer == False
#                     taskMgr.remove('itimer')
#                     self.itimer =taskMgr.add(self.inputtimer,'itimer')#, extraArgs=[activeframes, 1],appendTask = True ) 
#                 if self.character.movementState!= "attacking":
#                     self.character.movementState = "attacking"
#                 order = len(self.atx) +1
#                 if order == 1  or order == 4 : 
#                     self.animattackstab(1)
#                 if order == 2  or order == 5 : 
#                     self.animattackstab(2)
#                 if order == 3 or order ==6: 
#                     self.animattackstab(3)
#             # print('len stab', len(self.atx))
#         def doQueuedAttack(self, attack, order):
#             return
#         def getpausetime(self):
#             pass#get time between button presses and return pasuetime 
#         def smashAttack(self):
#             # print('SMASH!')  
#             #play smassh anim
#             # taskMgr.add(self.character.doSmashattack)  
#             if self.character.movementState =="airdodge":
#                 self.character.movementState = "exitddodge"
#             if self.attached == False:
#                 self.hb(parent=self.leftfoot, node=self.atkNode,shape=CollisionCapsule(0, .5, 0, 0, 0, 0, .5))
#             self.character.airAttack = True
#             self.character.movementState = "attacking" 
#             self.animsmashattack()
#         def endsmash(self):
#             #maybe send a shockwave idkl
#             self.character.smashonground = False
#             self.player.finish()
#             print('endsmash')
#             # print('endsmash')
#             # self.movementState ="endaction"
#             # self.airAttack = False
#             # self.smash1 = False
#             # self.smashtask = None
#             # self.isAttacking = False
#             # self.__land(smash=True)
#             # return #task.done          

        def hit(self, entry):
            print(entry)
            print('hit!')

        # def playerStun(self):
        #     print('player takes hit')
        #     self.player.finish()
            

        def bicepbreak(self, enemy):
            """special finisher anim"""
            # self.animspecial = True# use to overide
            # ml.disable()
            enemy.trackPlayer = False
            self.charM.hide()
            self.parryM.reparentTo(self.character.movementParent)
            # self.parryempties.reparentTo(self.character.movementParent)
            self.parryM.play('flex')
            enemy.model.play('bicepbreak')
            # camerapos = self.parryempties.find('cameraPos')
            # connect = self.parryempties.find('connect')
            # print(camerapos.getPos())
            # base.camera.detachNode()
            camlerp = LerpPosHprInterval(base.camera,2, (0,15,0),(180,0,0), other=self.charM )
            camlerp.start()
            # base.camera.setPos(self.character.movementParent, (20,0,0))
            # base.camera.setH(180)
            enemy.model.setH(90)
            enemy.NP.setPos(self.character.movementParent, (-2,0,1))

            # anim that plays during perfect Parry
            # 1 hide charM 
            # 2 showbicep model + enemy model at break poihnt
            #3 move camera to set position
                #play anims, move cam forward

        def finisher(self, enemy):
            #
            # 2move player to enemy pos
            #3play both enemy/player anims
            #4 kill enemy
            def start():
                self.character.movementState = "finisher"
            def exit():
                self.player.character.movementState = 'endaction'
            x = self.charM.getX(render) - enemy.model.getX()
            y = self.charM.getY(render) - enemy.model.getY()

            h = math.atan2(-x,y )
            angle = math.degrees(h) 

        # self.closest = closest
            self.charM.setH(render, -angle)


            print('finisher')
            # self.charM.setH(-(enemy.model.getH(render)))
            # self.character.movementParent.setPos(enemy, 0,-1,0)
            point = render.getRelativePoint(enemy.model, (0,3,0))
            
            move2enemy =Parallel(LerpPosInterval(self.character.movementParent, .2, point))#,
                                                # LerpPosInterval(self.camtarg, .5, point),
                                                # LerpHprInterval(self.player.charM, .5, point))
            pose = Func(self.charM.pose, 'finisher', 0)
            playeranim = self.charM.actorInterval(animName='finisher',loop = 0, startFrame=0, endFrame = 40)
            enemyanim = enemy.model.actorInterval(animName='finished',loop = 0, startFrame=0, endFrame = 40)

            start = Func(start)
            die = Func(self.enemydeath, enemy)
            fin = Func(exit)
            # en
            # if self.finisherSeq== None:

            s = Sequence(start, Parallel(move2enemy,pose),
                        Parallel(playeranim,enemyanim),
                        die, fin
                        )
            s.start()
            #sequence= do anim, dodge/jump in direction
        # def doDodge(self, air=False):
        #     if air==False:
        #         self.animDodge()
        #     else:
        #         print('aor ddge')
        #         if self.character.movepoints!=0:
        #             self.character.movepoints -=1

        def finisherCheck(self):
            """if enemy is stunned, do finisher on it. if multiple enemies are stunned, see which is the closest """
            print('checking for finisher')
            targetenemy = None
            stunneds = []
        
            for enemy in self.enemies:
                if enemy.currentBehavior == 'stunned':
                    stunneds.append(enemy)
                    # print(min(stunneds, key=lambda e: e.d2p))
                    e = min(stunneds, key=lambda e: e.d2p)
                    self.finisher(e)
                    return
            else:
                print('no one 2 finish')
                pass    
        def takeDamage(self):
            """event when player takes damage and doesnt have super armor"""
            return
            #if you dont have super armor,  end attack and staggert    # print('dodge')
        def observePilotArmor(self):
            """look at pilot armor"""
            # if self.observing == False:
            self.observing = True
            # if card == 1:
            self.text.setText('Experimental PILOT ARMOR')
            if self.observing ==True:
                    self.text.setText('Experimental PILOT ARMOR Unit \nPilots must withstrand a neural grafting procedure to fly the vehicle. \n The procedure has a .000003% Survival rate')

            # elif card == 2:
                # self.text.setText('Pilots must withstrand a neural grafting procedure to fly the vehicle. \n The procedure has a .000003% Survival rate')
                # self.observe2 = True
            # elif card == 3:
                # self.text.clearText()
                # self.observing = False
        