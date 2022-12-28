from panda3d.core import *
from panda3d.bullet import *
from kcc import PandaBulletCharacterController
from anims import Anims
from actions import Actions
from direct.showbase.InputStateGlobal import inputState
from fx import Fx

class Player(Anims,Actions, Fx):

    def __init__(self, world, worldNP, gamepad, enemies, state):
        """contains kcc, anims, actions, player task. switch between on foot and in mech"""
        self.character =PandaBulletCharacterController(world, worldNP, 4, 1.5,.5, 1,) 
        self.state = state #either on foot or mech
        # if self.state == 'OF':
        self.health = .99
        self.isStunned = False
        self.plotArmour =  0#1# for testing

        self.setupOF()
        # self.charM = self.character.char # the model - need to switch between on foot and mech
        self.shader = Shader.load(Shader.SL_GLSL, "../shaders/vert.vert", "../shaders/frag.frag")
        Fx.__init__(self)
        Anims.__init__(self)
        Actions.__init__(self)

        
        self.enemies = enemies
        self.player = None
        
        self.lockedOn = False
        self.idleDirection = 0
        self.isIdle=False
        self.isWalking = False
        self.leftjoystick = True
        self.gamepad = gamepad
        self.angle =0

        self.wallGrabTimer = None
        self.wallJumpEnabled = False
        self.wallruncam=False

        self.leftValue = self.rightValue = 0
        self.dead = False

        self.enemyLaunchTarget = self.character.movementParent.attachNewNode('launchtarg')#enemies go to this point when you launch them
        self.enemyLaunchTarget.setPos(0,30,15)


        #init hitboxes
        # self.charhitbox(self.charM, self.character.HB, True,'player')
            # def charhitbox(self, self.charM, HBlist,visible,name):
        """set up hitbox for taking damage"""
        # print(self.charM.listJoints())
    def updatePlotarmor(self, x):
        #need to add this to hud
        self.plotArmour += x

        if self.plotarmour >= 100:
            self.plotPoints +=1
            self.plotarmour = 0
    def setUpMech(self):
        """clear on foot stuff, switch player to mech w mech anims + controls"""
        self.character.char.detachNode()
        self.charM = self.character.mech
        self.character.startCrouch()
        self.charM.reparentTo(self.character.movementParent)
        self.character.state = 'mech'
        self.character.gravity =-4.4 
        self.character.stepHeight = 0
        # self.character.movementState = 'mech'
        self.character.startFly()      

        #set up hitbox and actor stuff
        self.mechThighR = self.charM.controlJoint(None, "modelRoot", "thigh.R")
        self.mechThighL = self.charM.controlJoint(None, "modelRoot", "thigh.L")
        self.mechShinL = self.charM.controlJoint(None, "modelRoot", "shin.L")
        self.mechShinR = self.charM.controlJoint(None, "modelRoot", "shin.R")

        self.charM.makeSubpart("legs", ["thigh.L", "thigh.R", " shin.L", "shin.R","heelik.L", "heelik.R",
                                        "kneeik.L", "kneeik.R" ])
        self.charM.makeSubpart("arms", ["blade.L", "blade.R",
                                        "forearm.L", "forearm.R", "bicep.L", 
                                        "bicep.R",
                                        "elbowIK.L", "elbowik.R", "handik.L", "handIK.R"
                                        ], ["thigh.L", "thigh.R", " shin.L", "shin.R","heelik.L", "heelik.R",
                                        "kneeik.L", "kneeik.R" ])
        
        self.bladeL = self.charM.expose_joint(None, 'modelRoot', 'blade.L')
        self.bladeR = self.charM.expose_joint(None, 'modelRoot', 'blade.R')

        self.moving = False
        self.mechanim = None

        self.mechdodgefx = []
        for i in range(5): #self.dodgetrail[i] == None:
            self.mechdodgefx.append(NodePath(f"mechtrail{i}"))
            self.character.mech.instanceTo(self.mechdodgefx[i])
            self.FXset = False
    def setupOF(self):
        
        self.charM = self.character.char
        self.pdodgecheck = NodePath(CollisionNode('pdodgecheck'))
        self.HitBoxOF()
    

    def HitBoxOF(self, HBvisible = False):
            self.HB = []
            self.head = self.charM.expose_joint(None, 'modelRoot', 'head')
            self.chest = self.charM.expose_joint(None, 'modelRoot', 'chest')
            rightbicep= self.charM.expose_joint(None, 'modelRoot', 'bicep.R')
            # self.rightfoot = self.charM.expose_joint(None, 'modelRoot', 'foot.R')
            # self.leftfoot = self.charM.expose_joint(None, 'modelRoot', 'foot.L')
            rightforearm= self.charM.expose_joint(None, 'modelRoot', 'forarm.R')
            rightthigh = self.charM.expose_joint(None, 'modelRoot', 'femur.R')
            rightshin = self.charM.expose_joint(None, 'modelRoot', 'shin.R')
            leftbicep= self.charM.expose_joint(None, 'modelRoot', 'bicep.L')
            leftforearm= self.charM.expose_joint(None, 'modelRoot', 'forarm.L')
            leftthigh = self.charM.expose_joint(None, 'modelRoot', 'femur.L')
            leftshin = self.charM.expose_joint(None, 'modelRoot', 'shin.L')
    
            # print(self.head.getPos(render))
            headHB = CollisionSphere(0,0,0, .1)
            chestHB= CollisionSphere(0,.2,0,.4)
            arm =  CollisionCapsule((0,-.2,0),(0,.8,0),0.07)
            leg =  CollisionCapsule((0,-.38,0),(0,1,0),0.1)
            # forearm =  CollisionCapsule((0,-.2,0),(0,.8,0),0.07)
            self.characterHitB = self.character.movementParent.attachNewNode(CollisionNode('character'))
            self.attachblade(loader.loadModel('../models/blade.glb'))
            # # self.blade.setH(180)
            bladeheight = .25
            self.blade.setZ(.1)
            # taskMgr.add(self.character.updatechar, "updateCharacter")
            self.charM.setZ(bladeheight)
            # self.characterHB = []
    
            # self.headHB = self.characterHitB.attachNewNode(CollisionNode('head'))
            # self.headHB.reparentTo(self.characterHitB)
            # self.headHB.node().addSolid(headHB)       
            # self.headHB.show()
            # self.characterHB.append(self.headHB)
            # self.headHB.setCompass(self.head)
            # self.headHB.setPos(self.head, 0,0,7)
            # self.characterHitB.show()
    
            self.headHB = self.head.attachNewNode(CollisionNode('playerhead'))
            self.headHB.node().addSolid(headHB)
            self.headHB.setZ(-.2)
            # self.headHB.show()
            self.HB.append(self.headHB)
            # self.headHB.wrtReparentTo(self.characterHitB)
            
    
            self.chestHB = self.chest.attachNewNode(CollisionNode('playerchest'))
            self.chestHB.node().addSolid(chestHB)
            self.chestHB.setY(-.2)
            # self.chestHB.show()
            self.HB.append(self.chestHB)
            # self.chestHB.reparentTo(self.characterHB)
    
            self.bicepR = rightbicep.attachNewNode(CollisionNode('playerbicepr'))
            self.bicepR.node().addSolid(arm)
            # self.bicepR.show()
            self.HB.append(self.bicepR)
    
            self.forarmR = rightforearm.attachNewNode(CollisionNode('playerforearmr'))
            self.forarmR.node().addSolid(arm)
            # self.forarmR.show()
            self.HB.append(self.forarmR)
    
            self.thighR = rightthigh.attachNewNode(CollisionNode('playerthighr'))
            self.thighR.node().addSolid(leg)
            # self.thighR.show()
            self.HB.append(self.thighR)
            
            self.shinR = rightshin.attachNewNode(CollisionNode('playershinr'))
            self.shinR.node().addSolid(leg)
            # self.shinR.show()
            self.HB.append(self.shinR)
    
            self.bicepL = leftbicep.attachNewNode(CollisionNode('playerbicepl'))
            self.bicepL.node().addSolid(arm)
            # self.bicepL.show()
            self.HB.append(self.bicepL)
    
            self.forarmL = leftforearm.attachNewNode(CollisionNode('playerforearml'))
            self.forarmL.node().addSolid(arm)
            # self.forarmL.show()
            self.HB.append(self.forarmL)
    
            self.thighL = leftthigh.attachNewNode(CollisionNode('playerthighl'))
            self.thighL.node().addSolid(leg)
            # self.thighL.show()
            self.HB.append(self.thighL)
            
            self.shinL = leftshin.attachNewNode(CollisionNode('playershinl'))
            self.shinL.node().addSolid(leg)
            # self.shinL.show()
            self.HB.append(self.shinL)
    
            if HBvisible ==True:
                for node in self.HB:
                    node.show()
            # print('char hb', self.characterHB)
            #hb for perfect dodge
            self.hb(self.charM,self.pdodgecheck,shape=CollisionCapsule(0,0,0,0,0,3,1.2),visible=False)
    def addSolids(self):
        """puts collision solids back into player"""
            
        
        # self.headHB = self.head.attachNewNode(CollisionNode('playerhead'))
        headHB = CollisionSphere(0,0,0, .1)
        chestHB= CollisionSphere(0,.2,0,.4)
        arm =  CollisionCapsule((0,-.2,0),(0,.8,0),0.07)
        leg =  CollisionCapsule((0,-.38,0),(0,1,0),0.1)
        self.headHB.node().addSolid(headHB)
        self.bicepR.node().addSolid(arm)
        self.forarmR.node().addSolid(arm)
        self.thighR.node().addSolid(leg)
        self.shinR.node().addSolid(leg)
        self.bicepL.node().addSolid(arm)
        self.forarmL.node().addSolid(arm)
        self.thighL.node().addSolid(leg)
        self.shinL.node().addSolid(leg)

    def iframes(self):
        print('player is invu;nerable')
        for node in self.HB:
            node.node().clearSolids()
    def playerTask(self, dt):#, task):
        # print('mvt state', self.character.movementState)
        if self.isGrapplingGround==True:
             self.processGroundGrapple(self.currentGrapple)
        # #     # self.charM.lookAt(self.currentGrapple)
        #     return
        if self.isGrapplingAir==True:
            if self.isPerched==True:
                # self.animPerch()
                self.perched(dt)
                
            return
        if self.character.movementState == 'ground' and self.lastGrapple!=None:
            self.lastGrapple = None
        if self.isStunned == True:
            # print('u AARE STUNNDE')
            return
        if self.character.movementState == "finisher":
            print('ifinfisher')
            return
        if self.character.movementState == "attacking":#cancel attack anims ig joystuick is true
            if self.character.isAttacking==False:
                if self.pauseframe==True:# or self.buffer == True:
                    if self.leftjoystick==True:
                        print('walk oput of atack')
                        self.finish()
        if self.state == 'OF':
            self.updateAnimOF()
            if self.character.movementState == 'falling' and self.previousState == 'ground':
                self.character.ground2fall(5)
        if self.state == 'mech':
            if self.leftjoystick ==True:
                self.moving = True
            self.updateAnimMech()

        if self.character.enableVaulting==True and self.leftjoystick == True:
            self.vaultUp()
        self.prevGroundState = self.groundstates
        self.prevAirState = self.airstates
        oldCharPos = self.character.getPos(render)
        if self.character.movementState != 'attacking': #and self.character.movementState != 'grinding':
            self.character.setH(base.camera.getH(render))
            # print('setting H')
