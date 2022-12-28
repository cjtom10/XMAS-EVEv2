from re import A, S
from panda3d.bullet import *
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.actor.Actor import Actor
from direct.interval.LerpInterval import *
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
import random
import math
from lvl import HealthBar
class Turret():
    def __init__(self, world, parentnode, actor,initpos, pos, name ):
        """turrets track player and shoot at them. wehen player is in range, they swing at them. they spawn one at a time"""
        
        self.pos = pos
        self.model = actor
        self.name = name
        self.worldNP = parentnode
        self.initpos = initpos
        # self.model.setPos(0,0,-50)

        self.lookTarget = Vec3(0,0,0)

        self.capsule = BulletCapsuleShape(2,3)
        self.controller =BulletCharacterControllerNode(self.capsule,0.4, name)
                
        self.NP =parentnode.attachNewNode(self.controller)
        self.NP.setCollideMask(BitMask32.bit(1))
        self.NP.setPos(initpos)
        world.attachCharacter(self.controller)


        self.anim = self.model.getCurrentAnim()
        self.frame = self.model.getCurrentFrame()

        self.active =False

        self.health = .99

        # self.healthbar = HealthBar(pos=(-1, 1, .9, 1.1))
        # # self.healthbar.postureBar(pos = (-1,1,0.6, .8))
        # self.healthbar.setCompass(base.camera)
        # self.healthbar.reparentTo(self.NP)
        # self.healthbar.setZ(5)
        
        
        self.isSpawning = False
        self.isDying = False
        self.isHit = False
        self.hasHit = False
        self.isStunned = False

        self.hbSetup()

        #bullets shoot in linear lines away from emitter - emitter moves around
        #bullets continue moving until they hit something
        # max 10 bullets
        self.bullets = []
        # self.bulletHBs = []
       
        self.orb = loader.loadModel('../models/enemies/orb.glb')
        self.emitter = self.model.attachNewNode('bullet emitter')
        self.emitter2 = self.model.attachNewNode('bullet emitter2')
        self.emitter.setZ(1)
        self.orb = loader.loadModel('../models/enemies/orb.glb')
        self.orb.reparentTo(self.emitter)
        # print('bullets',self.bullets)
        self.bulletsetup(20)

        self.atkseq = None
        self.isAttacking=False
        self.attached = False
        self.atkNodeL = NodePath(CollisionNode(f'{self.name}attackL'))
        self.atkNodeR = NodePath(CollisionNode(f'{self.name}attackR'))
        self.forearmR = self.model.exposeJoint(None, 'modelRoot', 'forearm.R')
        self.forearmL = self.model.exposeJoint(None, 'modelRoot', 'forearm.L')
    def tracktarget(self):
        a = self.model.getX(render) - self.lookTarget.x
        b = self.model.getY(render) - self.lookTarget.y

        h = math.atan2(a,-b)
        angle = math.degrees(h) 

        # self.closest = closest
        self.model.setH(render, angle)     
    def hbSetup(self):
        #hb for TAKING DAMAGE
        capsule = CollisionCapsule((0,0,-1),(0,0,2),2)

        self.HB = self.NP.attachNewNode(CollisionNode(f'{self.name}hb'))
        self.HB.node().addSolid(capsule)

        # self.HB.show()


    def bulletsetup(self, number ):
       

        for x in range (number):
            bullet = Bullet(self.emitter, self.worldNP,f'bullet{x}', self.orb,False, .5,20, self.emitter.getPos(render))

            self.bullets.append(bullet)
            print('setup pos',bullet.NP.getPos())

        print('bullets,', self.bullets)


    def bulletPatterns(self, t, pattern):
        if pattern == 1:
            self.emitter.setX(math.sin(t*2)* 2)
        if pattern == 2:
            self.emitter.setZ(math.sin(t*2)* 2)
        if pattern == 3:
            self.emitter.setX(math.sin(t*3))
            self.emitter.setZ(math.cos(t*5))
       
        p = self.emitter.getPos()
        

    def fire(self):
        "goes thru self.bullets and shoots them"
        for bullet in self.bullets:
            # while bullet.active == True:
            #     continue
            if bullet.active == True:
                # print(bullet.name, 'is active')
                continue
            else:      
                bullet.shoot()
                # print('firing', bullet.name)
                return
    def spawnSeq(self):
        self.NP.setPos(self.pos)
        self.active = True
        self.model.reparentTo(self.NP)
        self.model.setPos(0,0,-2)

        sp = LerpPosInterval(self.model, 2, (0,0,-2),(0,0,-10))
        def spawnin():
            self.isSpawning = True
        def spawnout():
            self.isSpawning = False
        s=Func(spawnin)
        e=Func(spawnout)
        spawn = Sequence(s,sp,e).start()
    def dieSeq(self):
        self.isDying = True
        sp = LerpPosInterval(self.model, 2, (0,0,-10),(0,0,-2))
        def tp():
            self.NP.setPos((self.initpos))
        setpos = Func(tp)
        def finish_dying():
            self.isDying = False
            self.active = False
        e = Func(finish_dying)

        die = Sequence(sp,setpos,e).start()

    def meleeatk(self):
        # print('atack')
        self.isAttacking = True
        
        def clear(node):
            node.node().clearSolids()
            # self.attached = False
        def end():
            self.isAttacking = False
            self.hasHit=False

        rightarm = Func(self.atkhb, self.forearmR, CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3), self.atkNodeR)
        leftarm = Func(self.atkhb, self.forearmL, CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3),self.atkNodeL)
        a1 = self.model.actorInterval('atk1')
        a2 = self.model.actorInterval('atk2')
        clearL = Func(clear, self.atkNodeL)
        clearR = Func(clear, self.atkNodeR)
        send = Func(end)


        self.atkseq = Sequence(Parallel(leftarm, a1),clearL,Parallel(rightarm, a2), clearR,send)
        self.atkseq.start()

    def atkhb(self,parent,shape,node ):
        # if self.attached == True:
        #     return
        # self.blade = self.model.expose_joint(None, 'modelRoot', 'blade')
        # self.attached=True
        # self.atkNode = NodePath(CollisionNode(f'{self.name}attack'))
        # HitB = CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3)
        node.reparentTo(parent)
        node.node().addSolid(shape)
        node.show()
 
    def staggered(self,side):
        #play anim thru thenm return
        # self.s

        self.isStunned = True
        if self.atkseq.isPlaying():
            self.atkseq.finish()
        
        print('staggere enemy on', side)
        def end():

            self.isStunned = False
        e = Func(end)
        # if self.anim!=f'staggered{side}':
        #     self.model.play(f'staggered{side}')

        anim = self.model.actorInterval(f'staggered{side}',startFrame=0, endFrame = 60)
        staggerseq = Sequence(anim,e).start()
    def update(self, dt, et):
        # print('turret dt', dt)
        # print('turret elapsed time', et)
        
        self.anim = self.model.getCurrentAnim()
        self.frame = self.model.getCurrentFrame()
        
        if self.isStunned == True:
        #     # if self.frame!=None:
        #     #     if self.frame > 55:
        #     #         self.isStunned = False
            return
        if self.isSpawning == True:
            return
        for x in self.bullets:
                if x.active == False:
                    x.NP.setPos(self.emitter.getPos(render))
                    x.NP.setH(self.model.getH(render))                
                if x.active == True:
                    x.processShooting(dt)
        self.d2p = (self.NP.getPos(render) - self.lookTarget).length()
        # print('turret d2p', self.d2p)
        if self.d2p<7:
            if self.isAttacking == False:
                self.meleeatk()
            
        if self.d2p > 10: #shooty shooty
            self.bulletPatterns(et, 1)

            inactive_bullets = []
            active_bullets = []
    
            # if round(et*100) % 60 == 0:
          
            #     self.fire()

            # if self.health <1:
        
            #     self.healthbar.setHealth(self.health)
                # print('all bullets', self.bullets)

            #     inactive_bullets = [b for b, active in self.bullets.items() if not active]
            #     print("INACTIVE", inactive_bullets)
            #     if inactive_bullets:
            #         self.shoot(inactive_bullets[0])
            # print('turretpos', self.NP.getPos(render), 'vulletpos', self.bullets[0].NP.getPos(render), self.bullets[0].active)
            # if self.bullets[0].active == False:
            #     self.bullets[0].shoot()

            # for bullets in [b for b, active in self.bullets.items() if active]:
            #     self.processShooting(bullets, dt) 
                # for bullet in inactive_bullets:
                #     print("INACTIVE BULLET", bullet)
                #     self.shoot(bullet,dt)
            # processaction={
            #                     'idle': self.idleTurret,

            #                     'melee': self.processAttack, 

            #                     'stunned': self.isStunned,


            #     }
        anim = self.model.getCurrentAnim()
        if anim!='idle':
            self.model.loop('idle')

        self.tracktarget()
