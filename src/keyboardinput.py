from direct.showbase.InputStateGlobal import inputState
class KeyboardInput:
   

    def __init__(self):
        self.accept('escape', self.doExit)
        # self.accept('space', self.doJump)
        # self.accept('shift', self.evade)

        self.accept('c', self.switch2mech)
        self.accept('c-up', self.stopCrouch)

        # self.accept('k', self.dummy.die)

        self.accept('f', self.recenterCam)
        self.accept('f3', self.toggleDebug)
        self.accept('f1', self.wireframe)

        
        self.accept('e', self.actionX)
        
        self.accept('control-up', self.stopFly)
        
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        # inputState.watchWithModifiers('turnLeft', 'q')
        # inputState.watchWithModifiers('turnRight', 'e')
        
        # inputState.watchWithModifiers('run', 'shift')
        # inputState.watchWithModifiers('jump', 'space')

        inputState.watchWithModifiers('flyUp', 'r')
        inputState.watchWithModifiers('flyDown', 'f')

        self.WASD = ['forward',
                     'left',
                     'right',
                     'reverse']
        
