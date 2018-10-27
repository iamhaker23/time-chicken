import pygame
import random
import math

def makeEnemy(type):
    if type == "badger":
        badgerControl = {
            "ALWAYS":[('x-speed', -1.0), ('x-min', -200)]
        }
        badger = Enemy("badger", {"default":['BigBadger_1.png','BigBadger_2.png'], "old":["oldbadger1.png", "oldbadger2.png"]}, badgerControl, (700, 200), (0, 0))
        badger.milliseconds_per_sprite = 100.0
        return badger
    elif type == "psychic-fox":
        foxControl = {
            "ALWAYS":[('x', -1.0), ('x-min-reverse', 400), ('x-max-reverse', 611)]
        }
        fox = Enemy("psychic-fox", {"default":['Fox1.png','Fox2.png','Fox3.png','Fox4.png','Fox5.png','Fox6.png','Fox7.png','Fox8.png','Fox9.png']}, foxControl, (610, 100), (0, 0))
        fox.milliseconds_per_sprite = 200.0
        fox.hp = 100
        fox.spells = ["fox-elemental-spell", "heal-spell"]
        return fox
    elif type == "master-fox":
        foxControl = {
            "ALWAYS":[('x', -1.0), ('x-min-reverse', 400), ('x-max-reverse', 611)]
        }
        fox = Enemy("master-fox", {"default":['Fox1.png','Fox2.png','Fox3.png','Fox4.png','Fox5.png','Fox6.png','Fox7.png','Fox8.png','Fox9.png']}, foxControl, (610, 100), (0, 0))
        fox.milliseconds_per_sprite = 200.0
        fox.hp = 100
        fox.spells = ["fox-elemental-spell", "heal-spell", "fox-wall-spell"]
        return fox
    elif type == "ultimate-fox":
        foxControl = {
            "ALWAYS":[('x', -5.0), ('x-min-stop', 450)]
        }
        fox = Enemy("ultimate-fox", {"default":['UltimateBossA.png','UltimateBossB.png'],"cast":['UltimateBoss1.png','UltimateBoss2.png','UltimateBoss3.png','UltimateBoss4.png','UltimateBoss5.png','UltimateBoss6.png','UltimateBoss7.png','UltimateBoss8.png']}, foxControl, (610, 100), (0, 0))
        fox.milliseconds_per_sprite = 400.0
        fox.hp = 120
        fox.attack_cooldown = 2000
        fox.hp = 10
        fox.spells = ["fox-elemental-spell", "heal-spell", "fox-wall-spell"]
        return fox
    return None
    
def makeEffect(type, parent):
    if type == "heal-spell":
        effect = Effect("heal-spell", {"default":['spell1.png']}, parent=parent)
        return effect
    elif type == "shoot-spell":
        effect = Effect("shoot-spell", {"default":['spell2.png']}, {"ALWAYS":[('x',10)]}, position=(parent.x_delta, parent.y_delta))
        effect.life = 1000
        return effect
    elif type == "fox-elemental-spell":
        offset = 50 if parent.name != "ultimate-fox" else 100
        effect = Effect("fox-elemental-spell", {"default":["attack-" + Enemy.boss_elements[Enemy.boss_element]+".png"]}, {"ALWAYS":[('x',-5 + random.uniform(-5, 2) ), ('y',3 + + random.uniform(-1, 2) )]}, position=(parent.x_delta-offset, parent.y_delta+offset))
        effect.life = 2000
        return effect
    elif type == "fox-wall-spell":
        element = Enemy.boss_elements[Enemy.boss_element] if parent.name != "ultimate-fox" else Enemy.boss_elements[random.randint(0, len(Enemy.boss_elements)-1)]
        effect = Effect("fox-wall-spell", {"default":["wall-" + element +".png"]}, {"ALWAYS":[('x',-5 + random.uniform(-5, 2) ), ('x-min', -50)]}, position=(parent.x_delta-(10*random.uniform(0, 9)), parent.y_delta+100))
        effect.life = 4000
        return effect
    elif type == "hit-spell":
        effect = Effect("hit-spell", {"default":['spell3.png']}, {"ALWAYS":[('x',3)]}, position=(parent.x_delta, parent.y_delta))
        effect.life = 500
        return effect
    elif type == "demon-spell":
        effect = Effect("demon-spell", {"default":['attack-fire.png']}, position=(parent.x_delta, parent.y_delta))
        effect.life = 500
        return effect
    elif type == "hit-marker":
        effect = Effect("hit-marker", {"default":['hit.png']}, position=(parent.x_delta, parent.y_delta), padding=(50, 60))
        effect.life = 50
        return effect
    return None
   
