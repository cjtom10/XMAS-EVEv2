from enum import auto
from itertools import count
from typing import Sequence
from panda3d.bullet import *  
from panda3d.core import *      
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.IntervalGlobal import *



from direct.actor.Actor import Actor
class Level:#makd this a separate object
        def __init__(self, NP, world, triCount=3, boxCount=0):
                # NP.setAttrib(LightRampAttrib.makeSingleThreshold(0, 1))
                self.NP = NP
                self.world=world
                skybox = loader.loadModel('../models/inkskybox2.glb')
                skybox.setPos(0,0,0)
# skybox = loader.loadModel('../models/skybox.egg')
                
                skybox.setDepthWrite(False)
                # skybox.setTransparency(True)
                base.setBackgroundColor(0,0,0)
                skybox.reparentTo(base.camera)
                skybox.setCompass()

                
                
                # mtn = loader.loadModel('../models/mtn.glb')
                # mtn.setPos(mtn1pos)
                # mtn.setScale(10)
               
                # mtn.reparentTo(render)
                # mtn.instanceTo(mtn2) 
                # mtn2.setPos(-50, -200,-30)

                # mtn3 = loader.loadModel('../models/mtn2.glb')
                # mtn3.setPos(mtn.getPos())
                # mtn3.setY(4)
                # mtn3.setScale(4)
                # mtn3.reparentTo(render)

                
                # mtn3.setShaderAuto()
                # mtn3.setAttrib(LightRampAttrib.makeSingleThreshold(0, 0.5))
# 
                # mtn.setPos(-20, 10, -55)
                # rok.rehparentTo(render)
          
                # self.grindseq = Sequence()
        

#light setup
                sun = DirectionalLight("sun")
                sun.set_color_temperature(6000)
                sun.color = sun.color * 4
                sun_path = render.attach_new_node(sun)
                sun_path.set_pos(-10, -50, 100)
                sun_path.look_at(0, 0, 0)
                # sun_path.hprInterval(10.0, (sun_path.get_h(), sun_path.get_p() - 360, sun_path.get_r()), bakeInStart=True).loop()

                
                NP.set_light(sun_path)

                # Enable shadows; we need to set a frustum for that.
                sun.get_lens().set_near_far(1, 30)
                sun.get_lens().set_film_size(20, 40)
                sun.show_frustum()
                sun.set_shadow_caster(True, 4096, 4096)

                # Also add an ambient light and set sky color.
                skycol = VBase3(135 / 255.0, 206 / 255.0, 235 / 255.0)
                base.set_background_color(skycol)

                alight = AmbientLight("sky")
                alight.set_color(VBase4(skycol * 0.04, 1))
                alight_path = render.attach_new_node(alight)
                NP.set_light(alight_path)

                plight = PointLight('plight')
                plNP = render.attachNewNode(plight)
                plNP.setPos(0,0,100)
                NP.set_light(plNP)

