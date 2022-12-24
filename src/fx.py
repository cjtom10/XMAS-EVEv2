from panda3d.core import *
class Fx():
        def __init__(self):
                """pre loads fx geometries"""
                #kick1 motiuontrail:
           
                self.footstep = loader.loadSfx('../sounds/footstep.wav')
                self.hitsfx =  loader.loadSfx('../sounds/hit.wav')
                self.slash1sfx = loader.loadSfx('../sounds/slash.wav')
                self.slash2sfx = loader.loadSfx('../sounds/slash1.wav')
                self.preKicksfx = loader.loadSfx('../sounds/prekick.wav')
                self.deflectsfx = loader.loadSfx('../sounds/deflect1.wav')

        
                self.ts0 = TextureStage('texstage0')
                self.ts0.setTexcoordName("0")
                self.ts0.setMode(TextureStage.MReplace)
                trailmat = Material("material")
                trailmat.setEmission((1,1,1,1))
                trailmat.setSpecular((1,1,1,0))
                
                self.ts0.setSort(0)
                uvtex = loader.loadTexture('../models/tex/testuv.png')
                tex = loader.loadTexture('../models/tex/transgradiet.png')
                ptex = loader.loadTexture('../models/tex/bb.png')
                brushtex = loader.loadTexture('../models/tex/watercolorstrike.png')
                self.slash1trail = loader.loadModel('../models/newslashtrail.glb')
                

                # self.slashfx = loader.loadModel('../models/slashfx.glb')
                self.slashfx = loader.loadModel('../models/slashfx.glb')
                self.slashfx.setMaterial(trailmat)
                self.slashfx.clearTexture()
                self.slashfx.setTransparency(True)
                self.slashfx.setTexture(self.ts0, brushtex,1)
                self.slashfx.setShader(self.shader)    

                self.slash1trail.setMaterial(trailmat)
                self.slash1trail.clearTexture()
                self.slash1trail.setTransparency(True)
                self.slash1trail.setTexture(self.ts0, brushtex,1)
                self.slash1trail.setShader(self.shader)
                # self.slash1trail.setH(180)
                # self.slash1trail.replaceTexture(oldtex, tex)
                # self.slash1trail.setDepthWrite(False)
                # print(self.slash1trail.findAllTextures())
                # self.slash1trail.ls()

                self.slash2trail = loader.loadModel('../models/slashkick2trail.glb')
                self.slash2trail.setMaterial(trailmat)
                self.slash2trail.setShader(self.shader)
                # self.slash2trail.reparentTo(self.worldNP)
                # self.slashtrail2.setPos(0, -115, -10)
                self.slash2trail.setTransparency(True)
                self.slash2trail.setTexture(self.ts0, brushtex,1)
                # self.slash2trail.setH(180)

                self.slash3trail = loader.loadModel('../models/slashkick3trail.glb')
                self.slash3trail.setMaterial(trailmat)
                self.slash3trail.setTransparency(True)
                self.slash3trail.setTexture(self.ts0, tex,1)
                self.slash3trail.setShader(self.shader)

                self.dodgeframes = self.charM.getNumFrames('dodge')
                self.dodgeposeground = loader.loadModel('../models/dodgepose.glb')
                self.dodgeposeground.setShader(self.shader)
                self.dodgeposeground.setTransparency(True)
                self.dodgeposeground.setH(180)
                self.dodgeposeair= loader.loadModel('../models/dodgeposeair.glb')
                self.dodgetrail = []
                self.dodgetraileffect = False#if the copied nodes are visible        
                self.dodgetrailair = []

                # coral = loader.loadModel('../models/coral.glb')
                # coral.reparentTo(self.worldNP)
                # coral.setPos(0,-115,0)
     
                for i in range(self.dodgeframes ): #self.dodgetrail[i] == None:
                    self.dodgetrail.append(NodePath(f"dtrail{i}"))
                    self.dodgeposeground.instanceTo(self.dodgetrail[i])

                # self.crosshair = loader.loadModel('../models/crosshair.glb')
                self.crosshair = loader.loadModel('../models/lockonicon.glb')
                self.crosshair.set_depth_write(False)
                self.crosshair.set_depth_test(False)
                self.crosshair.setCompass(base.camera)        
