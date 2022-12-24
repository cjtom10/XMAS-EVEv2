from direct import showbase
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "win-size 1280 768")
loadPrcFileData("", "sync-video t")
import sys
import time
import direct.directbase.DirectStart

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from panda3d.core import *
from panda3d.bullet import *

import simplepbr
import gltf

from mouseLook import MouseLook
from gamepad import GamepadInput
import math

base.disableMouse()
ml = MouseLook()
ml.setMouseModeRelative(True)
ml.setCursorHidden(True)
ml.centerMouse = True
ml.mouseLookMode = ml.MLMOrbit
ml.enable()

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

from kcc import PandaBulletCharacterController

class Game(DirectObject, GamepadInput):

    def __init__(self):
        super().__init__()
        gltf.patch_loader(loader)
        pipeline = simplepbr.init()
        pipeline.use_normal_maps = True
        pipeline.use_occlusion_maps = True
        GamepadInput.__init__(self)
        self.gamepad = None
    # now, x and y can be considered relative movements

        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)

        skybox = loader.loadModel('../models/skybox.egg')
        skybox.setScale(100)
        skybox.reparentTo(render)
        
        self.resetCam()
        # base.cam.setPos(0, -7, 10)
        # base.cam.lookAt(0, 10, 0)

        ml.resolveMouse()
        
        # Input
        self.accept('escape', self.doExit)
        self.accept('space', self.doJump)
        
        self.accept('space', self.doJump)
        self.accept('c', self.doCrouch)
        self.accept('c-up', self.stopCrouch)

        self.accept('f', self.recenterCam)
        
        self.accept('control', self.startFly)
        self.accept('control-up', self.stopFly)
        
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnLeft', 'q')
        inputState.watchWithModifiers('turnRight', 'e')
        
        inputState.watchWithModifiers('run', 'shift')
        # inputState.watchWithModifiers('jump', 'space')

        inputState.watchWithModifiers('flyUp', 'r')
        inputState.watchWithModifiers('flyDown', 'f')


        # Task
        taskMgr.add(self.update, 'mainUpdateTask')
        
        # Physics
        self.setup()

        self.camBuffer = self.character.movementParent.attachNewNode('camMovebuffer')
        self.camBuffer.setPos((0,-10,5))
        
        self.camLookat = self.character.movementParent.attachNewNode('camLookat')
        self.camLookat.setPos(0, 5, 0)

        # self.accept("w-up", self.recenterCam)
        # self.accept("a-up", self.recenterCam)
        # self.accept("s-up", self.recenterCam)
        # self.accept("d-up", self.recenterCamR)