class TCGameObject(pygame.sprite.Sprite):


    scene_groups = None
    image_home = ""
    
        
    def update(self, keys_pressed=None, clock=None):
        
        if self.name == "chicken" and self.dead:
            Enemy.disable_scrolling = True
            if self.time_since_dead == 0:
                self.setAnimationState('dead', True, override=True)
            else:
                if self.image_name == "chicken_death_5.png":
                    self.game_reset_flag = True
            self.time_since_dead += clock.get_time()
            self.doPhysics()
            if clock != None:
                self.updateAnimation(clock.get_time())
            self.updatePosition()
        else:
            self.doPhysics()
            if clock != None:
                self.updateAnimation(clock.get_time())
            if (self.key_press_responses != None):
                if keys_pressed != None:
                    self.processKeys(keys_pressed)
            self.updatePosition()
        
    def __init__(self, name, animation_config=None, key_press_responses=None, position=(0,0), padding=(0,0), parent=None):
        pygame.sprite.Sprite.__init__(self)
        
        ######## START INSTANCE VARIABLES
        self.dead = False
        self.time_since_dead = 0
        self.game_reset_flag = False
        
        self.type="DEFAULT"
        self.parent = parent
        self.slowParentDelay = 0
        self.slowParentAccum = [0,0]
        self.slowParentInit = False
        
        self.x_delta = position[0]
        self.y_delta = position[1]
        
        self.jump = 0
        self.ground_level = 650
        self.canJump = False
            
        self.timeSinceLastFrame = 0
        self.currentFrame = 0
        self.reverse_animation = False
        self.physics = False
        self.mass = 2
        self.name = name
        self.padding = padding
        
        self.animations = {}
        self.animations_image_names = {}
        self.animation_activators = {}
        ##############
        
        #generate sprite list
        self.setAnimations(animation_config)
        
        fps = 15.0
        self.milliseconds_per_sprite = 1000.0/fps
        #hack to force first frame
        self.image = None
        self.image_name = ""
        self.updateAnimation(self.milliseconds_per_sprite)
        
        #fallback if no animations of image is set
        if (len(self.animations) == 0 or self.image == None):
            self.image = pygame.Surface([100, 100])
            self.image.fill((255,0,0))
        
        self.key_press_responses = key_press_responses
                    
    def setAnimations(self, conf, update=False):
        for animation_name in conf:
            animation_images = conf[animation_name]
            
            self.animations[animation_name] = []
            self.animations_image_names[animation_name] = []
            
            self.animation_activators[animation_name] = {"activators": [], "stop-on-last-frame": False, "reset-speed": 0}
            for image in animation_images:
                self.animations[animation_name].append(pygame.image.load(TCGameObject.image_home + image))
                self.animations_image_names[animation_name].append(image)
        if (update):
            self.updateAnimation(self.milliseconds_per_sprite)
                    
    def setAnimationState(self, anim_name, activate, activator="", override=False, play_stop=False, reset_speed=0):
        
        if override and activate:
            #deactivate all others
            self.currentFrame = 0
            for key in list(self.animation_activators.keys()):
                self.animation_activators[key]["activators"] = []
    
        if activate:
            if not anim_name in self.animation_activators.keys():
                self.animation_activators[anim_name]["activators"] = [activator+"SELF"]
            else:
                if not activator+"SELF" in self.animation_activators[anim_name]:
                    self.animation_activators[anim_name]["activators"].append(activator+"SELF")
            
        else:
            if not anim_name in self.animation_activators.keys():
                self.animation_activators[anim_name]["activators"] = []
            else:
                if activator+"SELF" in self.animation_activators[anim_name]:
                    self.animation_activators[anim_name]["activators"].remove(activator+"SELF")
                    
        self.animation_activators[anim_name]["stop-on-last-frame"] = play_stop
        if play_stop and reset_speed != 0:
            self.animation_activators[anim_name]["reset-speed"] = reset_speed
        #self.updateAnimation(self.milliseconds_per_sprite)
            
    #Add this draw function so we can draw individual sprites
    def updatePosition(self):
        
        #newPosition = [self.x_delta + self.padding[0], self.y_delta + self.padding[1]]
        
        newPosition = [self.x_delta, self.y_delta]
                
        if (self.parent != None):
            if (self.slowParentDelay != 0):
                if not self.slowParentInit:
                    self.slowParentInit = True
                    newPosition[0] += self.parent.x_delta
                    newPosition[1] += self.parent.y_delta
                    self.slowParentAccum[0] = newPosition[0]
                    self.slowParentAccum[1] = newPosition[1]
                else:
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
        
        max = 0
        
        #TODO: check here for animation_activators "terminate conditions"
        #If so, remove from list
                
        for animation_name in self.animations:
            if animation_name in self.animation_activators:
                
                on_last_frame = self.animation_activators[animation_name]["stop-on-last-frame"] and self.image_name == self.animations_image_names[animation_name][-1]
                if len(self.animation_activators[animation_name]["activators"]) > max:
                    active_animation_name = animation_name
                    max = len(self.animation_activators[animation_name]["activators"])
                if on_last_frame:
                    self.animation_activators[animation_name]["stop-on-last-frame"] = False
                    self.animation_activators[animation_name]["activators"] = []
                    if self.animation_activators[animation_name]["reset-speed"] != 0:
                        self.milliseconds_per_sprite = self.animation_activators[animation_name]["reset-speed"]
                    self.animation_activators[animation_name]["reset-speed"] = 0
                
                
        if (active_animation_name == None):
            if ("default" in self.animations):
                active_animation_name = "default"
            else:
                return
            
        images = self.animations[active_animation_name]
        image_names = self.animations_image_names[active_animation_name]
        
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
        self.image_name = image_names[self.currentFrame]
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
                            if self.name == "chicken":
                                if (self.x_delta + delta[1] > -20.0 and self.x_delta + delta[1] < 530):
                                    Enemy.user_speed_modifier += delta[1] * 0.02
                                    Enemy.user_speed_modifier = 0 if (Enemy.user_speed_modifier < 0) else Enemy.user_speed_modifier
                                    self.x_delta += delta[1]
                            else:
                                self.x_delta += delta[1] * (1 if self.type != "ENEMY" else self.scroll_direction)
                        elif delta[0] == 'x-speed':
                            self.x_delta += delta[1] * Enemy.get_speed()
                        elif delta[0] == 'y':
                            self.y_delta += delta[1]
                        elif delta[0] == 'x-min':
                            if self.rect.x <= delta[1]:
                                self.kill()
                        elif delta[0] == 'x-min-reverse':
                            if self.rect.x <= delta[1]:
                                self.scroll_direction = -1
                        elif delta[0] == 'x-min-stop':
                            if self.rect.x <= delta[1]:
                                self.scroll_direction = 0
                                Enemy.disable_scrolling = True
                        elif delta[0] == 'x-max-reverse':
                            if self.rect.x >= delta[1]:
                                self.scroll_direction = 1
                        elif delta[0] == 'frames-to-jump':
                            if self.jump == 0 and self.canJump:
                                self.jump = delta[1]
                                self.canJump = False
                        elif delta[0] in self.animations:
                            self.setAnimationState(delta[0], delta[1], key)
            else:
                #negative
                if key in self.key_press_responses:
                    deltaList = self.key_press_responses[key]
                    for delta in deltaList:
                        if delta[0] in self.animations:
                            self.setAnimationState(delta[0], not delta[1], key)
                            

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
            #self.setAnimationState('stand', True)
            self.jump -= 1
            self.y_delta += -10 if (self.jump < 5) else -15
        else:
            #self.setAnimationState('stand', False)
            if (not onGround):
                to_ground = self.distToGround()
                self.y_delta += (GRAVITY * self.mass) if (to_ground >= GRAVITY*self.mass) else to_ground

            