##end light setup
                # self.shader = Shader.load(Shader.SL_GLSL, "../shaders/vert.vert", "../shaders/frag.frag")

                self.arena = NodePath('arena')
                self.arenaGP = loader.loadModel('../models/lvl/arenaGP.glb')
                self.arenaGP.reparentTo(self.arena)
                self.arena.reparentTo(NP)
                self.arena.setCollideMask(BitMask32.allOn())
                # print('arena geoms', self.arenaOF.getGeoms())
                self.grapplePoints = []

                # self.observePA = self.arenaOF.find('observepa')
                # self.enterPA = self.arenaOF.find('enterpa')
                # self.staticMech = loader.loadModel('../models/lvl/staticMech.glb')
                # self.staticMech.reparentTo(self.NP)
                        # self.arena = loader.loadModel('../models/lvl/arenaMECH.glb')
                
                self.geomcount = 5 #used for making tris and generationg collisions w arena
                for i in range(self.geomcount):
                        self.findTris(f'tri{i}',self.arenaGP)

                # for i in range(12):# mech arena - 12 tris on foot - 7
                #         self.findTris(f'tri{i}',self.arena)
                #arena sensor for camera
                # for i in range(2, 1):
                # arenasensors = loader.loadModel('../models/lvl/arenaOFsensors.glb')
                # box = BulletBoxShape(Vec3(72, 92, 22))
                # self.sensor1 = self.NP.attachNewNode(BulletGhostNode('arenasensor1'))
                # self.sensor1.node().addShape(box)
                # self.sensor1.setPos(arenasensors.find('sensor1').getPos(render))
                # self.sensor1.setCollideMask(BitMask32(0x10))
                # self.world.attachGhost(self.sensor1.node())
                # self.sensor2 = self.NP.attachNewNode(BulletGhostNode('arenasensor2'))
                # self.sensor2.node().addShape(box)
                # self.sensor2.setPos(arenasensors.find('sensor2').getPos(render))
                # self.sensor2.setCollideMask(BitMask32(0x10))
                # self.world.attachGhost(self.sensor2.node())


                self.emptyPos(self.arenaGP)
                self.findGP(5,self.arenaGP)
           
                self.spawnNo = 0

                # rock = loader.loadModel('../models/rock1.glb')
                # rock.reparentTo(NP)
                # plane=BulletPlaneShape()
                # ground = self.world.attach
                self.groundNP = self.NP.attachNewNode(BulletRigidBodyNode('Ground'))
                self.groundNP.node().addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
                self.groundNP.setPos(0, 0, -200)
                self.groundNP.setCollideMask(BitMask32.allOn())

                self.world.attachRigidBody(self.groundNP.node())
        def arenaSensorcheck(self, sensor):
                ghost = sensor.node()
                print(ghost.getNumOverlappingNodes())
                # for node in ghost.getOverlappingNodes():
                #         print(node)
                if 'BulletCharacterControllerNode' in ghost.getOverlappingNodes():
                        print('im in')
        def switchArena(self):
                return
        def findGP(self, no, arena):
                for x in range(no):
                        self.grapplePoints.append(arena.find(f'gp{x}'))

                


        def emptyPos(self, lvl):
                """includes positions for inactive enemies as well as enemy spawn points TODO add spawn pooints"""
                # self.playerSpawn = (0,0,0) # onfoot spawn

                self.inactiveenemypos = [] 
                self.enemyspawnpoints = []
                self.turretPos = []
                for i in range(3):
                        self.turretPos.append(lvl.find(f'turretpos{i}').getPos(render))
                for i in range(5):
                        self.inactiveenemypos.append(lvl.find(f'enemypos{i}').getPos(render))   
                for i in range(3):
                        self.enemyspawnpoints.append(lvl.find(f'enemySpawn{i}').getPos(render))

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
  
        #     np.set_collide_mask(BitMask32.allOn())
            np.set_collide_mask(BitMask32.bit(0))
            world.attach_rigid_body(np.node())
 
        def findTris(self, name, model):
                shape = model.find(name)
                self.make_collision_from_model(shape,0,0,self.world,shape.getPos())

        # def makelvlcollisions(self):
                # iterate thru points in loaded level, for boxes, create box shape based on length of edges. 
        def box(self, x,y,z,number,parent, pos):
                dx = x/2
                dy = y/2
                dz=z/2
                box = BulletBoxShape((dx, dy, dz)) 
                np = parent.attachNewNode(BulletRigidBodyNode(f'box{number}'))
                np.node().addShape(box)
                # np.setPos(parent.find(f'box{number}').getPos())
                np.setPos(pos)
                np.setH(180)
                self.world.attachRigidBody(np.node())
                          
        # def levelunit(self, geom,shape, pos):
        #         ##load model and create collision shape independent of moedl

        #         geom.reparentTo(NP)
        #         geom.setPos(pos)
        #         collisionposition = geom.find('collisionposition')

        #         np = self.NP.attachNewNode(BulletRigidBodyNode('lvlunit'))
        #         np.node().addShape(shape)
        #         mask = BitMask32.bit(0) | BitMask32.bit(2)
        #         # np.setCollideMask(BitMask32.allOn())
        #         np.setCollideMask(mask)
        #         self.world.attachRigidBody(np.node())
        #         np.setPos(collisionposition.getPos())

        # # Ground
                #create grindrail
        def jumpPad(self, pos):
                model = loader.loadModel('../models/jumppad.glb')
                model.setPos(pos)
                # shape = BulletBoxShape((2,2,.3))
                # hb = 

        def railv3(self,number, geom, hitbox, points, count):

                geom.reparentTo(self.NP)
                self.rail = geom
                self.rail.setZ(-.5)
                self.make_collision_from_model(geom, 0, 0, self.world, (geom.getPos()))

                hb = self.make_ghost_from_model(hitbox,0,  self.world, (hitbox.getPos()))
                self.hbnode = self.NP.attachNewNode(BulletGhostNode('railcheck'))
                self.hbnode.node().addShape(hb)
                self.world.attachGhost(self.hbnode.node())

                self.points = []
                self.pointPos = []
                self.pointH = []
                self.relpointpos = []
                for i in range(count):
                       
                        # self.points.append(points.find(f'R1{i}'))
                        # self.pointPos.append(points.find(f'R1{i}').getPos(render))
                        # self.pointH.append(points.find(f'R1{i}').getHpr(render))
                        self.points.append(points.find(f'R{number}{i}'))
                        self.pointPos.append(points.find(f'R{number}{i}').getPos(render))
                        self.pointH.append(points.find(f'R{number}{i}').getHpr(render))
                        self.relpointpos.append(points.find(f'R{number}{i}').getPos(self.character.movementParent))
                #End caps - if you jump or hit these while grinding you enter 'exitgrind'
                shape = BulletBoxShape(Vec3(1))
                endcap1 = self.NP.attachNewNode(BulletGhostNode('endcap1'))
                endcap2 = self.NP.attachNewNode(BulletGhostNode('endcap2'))
                endcap1.node().addShape(shape)
                endcap2.node().addShape(shape)
                # end = endcaps.node().addShape(shape)
                endcap1.setPos(self.pointPos[0])
                endcap2.setPos(self.pointPos[count-1])
                self.world.attachGhost(endcap1.node())
                self.world.attachGhost(endcap2.node())
                # print('pointpos', self.pointPos, 'pointposrel', self.relpointpos)
                taskMgr.add(self.detectgrind)


        
        def detectgrind(self):
                Pos = self.charM.getPos(render)
                
                # if self.grindseq != None:
                        # print('grimdseequence4ee')

                # closestpoint = min(self.pointPos, key=lambda pt: LVector3f(abs((Pos - pt).y)))#IMPORTANT Pt is x y or z depernding on which axisd the rail is on,abs((Pos - pt).y),abs((Pos - pt).z)))
                closestpoint = min(self.pointPos, key=lambda pt: (Pos - pt).length())
                result = self.world.contactTest(self.hbnode.node())
                for  contact in result.getContacts():
                        # print('currentpos', self.character.getPos(), 'node pos', self.character.movementParent.getPos())
                        node = contact.getNode0()
                        if 'Character' in str(node):
                                
                                self.character.movementState = 'grinding'
                                for x in range(len(self.points)):
                                        Dir = self.charM.getH(self.points[x]) #if Dir is negative, reverse uwu
                                        PosRelative = self.charM.getY(self.points[x])#if this is negative, move to closest, if notr, move to next
                                        print('points H',self.points[x].getH(), 'dir',Dir, 'x:',x)
                                        if closestpoint == self.pointPos[x]:

                                                if Dir >= 0:
                                                        print('forward')
                                                        # self.character.grindvec = self.pointPos[x+1] - self.pointPos[x]
                                                        # self.character.grinddirection = self.character.grindvec
                                                      
                                                        if PosRelative < 0:#move to point
                                                                self.doGrind(self.character.movementParent,self.charM, .5, x, True)                                                                
                                                                # print('jaboo')
                                                        if PosRelative > 0:
                                                                self.doGrind(self.character.movementParent,self.charM, .5, x, False)                                                               
                                                                # print('nextpoint')
                                                if Dir < 0:
                                                        print('reverse')
                                                        if PosRelative < 0:#move to point
                                                                self.doGrind(self.character.movementParent,self.charM, .2, x, True, reverse = True)
                                                                
                                                                # print('negative jaboo')
                                                        if PosRelative > 0:
                                                                
                                                                self.doGrind(self.character.movementParent,self.charM, .2, x, False, reverse=True)
                                        # if self.character.movementState == 'jumping':
                                        #         self.exitGrind()                        
                                                # print('fniish')                
                                                # print(x, 'Direction',Dir,'position', PosRelative )
                return task.cont
        def doGrind(self, node, model, t, n, p1, reverse = False):
                # print('n', n, 'grindvec', self.character.grindvec)
                if self.grindseq == None:        
                        self.grindseq = Sequence()
                
                        if reverse == False:
                                if not p1:
                                        n+=1
                                self.character.grindvec = self.points[n].getPos(self.character.movementParent) - self.points[n-1].getPos(self.character.movementParent)
                                for i in range(n, len(self.points)):
                                        par = Parallel(LerpPosInterval(node, t, self.pointPos[i]),
                                                LerpPosInterval(self.camtarg, t, self.pointPos[i]),
                                                LerpHprInterval(model, t, ((self.pointH[i]))))
                                                # LerpHprInterval(base.camera, t, self.pointHpr[i]))
                                              
                                        self.grindseq.append(par)
                                        # t-=.1
                        if reverse == True:
                                if p1:                                
                                        n-=1
                                # self.character.grindvec = self.pointPos[n] - self.pointPos[n+1]
                                self.character.grindvec = self.points[n].getPos(self.character.movementParent) - self.points[n+1].getPos(self.character.movementParent)
                                
                                for i in range(n, -1, -1):
                                        par = Parallel(LerpPosInterval(node, t, self.pointPos[i]),
                                                LerpPosInterval(base.camera, t, self.pointPos[i]),
                                                LerpHprInterval(model, t,(self.pointH[i]) ))
                                        self.grindseq.append(par)        

                        self.grindseq.start()
                else:
                        return
        def exitGrind(self):
                if self.grindseq.isPlaying():
                        self.grindseq.pause()
                        print('pause grind!')
                self.grindseq = None
        def grindHB(self, task):
                # railcheck = self.railHB.node()
                pass
                # vec = None
                # # Pos = self.charM.getPos(render)
                # distances = []
                # Pos = self.charM.getPos(self.NP) 
                # # closestpoint = min(self.grindpoints, key=lambda pt: LVector3f(abs((Pos - pt).x),abs((Pos - pt).y),abs((Pos - pt).z)))
                
                # for x in range(len(self.railzones)):
                #         Dir = self.charM.getH(self.grindDirection[x])
                #         # grindcenter = self.charM.getX(self.grindDirection[x]) 
                #         # print(self.railzones[x].node().getOverlappingNodes())
                #         result = self.world.contactTest(self.railzones[x].node())
                #         for contact in result.getContacts():
                #                 # print('node1:', contact.getNode1(), 'node0:', contact.getNode0())
                #                 node = contact.getNode0()
                #                 if 'Character' in str(node):
                #                         # if self.character.previousrailzone != x:
                #                         self.character.setX(self.grindDirection[x], 0) 
                #                         base.camera.setX(self.grindDirection[x], 0) 
                #                                 # self.character.previousrailzone = x
                #                                 # print('uwu')

                #                         # print('node1:', contact.getNode1(), 'node0:', contact.getNode0())
                #                         self.character.movementState = 'grinding'
                #                         # print('centered:',self.character.grindcenter)
                #                         if abs(Dir) < 90:
                #                                 self.charM.setH(self.grindDirection[x], 0)
                #                                 self.character.grinddirection = self.grindpoints[x+1] - self.grindpoints[x]
                #                         if abs(Dir) > 90:
                #                                 self.charM.setH(self.grindDirection[x], 180)
                #                                 self.character.grinddirection = self.grindpoints[x] - self.grindpoints[x + 1]
                                        # print('on rail', x, 'direction:', Dir)
                                        
                        
                        # for node in self.railzones[x].node().getOverlappingNodes():
                        #         if 'Character' in str(node):
                        #                 # print(self.grindpoints)
                        #                 # self.character.movementState = 'grinding'
                                        
                        #                 self.character.grinddirection = self.grindpoints[x+1] - self.grindpoints[x]

                                        
                        #                 print('on rail', x, 'direction:', Dir)
                                
                                # print('grind', self.grindpoints)
                                # print( 'pos',Pos, 'dir',Dir)
                                #  #closest point
                                # closest = min(self.grindpoints, key=lambda pt: LVector3f(abs((Pos - pt).x),abs((Pos - pt).y),abs((Pos - pt).z)))
                                # for x in range(len(self.grindpoints)):
                                #         if closest == self.grindpoints[x]:
                                #                 self.character.grinddirection = Pos - self.grindpoints[x]
                                #                 # GP = x
                                #                 print('closest point:',x,'direction:', Dir)
                               
                               
                               
                                # closest = min(self.grindpoints, key=lambda pt:abs((Pos - pt).x))
                                
                                # if closest in self.grindpoints[1] - self.grindpoints[0]:
                                        
                                #         print(closest, 'direction', Dir)
                            

                                                # vec = self.grindpoints[x + 1] - self.grindpoints[x]
                                                # print(vec)

                                        ###need to get relative positions of grindpoints to character

                #                 self.character.movementState = 'grinding'
                #                 self.character.grinddirection = self.grindpoints[1] - self.grindpoints[0]
                #                 vec =  self.grindpoints[1] - self.grindpoints[0] # 
                        
                #                 currentPos = self.character.movementParent.getPos()
                # for node in self.railcheck1.node().getOverlappingNodes():
                #         if 'Character' in str(node):
                #                 self.character.movementState = 'grinding'
                #                 self.character.grinddirection = self.grindpoints[2] - self.grindpoints[1]
                #                 currentPos = self.character.movementParent.getPos()
                # for node in self.railcheck2.node().getOverlappingNodes():
                #         if 'Character' in str(node):
                #                 self.character.movementState = 'grinding'
                #                 self.character.grinddirection  = self.grindpoints[3] - self.grindpoints[2]
                #                 currentPos = self.character.movementParent.getPos() 
                # for node in self.railcheck3.node().getOverlappingNodes():
                #         if 'Character' in str(node):
                #                 self.character.movementState = 'grinding'
                #                 self.character.grinddirection  = self.grindpoints[4] - self.grindpoints[3]
                #                 currentPos = self.character.movementParent.getPos()    
                # for node in self.railcheck4.node().getOverlappingNodes():
                #         if 'Character' in str(node):
                #                 self.character.movementState = 'grinding'
                #                 self.character.grinddirection  = self.grindpoints[5] - self.grindpoints[4]
                #                 currentPos = self.character.movementParent.getPos()

                                # self.character.movementState = 'exitgrind'
                              

                                # for i in self.grindpoints:
                                # ###find next grind point and get vector of next grindpoint - current position
                                #         distance = self.grindpoints[i] - currentPos
                                #         print('distance', distance)
                # print(vec) Need to convert to relative to worrld
                
                # self.character.grinddirection = vec
                # print('grinddirection',self.character.grinddirection, 'directrion', self.character.direction)
                # print(self.character.direction)
                # return task.cont
        
        # def checkOverlap(self,task):
        #         railcheck = self.railcheck.node()
        #         for node in self.railcheck.getOverlappingNodes():
        #                 print (node, "on grindrail")
        
        def jumppad(self):
                self.character.startJump(50)
                self.character.movementPoints =0  
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

        def make_ghost_from_model(self, input_model, node_number, world, target_pos):
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
                return (tri_shape)

                # body = BulletGhostNode('input_model_tri_mesh')
                # np = render.attach_new_node(body)
                # np.node().add_shape(tri_shape)
                # np.node().set_friction(0.01)
                # np.set_pos(target_pos)
                # np.set_scale(1)
                # # np.set_h(180)
                # # np.set_p(180)
                # # np.set_r(180)
                # np.set_collide_mask(BitMask32.allOn())
                # world.attachGhost(np.node())
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
                #     dict(name = 'slope', size = Vec3(20, stepsY+Y*2.0, X), pos = Point3(-Y*2.0, 0, 0), hpr = Vec3(0, 0, 30)),
                # ]

                # for i in range(10):
                #     s = Vec3(0.4, stepsY, 0.2)
                #     p = Point3(Y*2.0 + i * s.x * 2.0, 0, s.z + i * s.z * 2.0)
                #     data = dict(name = 'Yall', size = s, pos = p, hpr = Vec3())
                #     shapesData.append(data)

                # for data in shapesData:
                #     shape = BulletBoxShape(data['size'])

                #     np = self.NP.attachNewNode(BulletRigidBodyNode(data['name']))
                #     np.node().addShape(shape)
                #     np.setPos(data['pos'])
                #     np.setHpr(data['hpr'])
                #     np.setCollideMask(BitMask32.allOn())

                #     self.world.attachRigidBody(np.node())

                # shape = BulletSphereShape(0.5)
                # np = self.NP.attachNewNode(BulletRigidBodyNode('Ball'))
                # np.node().addShape(shape)
                # np.node().setMass(10.0)
                # np.setPos(13.0, 0, 5.0)
                # np.setCollideMask(BitMask32.allOn())
                # self.world.attachRigidBody(np.node())

                # shape = BulletBoxShape(Vec3(0.5))
                # np = self.NP.attachNewNode(BulletRigidBodyNode('Crate'))
                # np.node().addShape(shape)
                # np.node().setMass(10.0)
                # np.setPos(-13.0, 0, 10.0)
                # np.setCollideMask(BitMask32.allOn())
                # self.world.attachRigidBody(np.node())
        # def enemySetup(self): #enemy):
        #         """sets up enemies, defaults to inactive. spawn enemy to add them to arena"""
        #         # def enemySetup(self, actor, startpos, ):
        #         # dummy = Actor('../models/atkdummy/atkdummy.bam',{
        #         #                   'slash' : '../models/atkdummy/atkdummy_slash.bam',
        #         #                   'idle' : '../models/atkdummy/atkdummy_idle.bam',
        #         #                   'SMASH' : '../models/atkdummy/atkdummy_SMASH.bam',
        #         #                     })
        #         enemyM = Actor('../models/atkdummy/enemy.bam',{
        #                           'slash' : '../models/atkdummy/enemy_slash.bam',
        #                           'idle' : '../models/atkdummy/enemy_idle.002.bam',
        #                           'deflected' : '../models/atkdummy/enemy_deflected.bam',
        #                           'recoil1' : '../models/atkdummy/enemy_recoil1.bam',
        #                           'bicepbreak' : '../models/atkdummy/enemy_bicepbreak.bam',
        #                           'death' : '../models/atkdummy/enemy_death.bam',
        #                           'run' : '../models/atkdummy/enemy_walk.bam',
        #                             })
        #         enemy2 = Actor('../models/atkdummy/enemy.bam',{
        #                           'slash' : '../models/atkdummy/enemy_slash.bam',
        #                           'idle' : '../models/atkdummy/enemy_idle.002.bam',
        #                           'deflected' : '../models/atkdummy/enemy_deflected.bam',
        #                           'recoil1' : '../models/atkdummy/enemy_recoil1.bam',
        #                           'death' : '../models/atkdummy/enemy_death.bam',
        #                           'run' : '../models/atkdummy/enemy_walk.bam',
        #                             })
        #         enemy3 = Actor('../models/atkdummy/enemy.bam',{
        #                           'slash' : '../models/atkdummy/enemy_slash.bam',
        #                           'idle' : '../models/atkdummy/enemy_idle.002.bam',
        #                           'deflected' : '../models/atkdummy/enemy_deflected.bam',
        #                           'recoil1' : '../models/atkdummy/enemy_recoil1.bam',
        #                           'death' : '../models/atkdummy/enemy_death.bam',
        #                           'run' : '../models/atkdummy/enemy_walk.bam',
        #                             })
        #         self.shader = Shader.load(Shader.SL_GLSL, "../shaders/vert.vert", "../shaders/frag.frag")
        #         # dummy2 = Actor()
        #         # # dummy.instanceTo(dummy2)
        #         self.dummy = Enemy(self.world, 
        #                             self.NP,enemyM, startpos = self.inactiveenemypos[0],
        #                             posture= .01,
        #                             hbshader=self.shader,
        #                             healthbar = HealthBar(pos=(-1, 1, .9, 1.1)),
        #                             name = 'dummy' )
        #         self.dummy2 = Enemy(self.world, self.NP,enemy2, startpos = self.inactiveenemypos[1],
        #                             posture=.01,
        #                             hbshader=self.shader,
        #                             healthbar = HealthBar(pos=(-1, 1, .9, 1.1)),
        #                             name = 'dummy2'  ) 
        #                             # parrypos=loader.loadModel('../models/atkdummy/enemyparrypos.glb'), )
        
        #         self.inactiveEnemies = []
        #         self.enemies = []
        #         self.activeEnemiesPos = {}

        #         # self.dummy.atkhb(self.dummy.model.expose_joint(None, 'modelRoot', 'blade'),
        #         #               CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        #         self.dummy2.attachWeapon(loader.loadModel('../models/sword.glb'),
        #                                  self.dummy2.model.exposeJoint(None, "modelRoot", "swordpos"))
        #         self.dummy.attachWeapon(loader.loadModel('../models/sword.glb'),
        #                                  self.dummy.model.exposeJoint(None, "modelRoot", "swordpos"))
        #         # self.dummy.atkhb(self.dummy2.model.exposeJoint(None, "modelRoot", "swordpos"),
        #         #               CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        #         # self.enemysword()
        #         # self.spawnEnemy(self.dummy2)
        #         self.enemies.append(self.dummy)
        #         self.enemies.append(self.dummy2)
        #         self.activeEnemiesPos.update({self.dummy.NP:self.dummy.NP.getPos()})
        #         self.activeEnemiesPos.update({self.dummy2.NP:self.dummy2.NP.getPos()})
        #         # if self.activeEnemies:
        #         for enemy in self.enemies:
        #                 self.atx.charhitbox(enemy.model, enemy.Hitbox,False, enemy.name)
        #         taskMgr.add(self.updateEnemies, 'update enemies')