########LVLbsetup
        # lvl = loader.loadModel('../models/buildingz.glb')
        # lvl.reparentTo(self.worldNP)    
        # self.make_collision_from_model(lvl, 0, 0, self.world, (lvl.get_pos()))
         
        # _____HANDLER_____
    
    def resetCam(self):
        initcamPos = (0,-10,5)
        base.cam.setPos(initcamPos)
        base.camera.setP(render, -90)
        
        # base.cam.lookAt(self.camBuffer, (0, 10, 0))
        # print(initcamPos)
        # print('camreset')

    def recenterCam(self):
        direction = self.character.char.getH()
        base.camera.setH(direction)
        self.character.char.setH(self.character.movementParent, 180)
        # base.cam.setPos(0,20,23)
        # base.cam.lookAt(self.camLookat)
        # base.cam.setPos(self.camBuffer, 0)
        # base.cam.lookAt(self.camBuffer, (0, 10, 0))
       
        # print('cam recentered')

    def doExit(self):
        self.cleanup()
        sys.exit(1)
    
    def doJump(self):
        self.character.startJump(5)
    
    def doCrouch(self):
        self.character.startCrouch()
    
    def stopCrouch(self):
        self.character.stopCrouch()
    
    def startFly(self):
        self.character.startFly()
    
    def stopFly(self):
        self.character.stopFly()
    def actionA(self):
        print('a pressed')
    def actionB(self):
        print('b pressed')
    def actionX(self):
        print('x pressed')
    def actionY(self):
        print('y pressed')
    def actionrb(self):
        print('rb pressed')
    def actionlb(self):
        print('lb pressed')
    # def processInput(self, dt):

    #     speed = Vec3(0, 0, 0)
    #     omega = 0.0
        
    #     v = 5.0
        
    #     if inputState.isSet('run'): v = 15.0

    #     if inputState.isSet('forward'): speed.setY(v)
    #     if inputState.isSet('reverse'): speed.setY(-v)
    #     if inputState.isSet('left'):    speed.setX(-v)
    #     if inputState.isSet('right'):   speed.setX(v)
        
    #     if inputState.isSet('flyUp'):   speed.setZ( 2.0)
    #     if inputState.isSet('flyDown'):   speed.setZ( -2.0)
        
    #     if inputState.isSet('turnLeft'):  omega =  120.0
    #     if inputState.isSet('turnRight'): omega = -120.0

    #     self.character.setAngularMovement(omega)
    #     self.character.setLinearMovement(speed, True)
    def processInput(self, dt):

        self.speed = Vec3(0,0,0)
        omega = 0.0
        
        v = 5.0
        vx = .50
        vy = .50
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
      
            x = self.leftX / 10
            y = self.leftY / 10
           
            # print(self.left_x.value, self.left_y.value)
            # h = math.atan2(-self.left_x.value, self.left_y.value )
            h = math.atan2(-x, y)
            self.angle = math.degrees(h) 
            # vx*= round(self.left_x.value) * 24 
            # vy*= round(self.left_y.value) * 24
            # if self.character.wallJump ==True and self.trigger_r.value > .1:
            #     self.character.movementState = "wallrun"
            vx*= self.leftX * 24 
            vy*= self.leftY * 24
            # print(self.leftX, self.leftY)
            if self.character.movementState == "jumping" or self.character.movementState == 'falling':
                vx *=.2
                vy *= .2


            # ADD DELAy here
            self.speed.setX(vx)
            self.speed.setY(vy)
        # if self.character.movementState!="attacking" and self.character.movementState  not in self.character.nonInputStates:
        if self.character.movementState=="attacking": #or self.character.movementState   in self.character.nonInputStates:
            self.speed = Vec3(0,0,0)
            # self.character.setAngularMovement(omega)
            # self.character.setLinearMovement(self.speed, True)
        self.character.setAngularMovement(omega)
        self.character.setLinearMovement(self.speed, True)
        
    def update(self, task):
        dt = globalClock.getDt()
        
        self.processInput(dt)
        
        oldCharPos = self.character.getPos(render)
        self.character.setH(base.camera.getH(render))
        self.character.update() # WIP
        # self.character.updatechar
        newCharPos = self.character.getPos(render)
        delta = (newCharPos - oldCharPos) #+ 1
        
        self.world.doPhysics(dt, 4, 1./120.)
        
        ml.orbitCenter = self.character.getPos(self.worldNP)

        camDist = base.camera.getPos(self.character.movementParent)
        camDistX = base.camera.getX(self.character.movementParent)
        camDistY = base.camera.getY(self.character.movementParent)
        camDistZ = base.camera.getZ(self.character.char) * 100
        camPos = base.camera.getPos(render)

        cambuffer = NodePath('cambufffer')
        # cambuffer.setPos(newCharPos)
        cambuffer.reparentTo(self.character.movementParent)

        clampnode = base.camera.attachNewNode('clamp')
        camlimit = base.camera.getP(self.character.movementParent) 

        if camlimit < -40:
            ml.toplimited = True
            # print('upper limit')
        elif camlimit > 20:
            ml.bottomlimited = True
            # print('lower limit')
        else: 
            ml.toplimited = False
            ml.bottomlimited = False
            # print('ok uwu')

        # print(camlimit)

 #######       
        # def clamp(value, a, b):
    
        #     if a < b:
        #         if value < a:
        #             return a
        #         elif value > b:
        #             return b
        #         else:
        #             return value
        #     else:
        #         if value < b:
        #             return b
        #         elif value > a:
        #             return a
        #         else:
        #             return value

        # clamp(camlimit, -80, -30)
        

        def moveCam(node):
            # print('distance:',camDistX)
            # base.camera.setPos(camPos + delta)
            node.setPos(camPos + delta)
        
        moveCam(cambuffer)  
        moveCam(base.camera)  