class Effect(TCGameObject):
    def __init__(self, name, animation_config=None, key_press_responses=None, position=(0,0), padding=(0,0), parent=None):
        TCGameObject.__init__(self, name, animation_config, key_press_responses, position, padding, parent)
        self.type="EFFECT"
        self.age = 0
        #self.scaleFactor = 1
        self.life = 400
        
    def update(self, keys_pressed, clock):
        TCGameObject.update(self, keys_pressed, clock)
        
        #loc = self.parent.image.get_rect().center
        #self.image = pygame.transform.smoothscale(self.image, (self.age * self.scaleFactor, self.age * self.scaleFactor))

        if self.age < self.life:
            self.age += clock.get_time()
        else:
            self.kill()
            
class Enemy(TCGameObject):
    

    
    boss_elements = ["fire", "water", "earth"]
    
    disable_scrolling = False
    boss_element = 0
    player_hit_bonus = 1
    attack_bonus = 1
    enemies_killed = 0
    base_speed = 3
    user_speed_modifier = 0
    level_speed_modifier = 0
    damage_recieved = 0
    
    def get_speed(base_increase=0):
        return 0 if Enemy.disable_scrolling else (Enemy.user_speed_modifier + Enemy.base_speed + base_increase + Enemy.level_speed_modifier)

    def __init__(self, name, animation_config=None, key_press_responses=None, position=(0,0), padding=(0,0), parent=None):
        TCGameObject.__init__(self, name, animation_config, key_press_responses, position, padding, parent)
        self.type="ENEMY"
        self.hp = 10
        self.scroll_direction = 1
        self.x_bounded_by = [0,0]
        self.spells = None
        self.last_attack = 0
        self.dead = False
        self.attack_cooldown = 1200
        self.old = False
        
    def update(self, keys_pressed, clock):
        TCGameObject.update(self, keys_pressed, clock)
        if self.hp <= 0:
            if not self.dead:
                self.key_press_responses = {"ALWAYS":[('y', 20)]}
                self.dead = True
                Enemy.enemies_killed += 1
            else:
                if self.y_delta >= 700:
                    self.kill()
            
        
    def checkHits(self, group):
        
        BASE_HP = (1 if self.name != "ultimate-fox" else 0.2) * Enemy.player_hit_bonus
        
        if self.dead:
            return
        
        collisions = pygame.sprite.spritecollide(self, group, False, pygame.sprite.collide_circle_ratio(0.75))
        
        for thing in collisions:
            if thing.name == "shoot-spell" or thing.name == "hit-spell":
                dmg = (1*BASE_HP) if thing.name == "shoot-spell" else (3*BASE_HP)
                self.hp -= dmg
                Enemy.damage_recieved += dmg
                if TCGameObject.scene_groups != None and bool(random.getrandbits(1)):
                    TCGameObject.scene_groups["effects"].add(makeEffect("hit-marker", thing))
        
    
    def attack(self, clock, target):
        #can only attack if spell list is set
        if not self.dead and self.spells != None and len(self.spells) > 0:
            #will add spell into own layer (i.e. "enemy" layer)
            my_groups = self.groups()
            if self.last_attack < self.attack_cooldown:
                self.last_attack += clock.get_time()
            else:
                self.last_attack = 0
                if my_groups != None and len(my_groups) >= 1 and my_groups[0] != None:
                        for spell in self.spells:
                            if bool(random.getrandbits(1)):
                                
                                if self.name == "ultimate-fox":
                                    self.milliseconds_per_sprite = 200.0
                                    self.setAnimationState('cast', True, override=True, play_stop=True, reset_speed=400.0)
                                
                                if spell == "heal-spell":
                                    if self.hp <= 20:
                                        self.hp += 2
                                        my_groups[0].add(makeEffect(spell, self))
                                else:
                                    attack_effect = makeEffect(spell, self)
                                    if spell == "fox-elemental-spell":
                                        #hack to target player, instead of using random movement vector generated in makeEffect()
                                        x_step = ((target.x_delta+10)-attack_effect.x_delta)/10
                                        y_step = ((target.y_delta+20)-attack_effect.y_delta)/10
                                        attack_effect.key_press_responses = {"ALWAYS":[('x', x_step), ('y', y_step)]}
                                        
                                    my_groups[0].add(attack_effect)
                                break
                                