########check state changes
        self.previousState = self.character.movementState
        self.character.update() # WIP
        self.currentState = self.character.movementState
        # print('curtrent state',self.character.movementState, 'prev',self.previousState)
        
        #walk out of parry
        # if self.isWalking==True and self.character.:
            

########Character set character direction
        if self.character.movementState == "landing":
            self.idleDirection = self.charM.getH(render)

        if self.previousState != self.currentState and self.character.isdodging == False and self.currentState == "ground" and self.previousState != "Falling":
            self.enterIdle()

        #             self.charM.stop()      
        if self.character.movementState == "ground" or self.character.movementState =="attacking" and self.character.isAttacking ==False:
            if self.character.isdodging == False:
                self.isIdle = False
                self.isWalking = False
                # self.attackWalking = False
            
            if self.character.movementState!= "attacking":
                self.GroundStates()

        if self.character.movementState == "jumping" or self.character.movementState == "falling":
        # if self.character.movementState in self.character.airstates:
            self.isIdle = False
            self.isWalking = False
            # self.attackWalking = False
            self.AirStates()

        self.wallGrabcheck()

        if self.character.movementState == "attacking" or self.character.movementState == "dodging":
            self.isWalking = False
          
        # print('State:',self.character.movementState)
########FOR ANIMS
    
        newCharPos = self.character.getPos(render)
        self.delta = (newCharPos - oldCharPos) #+ 1
        return# task.cont
    def wallGrabcheck(self):
            #Need to add timer  here
            def end():
                print('end wallgrab or run')
                self.wallruncam = False
                self.character.movementState = "endaction"
                # self.character.wallRun[0] = None
                self.character.WGAngle = None
                self.character.wallray.reparentTo(render)
                self.character.wallray.setPos(self.charM, (0,20,20))

                # self.character.wallRunVec = 0
                
                # taskMgr.remove('wgtimer')
                # self.wallGrabTimer=None
            # print(self.character.wallJump, 'WC',self.character.wallContact)
            
            if self.character.wallContact == True and self.trigger_r.value > .1:
                self.wallJumpEnabled = True
            else:
                self.wallJumpEnabled = False
            if self.character.movementState == 'wallgrab':
                # if self.wallGrabTimer == None:
                #     self.wallGrabTimer = taskMgr.add(self.timer,'wgtimer')

                
                # print(self.character.WGAngle)
                # print(self.character.wallRun)
                # if self.wallruncam==False:
                #     self.recenterCam()
                if self.leftValue != 0:
                    self.character.wallRun[4] = 'wallrunning'
                    # self.character.wallray.reparentTo(self.charM)
                elif self.leftValue == 0:
                    self.character.wallRun[4] = 'wallgrabbing'

                # print('wg angle',self.character.WGAngle)
                
                if self.character.WGAngle == None:
                    self.character.WGAngle = self.character.wallRun[0]

                # if self.character.wallRun[0]== None:
                self.charM.setH(render, self.character.WGAngle)
                # self.character.movementParent.setH(render, self.character.WGAngle)
                self.character.wallspeed = self.leftValue * 3

            if self.character.wallJump == True:
                return
            # self.character.d2wall<2self.character.nearWall ==True
            if  self.character.wallContact == True and self.character.nearWall == True and self.trigger_r.value > .1:# and self.character.canWallGrab==True: #and self.character.canWallGrab ==True:
                if self.character.movepoints!=3:
                    self.character.movepoints = 3
                self.character.movementState = "wallgrab"
                # self.character.canWallGrab = False
                
            if self.character.movementState == "wallgrab": 
                if self.trigger_r.value <.1 or self.character.nearWall == False:#self.character.d2wall>2 :
                    print('its over')
                    end()

