import pygame

def doGameLoopAndRender(scene, surface, clock, keys_pressed):
    for gameobj in scene.sprites():
        gameobj.doPhysics()
        gameobj.updateAnimation(clock.get_time())
        if (gameobj.key_press_responses != None):
            gameobj.processKeys(keys_pressed)
        #gameobj.updateRect()
        gameobj.updatePosition()
        
    scene.draw(surface)

class TCGameObject(pygame.sprite.Sprite):
        
    def __init__(self, name, image_home, animation_config, key_press_responses, position=(0,0), padding=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        
        ######## START INSTANCE VARIABLES
        self.parent = None
        self.slowParentDelay = 0
        self.slowParentAccum = [0,0]
        
        self.x_delta = position[0]
        self.y_delta = position[1]
        
        self.jump = 0
        self.ground_level = 650
        self.canJump = False
            
        self.timeSinceLastFrame = 0
        self.currentFrame = 0
        self.reverse_animation = False
        self.physics = True
        self.mass = 2
        self.name = name
        self.padding = padding
        
        self.animations = {}
        self.animation_activators = {}
        ##############
        
        #generate sprite list
        for animation_name in animation_config:
            animation_images = animation_config[animation_name]
            self.animations[animation_name] = []
            self.animation_activators[animation_name] = []
            for image in animation_images:
                self.animations[animation_name].append(pygame.image.load(image_home + image))
        
        #TODO: animation list
        FPS = 15.0
        self.milliseconds_per_sprite = 1000.0/FPS
        #hack to force first frame
        self.image = None
        self.updateAnimation(self.milliseconds_per_sprite)
        
        #fallback if no animations of image is set
        if (len(self.animations) == 0 or self.image == None):
            self.image = pygame.Surface([100, 100])
            self.image.fill((255,0,0))
        
        self.key_press_responses = key_press_responses
                    
    #Add this draw function so we can draw individual sprites
    def updatePosition(self):
        newPosition = [self.x_delta, self.y_delta]
        if (self.parent != None):
            if (self.slowParentDelay != 0):
                slowParentFactor = float(self.slowParentDelay)/100.0
                
                xDiffSigned = float(self.slowParentAccum[0] - self.parent.x_delta)
                yDiffSigned = float(self.slowParentAccum[1] - self.parent.y_delta)
                
                slowParentIncrement = [slowParentFactor*xDiffSigned, slowParentFactor*yDiffSigned]
                
                if (abs(xDiffSigned) >= abs(slowParentIncrement[0])):
                    self.slowParentAccum[0] -= slowParentIncrement[0]
                
                if (abs(yDiffSigned) >= abs(slowParentIncrement[1])):
                    self.slowParentAccum[1] -= slowParentIncrement[1]
                
                newPosition[0] += self.slowParentAccum[0]
                newPosition[1] += self.slowParentAccum[1]
            else:
                newPosition[0] += self.parent.x_delta
                newPosition[1] += self.parent.y_delta
        self.rect = self.rect.move(newPosition[0], newPosition[1])
        
            
    def updateAnimation(self, timePassedLastFrame):
        active_animation_name = None
        
        for animation_name in self.animations:
            if animation_name in self.animation_activators and len(self.animation_activators[animation_name]) > 0:
                active_animation_name = animation_name
            
        if (active_animation_name == None):
            if ("default" in self.animations):
                active_animation_name = "default"
            else:
                return
            
        images = self.animations[active_animation_name]
        
        if (self.timeSinceLastFrame + timePassedLastFrame >= self.milliseconds_per_sprite):
            self.timeSinceLastFrame = 0
            diff = -1 if self.reverse_animation else 1
            self.currentFrame = (self.currentFrame + diff) if (self.currentFrame < len(images)) else 0
            self.currentFrame = (len(images)-1) if (self.currentFrame == -1) else self.currentFrame
        else:
            self.timeSinceLastFrame = self.timeSinceLastFrame + timePassedLastFrame
        
        #update current frame, image and bounds
        self.currentFrame = self.currentFrame if (self.currentFrame < len(images)) else 0
        self.image = images[self.currentFrame]
        self.updateRect()
        
    def updateRect(self):
        self.rect = self.image.get_rect()
        self.updatePosition()
        
    
    def processKeys(self, keys_pressed):
        for key in keys_pressed:
            if keys_pressed[key]:
                #positive
                if key in self.key_press_responses:
                    deltaList = self.key_press_responses[key]
                    for delta in deltaList:
                        if delta[0] == 'x':
                            self.x_delta += delta[1]
                        elif delta[0] == 'y':
                            self.y_delta += delta[1]
                        elif delta[0] == 'frames-to-jump':
                            if self.jump == 0 and self.canJump:
                                self.jump = delta[1]
                                self.canJump = False
                        elif delta[0] in self.animations:
                            activator = str(key)
                            anim = delta[0]
                            target = delta[1]
                            if target:
                                if not activator in self.animation_activators[anim]:
                                    self.animation_activators[anim].append(activator)
                            else:
                                #target is false, activator is present
                                if activator in self.animation_activators[anim]:
                                    self.animation_activators[anim].remove(activator)
            else:
                #negative
                if key in self.key_press_responses:
                    deltaList = self.key_press_responses[key]
                    for delta in deltaList:
                        if delta[0] in self.animations:
                            activator = str(key)
                            anim = delta[0]
                            target = not delta[1]
                            if target:
                                if not activator in self.animation_activators[anim]:
                                    self.animation_activators[anim].append(activator)
                            else:
                                #target is false, activator is present
                                if activator in self.animation_activators[anim]:
                                    self.animation_activators[anim].remove(activator)

    def isOnGround(self):
        return self.distToGround() <= 0
        
    def distToGround(self):
        pos = self.rect.midbottom[1] - (self.rect.height/2) + (self.padding[1])
        return self.ground_level - pos
        
    def doPhysics(self):
        #TODO: generate collision force list
        
        onGround = self.isOnGround()
        
        #only allow jumping again on frame after force is depleted
        if (self.jump == 0 and onGround):
            self.canJump = True
        
        if not self.physics:
            return
        GRAVITY = 5
        
        if (self.jump > 0):
            self.jump -= 1
            self.y_delta += -5 if (self.jump < 5) else -10
        elif (not onGround):
            to_ground = self.distToGround()
            self.y_delta += (GRAVITY * self.mass) if (to_ground >= GRAVITY*self.mass) else to_ground