class Background(TCGameObject):
            
    def __init__(self, name, animation_config=None, key_press_responses=None, position=(0,0), padding=(0,0), parent=None):
        TCGameObject.__init__(self, name, animation_config, key_press_responses, position, padding, parent)
        self.type="BACKGROUND"
        self.scrollMultiplier = 1.0
        
        self.randomFactor = False
        self.wrap = 0
        self.skips = []
        
                
    def update(self):
        if self.x_delta <= -self.image.get_width():
            self.x_delta += self.image.get_width()
            
        self.x_delta -= self.get_scroll()
        
        TCGameObject.update(self)
        
    def get_scroll(self):
        return int(((Enemy.get_speed(2))*self.scrollMultiplier))
    
    def draw(self, screen):
        width = self.image.get_width()
        
        #Dear Reader
        #Do not try to understand this algorithm
        #I've horribly hacked the original repeat-blits-for-x-tiling algo to allow for scrolling gaps
        #It depends on:
        # - self.wrap
        # - self.skips
        # - self.randomFactor
        # - tiles_per_screen
        
        image_positions = []
        if not self.randomFactor or not 0 in self.skips:
            image_positions.append(self.x_delta)
                
        tiles_per_screen = int(math.floor((screen.get_width()/width)))
            
        repeat = 1
        while (image_positions[-1] if len(image_positions) > 0 else 0) + width < screen.get_width():
            if not self.randomFactor or not (repeat) in self.skips:
                image_positions.append(self.x_delta + (width*repeat))
            repeat += 1
        
        for position in image_positions:
            screen.blit(self.image, (position, self.y_delta))
        
        if self.randomFactor and abs(self.x_delta) >= width:
            self.wrap += 1
            self.wrap %= tiles_per_screen
            
            removeGaps = []
            
            for x in range(0, len(self.skips)):
                if self.skips[x]-1 < 0:
                    removeGaps.append(self.skips[x])
                else:
                    self.skips[x] -= 1
            
            for negative in removeGaps:
                self.skips.remove(negative)
            
            if len(self.skips) < 2 and bool(random.getrandbits(1)):
                self.skips.append(tiles_per_screen+1)