class HealthBar(NodePath):
    def __init__(self, pos):
        NodePath.__init__(self, 'healthbar')


        # self.postureBar(pos = (-1,1,0.6, .8))

        self.setShaderAuto()
        cmfg = CardMaker('fg')
        # cmfg.setFrame(-1, 1, -0.1, 0.1)
        cmfg.setFrame(pos)
        self.fg = self.attachNewNode(cmfg.generate())

        cmbg = CardMaker('bg')
        # cmbg.setFrame(-1, 1, -0.1, 0.1)
        cmbg.setFrame(pos)
        self.bg = self.attachNewNode(cmbg.generate())
        self.bg.setPos(1, 0, 0)

        self.fg.setColor(1, 0.5, 0, 1)
        self.bg.setColor(0.5, 0.5, 0.5, 1)

        self.setHealth(1.0)#, full = True)
        # self.setPosture(0.0001)
        # self.set_depth_write(False)
        # self.set_depth_test(False)
        # self.setCompass(base.camera)
#     def postureBar(self, pos):
#         p1 = CardMaker('pos1`')
#         p1.setFrame(pos)
#         self.posture1=self.attachNewNode(p1.generate())
#         self.posture1.setColor(0, 0.5, 1, 1)

#         p2 = CardMaker('pos2`')
#         p2.setFrame(pos)
#         self.posture2=self.attachNewNode(p2.generate())
#         self.posture2.setPos(1, 0, 0)
#         self.posture2.setColor(0.5, 0.5, 0.5, 1)