class Bullet():
    def __init__(self,worldNP, parentNode, name, model, active,radius, speed,initpos ):
        self.worldNP = worldNP
        # self.parentNode = parentNode
        self.inactivePos = initpos
        self.name = name
        self.parentNode = parentNode
        self.speed = speed

        self.NP = parentNode.attachNewNode(name)
        model.instanceTo(self.NP)
        self.active = active
        self.cNP = self.NP.attachNewNode(CollisionNode(f'{name}HB'))
        #cNP.setCollideMask(BitMask32.allOn())
        frommask = BitMask32(0x1)
        intomask = BitMask32(0x2)
        # cNP.setFromCollideMask(BitMask32(0x1))
        # cNP.setIntoCollideMask(BitMask32(0x2))
        self.sphere = CollisionSphere(0,0,0, radius)
        self.HBattached = False   
        
        self.NP.setPos(render, self.inactivePos)
        print('inactive pos', self.inactivePos)
    
    def attachHB(self):
        self.cNP.node().addSolid(self.sphere) 
        self.HBattached = True   
        self.cNP.show()


    def shoot(self):
        # print('oh shoot')
        self.NP.reparentTo(render)
        # self.NP.setH(self.parentNode.getH())
        if self.active ==True:
            # print('bullet already active')
            return
        self.active =True
        if self.HBattached == False:
            self.attachHB()

    def processShooting(self, t):
        # forward = v
        self.NP.setY(self.NP, t * self.speed)
        # self.NP.setY(t * forward.y)
        # print(self.NP.getPos(render), self.parentNode.getPos(render))
        # print('shooting', self.name, self.NP.getPos(), self.NP.getPos(render))
        return
    def hit(self):
        """bullet explodes and resets"""
        
        self.cNP.node().clearSolids()
        # print('clear solid')

        self.HBattached = False

        self.NP.reparentTo(self.parentNode)
        self.NP.setPos(self.parentNode, (0,0,0))
        
        print('hit - reset', self.NP.getPos(render), self.inactivePos)
        self.active = False
        # return