######3Char model handler---------
    def GroundStates(self):
        """set character's direction when on ground/walking"""
        # sets direction of character when on ground
        # if self.character.isdodging ==False:
        # print('groundstates')
        self.isIdle=True
        self.isWalking = False
        # self.attackWalking = False
        # self.charM.setHpr(0,0,0)
        # if self.character.isdodging:
        #     self.isIdle=False
        #     self.isWalking = False

        
# ########KEYBOARD
#         if self.character.movementState == "dodging":
#             self.isIdle = False

#         if self.character.movementState == "landing":
#             self.isIdle = False

        # anim=self.charM.getCurrentAnim()
        # if anim not in ("walk","idle","land" ,None):
        #     return task.cont

        if self.isIdle and self.lockedOn!=True:
            # self.enterIdle()
            # self.groundstates = 'idle'
            self.charM.setH(render, self.idleDirection) 
            # taskMgr.remove(self.enterIdle)
            # if(anim!="idle"):
            #     self.charM.loop("idle") 
        
        if inputState.isSet('forward') : 
            self.isIdle = False
            if self.character.isdodging ==False:
                self.isWalking = True
            self.charM.setH(self.character.movementParent, 180)
            self.idleDirection = self.charM.getH(render)
            # self.charM.setPlayRate(1.0, "walk")
            # if(anim!="walk"):
            #     self.charM.loop("walk")             

        if inputState.isSet('left'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, -90)
            self.idleDirection = self.charM.getH(render)
            if self.character.isdodging ==False:
                self.isWalking = True
        #     self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")  

        if inputState.isSet('right'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, 90)
            self.idleDirection = self.charM.getH(render)
            if self.character.isdodging ==False:
                self.isWalking = True
        #     self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")

        if inputState.isSet('right') and inputState.isSet('forward'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, 135)
            self.idleDirection = self.charM.getH(render)
            # self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")        

        if inputState.isSet('left') and inputState.isSet('forward'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, -135)
            self.idleDirection = self.charM.getH(render)
            # self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")   

        if inputState.isSet('reverse') : 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, 0)
            self.idleDirection = self.charM.getH(render)
            if self.character.isdodging ==False:
                self.isWalking = True
        #     self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")

        if inputState.isSet('right') and inputState.isSet('reverse'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, 45)
            self.idleDirection = self.charM.getH(render)
        #     self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")        

        if inputState.isSet('left') and inputState.isSet('reverse'): 
            self.isIdle = False
            self.charM.setH(self.character.movementParent, -45)
            self.idleDirection = self.charM.getH(render)
        #     self.char.setPlayRate(1.0, "walk")
        #     if(anim!="walk"):
        #         self.char.loop("walk")   
        # 
    #####controller
        if self.gamepad:
            
            # self.enterIdle()
            # self.charM.setH(render, self.idleDirection) 
            # self.charM.setH(self.character.movementParent, -45)
            #self.left_x self.left_y
            # leftStickX = round(self.left_x.value * 10)
            # leftStickY = round(self.left_y.value * 10)
            # # print(leftStickX, leftStickY)
            # self.charM.setH(self.idleDirection)

            # if abs(leftStickX) > 1 or abs(leftStickY) > 1:
            if self.leftjoystick==True:
                self.isIdle = False
                # if self.character.isdodging ==False: #and self.character.movementState!="attacking":
                #     self.attackWalking = True
                # self.groundstates = 'walking'
                # set angle
                # if leftStickY != 0 or leftStickX != 0 :
                if self.leftX!=0 or self.leftY!=0:
                # if self.leftValue!=0:
                    # print('wwjwjwjwj')
                    self.isIdle = False
                    if self.character.isdodging ==False and self.character.movementState!="attacking":
                        self.isWalking = True
                    # if self.character.isdodging ==False: #and self.character.movementState!="attacking":
                    #     self.attackWalking = True
                        
                # if self.character.movementState == "attacking":
                #     if self.character.isAttacking == False:
                #         self.isWalking = True
                    # h = math.atan2(leftStickX, -leftStickY)
                    # self.angle = math.degrees(h) #* -1
                    # print(angle)
                    # print(leftStickX, leftStickY, 'angle:', self.angle)
                    if self.character.isdodging == False and self.character.movementState!="attacking":
                        if self.lockedOn ==False:
                            self.charM.setH(self.angle)
                        self.idleDirection = self.charM.getH(render)

    def enterIdle(self):
  
            self.idleDirection = self.charM.getH(render)
            # self.idleDirection = self.charM.getQuat().getForward() * -50
            # print('enter idle, direction -',self.idleDirection)

        

    def AirStates(self):

     
        if inputState.isSet('forward') and self.character.isdodging == False: 
            self.charM.setP(self.character.movementParent, 10)
        
        if inputState.isSet('right') and self.character.isdodging == False: 
            right = LerpHprInterval(self.charM,.1, HPR, (180,0,-10))
            leanright = Sequence(right)
            leanright.start()
            #  self.charM.setR(self.character.movementParent, -10)
        
        if inputState.isSet('left') and self.character.isdodging == False: 
            self.charM.setR(self.character.movementParent, 10)

        if inputState.isSet('reverse') and self.character.isdodging == False: 
            self.charM.setP(self.character.movementParent, -10)
            #####controller
        # if self.gamepad:
        #     leftStickX = round(self.leftX* 15)
        #     leftStickY = round(self.leftY * 15)
            
        #     self.charM.setP(render, -leftStickY)
        #     self.charM.setR(render,leftStickX)