#         self.posture1.setColor(1, 0.5, 0, 1)
#         self.posture2.setColor(0.5, 0.5, 0.5, 1)

    def PAgauge(self, pos):        
        p1 = CardMaker('pos1`')
        p1.setFrame(pos)
        self.posture1=self.attachNewNode(p1.generate())
        self.posture1.setColor(0, 0.5, 1, 1)

        p2 = CardMaker('pos2`')
        p2.setFrame(pos)
        self.posture2=self.attachNewNode(p2.generate())
        self.posture2.setPos(1, 0, 0)
        self.posture2.setColor(0.5, 0.5, 0.5, 1)

        self.posture1.setColor(1, 0.5, 0, 1)
        self.posture2.setColor(0.5, 0.5, 0.5, 1)

    def setHealth(self, value):#, full = False):
        # if value ==1:
        #         value =.999
        # i
        # f value ==0:
        #         value =.001
        offset = 1.0-value

        self.fg.setScale(value, 1, 1)
        self.bg.setScale(offset, 1, 1)

        
        self.fg.setPos(-offset,0,0)
        self.bg.setPos(1-offset,0,0)
        
        #         self.bg.setScale(1.0 - value, 1, 1)
#     def setPosture(self, value, posturecount = 3):
#         ## Should be divided into enemy's posture count
#         # if value ==1:
#         #         value =.999
#         # if value ==0:
#         #         value =.001
#         # offset = 1.0-value
#         offset = (posturecount - value) / posturecount

#         self.posture1.setScale(value, 1, 1)
#         self.posture2.setScale(1.0-value, 1, 1)

#         self.posture1.setPos(-offset,0,0)
#         self.posture2.setPos(1-offset,0,0)