######FIX THIS LATER--slight offset between char and cam mvt        
        # print(camDistX)
        # if camDistX > 1 or camDistX < -1:
        #     moveCam(base.camera)
        # elif camDistY > 1 or camDistY < -1:
        #     moveCam(base.camera)

        # def recenterCam():
        #     print(' cma reset yay')
        #     pos = cambuffer.getPos(self.character.movementParent)
        #     print('bufferpos:', pos)
        #     print('camerapose:', base.camera.getPos(self.character.movementParent))
        #     base.camera.setPos(pos)
        
        # reset cam when key rerleased
        # self.accept("w-up", recenterCam)
        # self.accept("a-up", self.recenterCam)
        # self.accept("s-up", self.recenterCam)
#####        # self.accept("d-up", self.recenterCam)

        
        return task.cont
            
    #     base.camera.setPos(self.character.getPos(render) )
    def make_collision_from_model(self, input_model, node_number, mass, world, target_pos):
            # tristrip generation from static models
            # generic tri-strip collision generator begins
            geom_nodes = input_model.find_all_matches('**/+GeomNode')
            geom_nodes = geom_nodes.get_path(node_number).node()
            # print(geom_nodes)
            geom_target = geom_nodes.get_geom(0)
            # print(geom_target)
            output_bullet_mesh = BulletTriangleMesh()
            output_bullet_mesh.add_geom(geom_target)
            tri_shape = BulletTriangleMeshShape(output_bullet_mesh, dynamic=False)
            print(output_bullet_mesh)

            body = BulletRigidBodyNode('input_model_tri_mesh')
            np = render.attach_new_node(body)
            np.node().add_shape(tri_shape)
            np.node().set_mass(mass)
            np.node().set_friction(0.01)
            np.set_pos(target_pos)
            np.set_scale(1)
            # np.set_h(180)
            # np.set_p(180)
            # np.set_r(180)
            np.set_collide_mask(BitMask32.allOn())
            world.attach_rigid_body(np.node())


    
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

        # Ground
        shape = BulletPlaneShape(Vec3(0, 0, 1.0), 0)
        
        np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
        np.node().addShape(shape)
        np.setPos(0, 0, 0)
        np.setCollideMask(BitMask32.allOn())
        
        cm = CardMaker('ground')
        cm.setFrame(-20, 20, -20, 20)
        gfx = render.attachNewNode(cm.generate())
        gfx.setP(-90)
        gfx.setZ(-0.01)
        gfx.setColorScale(Vec4(0.4))
        
        self.world.attachRigidBody(np.node())
        
        
        # X = 0.3
        # Y = 4.0
        # Z = 1.5
        
        # stepsY = 1.5
        
        # shapesData = [
        #     dict(name = 'wall0', size = Vec3(X, Y, Z), pos = Point3(Y*2.0, -(Y + stepsY), Z), hpr = Vec3()),
        #     dict(name = 'wall1', size = Vec3(X, Y, Z), pos = Point3(Y*2.0, (Y + stepsY), Z), hpr = Vec3()),
            
        #     dict(name = 'wall4', size = Vec3(X, Y, Z), pos = Point3(Y, (Y*2.0 + stepsY - X), Z), hpr = Vec3(90, 0, 0)),
        #     dict(name = 'wall5', size = Vec3(X, Y, Z), pos = Point3(-Y, (Y*2.0 + stepsY - X), Z), hpr = Vec3(90, 0, 0)),
        #     dict(name = 'wall6', size = Vec3(X, Y, Z), pos = Point3(Y, -(Y*2.0 + stepsY - X), Z), hpr = Vec3(90, 0, 0)),
        #     dict(name = 'wall7', size = Vec3(X, Y, Z), pos = Point3(-Y, -(Y*2.0 + stepsY - X), Z), hpr = Vec3(90, 0, 0)),
            
        #     dict(name = 'ceiling', size = Vec3(Y, Y*2.0, X), pos = Point3(0, -(Y + stepsY - X), Z), hpr = Vec3(90, 0, 0)),
        #     dict(name = 'ceiling', size = Vec3(Y, Z, X), pos = Point3(-Z, (Y + stepsY - X), Z*2.0-X), hpr = Vec3(90, 0, 0)),
        #     dict(name = 'ceiling', size = Vec3(Y, Z, X), pos = Point3(Z, (Y + stepsY - X), Z*4.0-X), hpr = Vec3(90, 0, 0)),
            
        #     # CHANGE ROTATION TO TEST DIFFERENT SLOPES
        #     dict(name = 'slope', size = Vec3(20, stepsY+Y*2.0, X), pos = Point3(-Y*2.0, 0, 0), hpr = Vec3(0, 0, 50)),
        # ]
        
        # for i in range(10):
        #     s = Vec3(0.4, stepsY, 0.2)
        #     p = Point3(Y*2.0 + i * s.x * 2.0, 0, s.z + i * s.z * 2.0)
        #     data = dict(name = 'Yall', size = s, pos = p, hpr = Vec3())
        #     shapesData.append(data)
        
        # for data in shapesData:
        #     shape = BulletBoxShape(data['size'])
            
        #     np = self.worldNP.attachNewNode(BulletRigidBodyNode(data['name']))
        #     np.node().addShape(shape)
        #     np.setPos(data['pos'])
        #     np.setHpr(data['hpr'])
        #     np.setCollideMask(BitMask32.allOn())
            
        #     self.world.attachRigidBody(np.node())
        
        # shape = BulletSphereShape(0.5)
        # np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ball'))
        # np.node().addShape(shape)
        # np.node().setMass(10.0)
        # np.setPos(13.0, 0, 5.0)
        # np.setCollideMask(BitMask32.allOn())
        # self.world.attachRigidBody(np.node())
        
        # shape = BulletBoxShape(Vec3(0.5))
        # np = self.worldNP.attachNewNode(BulletRigidBodyNode('Crate'))
        # np.node().addShape(shape)
        # np.node().setMass(10.0)
        # np.setPos(-13.0, 0, 10.0)
        # np.setCollideMask(BitMask32.allOn())
        # self.world.attachRigidBody(np.node())
        
        
        shape = BulletBoxShape(Vec3(1, 1, 2.5))
        self.ghost = self.worldNP.attachNewNode(BulletGhostNode('Ghost'))
        self.ghost.node().addShape(shape)
        self.ghost.setPos(-5.0, 0, 3)
        self.ghost.setCollideMask(BitMask32.allOn())
        self.world.attachGhost(self.ghost.node())
        
        taskMgr.add(self.checkGhost, 'checkGhost')


        # self.actor = Character.actor
        self.character = PandaBulletCharacterController(self.world, self.worldNP, 3, 1.5, 0.5, 1)
        self.character.setPos(render, Point3(0, 0, 0.5))
        
        # taskMgr.add(self.character.updatechar, "updateCharacter")
    
    def checkGhost(self, task):
        pass
        # ghost = self.ghost.node()
        # for node in ghost.getOverlappingNodes():
        #     print ("Ghost collides with", node)
        # return task.cont

game = Game()
run()