class Enemy():
    def __init__(self, world, parentnode, actor, startpos,posture,
                hbshader,spawnpoint,initState, type, name ):
        self.active = False
        self.health = .01
        self.chargeAMT = 0.98
        self.posture = posture
        self.world = world
        self.parentnode = parentnode
        self.name = name
        self.spawnPoint = spawnpoint
        
        self.type = type

        self.isAttacking =False
        self.deflected = False
        self.model = actor
        self.capsule = BulletCapsuleShape(1,2)
        self.controller =BulletCharacterControllerNode(self.capsule,0.4, name)
        self.speed = 0
        

        self.NP =parentnode.attachNewNode(self.controller)
        self.NP.setCollideMask(BitMask32.bit(1))
        self.world.attachCharacter(self.controller)

        self.model.reparentTo(self.NP)
        self.model.setZ(-2)

        self.d2p = int
        # self.parrypos = parrypos.find('enemyparrypos')
        # self.parrypos.setCompass(self.NP)
        # self.anim = self.model.getCurrentAnim()
        # self.frame =self.model.getCurrentFrame()
        self.solidsCleared = False
        self.isHit = False
        self.hasHit=False
        self.startpos = startpos
        self.NP.setPos(self.startpos)

        self.lookTarget = Point3(0,0,0)### target to lookat player
        self.moveTarget = Point3(0,0,0)### move to here
        
        self.trackPlayer = True

        self.atkNode = NodePath(CollisionNode(f'{self.name}attack'))
        self.atkorder = 0
        self.atx = {0:'slash',1:'slash2'}#diff atacks stored here

        self.seq = None

        self.inRange = False

        self.finishMe = False

        self.isPaused = False

        self.grappleStruck = False
        self.pausePos = (0,0,0)
        # self.pdodgecheck = NodePath(BulletRigidBodynode(f'{self.name}pdodge'))
        # self.pdodgecheck.node().setKinematic(True)
        # self.pdodgecheck.node().addShape)

        # self.world.attachRigidBody(self.pdodgecheck.node())
        self.currentBehavior =  initState

        self.attached=False
        ###TODO Attach hb to joint instead of being arbitratry
        self.Hitbox=[]

        # self.currentBehavior = None
        self.behaviors = {1:'run',
                          2: 'idle',
                          3:'attack',4:'attack',5:'attack'}
#######healthbar
        self.healthbar = HealthBar(pos=(-1, 1, .9, 1.1))
        # self.healthbar.postureBar(pos = (-1,1,0.6, .8))
        self.healthbar.setCompass(base.camera)
        self.healthbar.reparentTo(self.NP)
        self.healthbar.setZ(3)
        self.healthpos = self.NP.attachNewNode('healthbarpos')
        # self.healthpos.setZ(3)


        # self.hb(name)
        # self.hbSetup()
    def hbSetup(self):
        # pass
        #placeholder - need to attach hbs to bones
        chestHB= CollisionCapsule(0, .5, 4, 0, 0, 0, .5)
        self.HB = self.NP.attachNewNode(CollisionNode(f'{self.name}hb'))
        self.HB.node().addSolid(chestHB)
        self.HB.setY(-.2)
        self.HB.show()
    # def resetPosture(self):


    def updateBasic(self):#, task):
        # print('posture', self.posture,'attackiing?', self.isAttacking)
        # if self.active == False:
        #     return\
        # print('my pisture', self.name, self.posture, 'hashiu', self.hasHit)
        #finisher check
        # self.healthbar.setPos(self.NP.getPos())
        if self.isPaused==True:
            self.NP.setPos(self.pausePos)
            # self.controller.setLinearMovement(0, False)
            return
        if self.grappleStruck == True and self.controller.isOnGround():
            self.land()
        
        if self.posture<=0: #and self.inRange == True:
            # self.finishMe = True
            self.currentBehavior = 'stunned'
            return

        if self.currentBehavior==None:
            self.randomizebehavior()
        self.anim = self.model.getCurrentAnim()
        self.frame =self.model.getCurrentFrame()

        self.d2p = (self.NP.getPos()-self.moveTarget).length()
        if self.d2p <3: 
            self.inRange = True
        if self.d2p >3:
            self.inRange = False # block out runnoing if iun range

        #

        self.d2p = (self.NP.getPos(render) - self.moveTarget).length()
        if self.trackPlayer==True:
            # self.NP.lookAt(self.lookTarget)
            self.tracktarget()
    #   ######FIX THIS LATER
        if self.deflected ==True:
            return #task.cont
    ########
        # if self.isAttacking!=True:
        #     self.atkNode.node().clearSolids()
        #     self.attached=False
        
        if self.isAttacking==True and self.frame!=None:
            if self.frame>15:
                self.isAttacking=False
            else:
                return #task.cont
 
        processaction={
                            'idle': self.idle,
                            'run': self.processRun,
                            'attack': self.processAttack, 
                            'deflected': self.processDeflect,
                            'stunned': self.isStunned,
                            'charging': self.processCharge,
                          
            }
        if self.active ==True and self.currentBehavior!=None:
            processaction[self.currentBehavior]()
########healthbar update
        # self.healthbar.setPosture(self.posture)
        if self.health <1:
        
            self.healthbar.setHealth(self.health)
        
        # if self.posture>.01:
        #     self.resetPosture()
        self.controller.setLinearMovement(self.speed, False)
        return #task.cont
    def pause(self, pos):
        """pauses enemy in place , sets it at pos, use for when its getting grappled
        """
        self.isPaused=True
        self.pausePos=pos

    def land(self):
        """landing after gettingh launched"""
        self.speed = 0
        #play anim to completion then get up and randomize behaviopr
        self.grappleStruck = False
    def randomizebehavior(self):#, task):
        """2 behaivors, when not in attack range and when in attacl range"""
        # print('randopmzia', self.d2p)
        self.d2p= (self.NP.getPos() - self.lookTarget).length()
        # if self.d2p>3:
        if self.inRange == False:
            num = random.randint(1,2)
        if self.inRange ==True:
            num = random.randint(2,5)
        #     print('1 to 2')
        # elif self.d2p<3:
        #     num = random.randint(2,5)
        #     print('2 to 5')
        self.currentBehavior = self.behaviors.get(num)
        # return task.again

        
    def resetPosture(self):
        #change this to descreete values
        self.posture = 2
        # self.posture -=.001
        # if self.posture > 1:
        #     self.posture = 0.999
        #     print('stun!')

    # def die(self):
    #     print('dead')
    #     # self.world.removeRigidBody(self.capsule.node())
    #     self.NP.detachNode()
        # taskMgr.remove(self.update)
        #includes model, hb, character controller node, update task
    def atkhb(self,parent,shape ):

        # self.blade = self.model.expose_joint(None, 'modelRoot', 'blade')
        self.attached=True
        # self.atkNode = NodePath(CollisionNode(f'{self.name}attack'))
        # HitB = CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3)
        self.atkNode.reparentTo(parent)
        self.atkNode.node().addSolid(shape)
        self.atkNode.show()
        
    def processAttack(self):
        self.speed = 0
        # print('qattacking state', self.d2p)
        if  self.d2p <10 and self.d2p > 5:
            print('strafe')
            self.speed = render.getRelativeVector(self.model, (5,0,0))
            return

        if self.isAttacking ==True:
            return
        else:
            self.doAttack(anim=self.atx[self.atkorder])
    

    def doAttack(self,anim='slash', limit = 2):#, limit=2):#, task):
        """limit is the max a mount of combos"""
        self.atkorder+=1
        self.isAttacking=True
        # if (self.anim!='slash'):
        #     self.model.play('slash')
        # if self.attached==False:
        def attach():
            if self.attached==False:
                self.atkhb(self.model.exposeJoint(None, "modelRoot", "swordpos"),
                   CollisionCapsule((0, 0, 0), (0, 2.5, 0), .3))
        def detach():
                self.atkNode.node().clearSolids()
                self.attached=False
        def endatk():
            self.isAttacking=False
            self.hasHit = False
            
            
            if self.atkorder>=limit:# wensures that each attack is 2 attacks
                self.atkorder=0
                self.resetPosture()
                # self.currentBehavior = None

        atta = Func(attach)
        HBend=Func(detach)
        end =Func(endatk)
        s1 = self.model.actorInterval(anim,loop = 0, startFrame=0, endFrame = 6)
        s2 = self.model.actorInterval(anim,loop = 0, startFrame=7, endFrame = 18)
        s3 = self.model.actorInterval(anim,loop = 0, startFrame=19, endFrame = 25)
        
        #if self.atkorder==0:#first attack
        if self.seq!=None:
            if self.seq.isPlaying():
                self.seq.pause()
        self.seq = Sequence(s1, Parallel(s2, atta),Parallel(s3,HBend), end)

        self.seq.start()
        # return task.again
    def processDeflect(self):
        #anim should only playy for stuyn state
        # if self.seq.isPlaying():
        #         self.seq.pause()
        # self.posture+=.3
        p = Func(self.seq.pause)#### add vfx here later
        r = Func(self.seq.resume)
        self.isAttacking =False
        self.attached = False
        self.atkNode.node().clearSolids()

        # atkpause = Sequence(p, Wait(.1), r)
        # if atkpause.isPlaying():
        #     return
        # else:
        #     atkpause.start()
        # print(self.frame)
        ##should go into either attack or stuned

    def attachWeapon(self,weapon, parent):
        weapon.reparentTo(parent)

    def tracktarget(self):
        a = self.model.getX(render) - self.lookTarget.x
        b = self.model.getY(render) - self.lookTarget.y

        h = math.atan2(a,-b )
        angle = math.degrees(h) 

        # self.closest = closest
        self.model.setH(render, angle)
        #model faces player indpendent of capsule

        # self.NP.lookAt(self.lookTarget)
        # self.Np.setH(render, 0)
        # self.NP.setP(0)

        # dir = self.NP.getQuat().getForward() * 3
        # self.controller.setLinearMovement(dir, False)
        # # print(dis)

        # if dis<3 and self.isAttacking!=True:
        #     self.attack()
    def processGrappleStruck(self):
        """make enemy grappleable, """ 
    def processCharge(self):
        # print(self.name, 'chargingup hhnnnnnngh','hp:',self.health,'charge amt', self.chargeAMT)
        if  (self.anim!='chargeup'):
            self.model.play('chargeup')

        if self.chargeAMT >0:
            self.health +=.01
            self.chargeAMT -=.01
        else:
            print('finish charging')
            self.currentBehavior = None
            self.randomizebehavior
        pass
    def processRun(self):
        self.d2p = (self.NP.getPos(render) - self.moveTarget).length()
        if self.inRange == True:
            self.currentBehavior = None
            return
        if self.d2p>2:
            self.run()
        else:
            self.currentBehavior=None
            # self.controller.setLinearMovement(0, False)
            self.speed = 0
    def run(self):#,  target):
     
        target = self.moveTarget
        # if self.d2p < 2:
        #     x=0
          
        dir = self.NP.getQuat().getForward() * 3
     

   
        # self.d2p = (self.NP.getPos(render) - target).length()
      
        # if self.d2p > 2:
        self.NP.lookAt(target)
        self.speed = dir
          
        # self.controller.setLinearMovement(x, False)

        if  (self.anim!='run'):
            self.model.loop('run')

    def idle(self):
        self.speed=0
        def end():
            self.currentBehavior=None
            print('end idle')
        # print('idle')
        if  (self.anim!='idle'):
            self.model.loop('idle')
        if self.frame == 30:
            self.currentBehavior=None

        # idle=self.model.actorInterval('idle',startFrame=0, endFrame = 30 )
        # fin = Func(end)
        # if self.seq!=None:
        #     if self.seq.isPlaying():
        #         self.seq.pause()
        #     self.seq=Sequence(idle, fin)
        #     self.seq.start()

    def chargeHP(self):
        """when enemies spawn in, they charge up their hp. they each have a different starting threshold before theyh become active"""
        print('charging up')
        # chargeseq = Sequence() 
        pass
    def isStunned(self):
        # print(self.name, 'is stuned!')
        if self.anim!='staggered':
            self.model.play('staggered')
   
        # if self.frame!=None:
        #     if self.frame >=40:
        #         self.randomizebehavior()
        #need to exit out after some tim e
 
        return
