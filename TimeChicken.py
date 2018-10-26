import pygame
import random
from tc_utils import TCGameObject, Background, Enemy, makeEnemy, makeEffect

class Menu:
    def __init__(self):
        self.do_game = False
        self.closegame = False
        self.options = ["Story Flow", "Endless Flow", "Quit"]
        
    def run(self, game):
        pygame.init()
        pygame.font.init()

        bigfont = pygame.font.Font('Assets/Fonts/tc_1_bold.ttf', 80)
        
        IMAGE_HOME = "Assets/Images/"
        display_width = 1280
        display_height = 720
        menuGameDisplay = pygame.display.set_mode((display_width,display_height))
        bg_col = (50, 10, 40)
        clock = pygame.time.Clock()
        delay = 0
        
        self.do_game = False
        self.closegame = False
        game.return_to_menu = False
        self.selected_option = 0
        
        OPENING_DELAY = 100
        
        TCGameObject.image_home = IMAGE_HOME
        
        layer1 = pygame.sprite.LayeredUpdates()
        house = TCGameObject("house", {"default":["menu_2.png"]},{"ALWAYS":[('x-speed', -1), ('x-min', -500)]}, position=(0, 0))
        bg = TCGameObject("house", {"default":["menu_1.png"]}, position=(420, -30))
        layer1.add(house)
        layer1.add(bg)
        
        while not self.do_game and not self.closegame:
            menuGameDisplay.fill(bg_col)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.closegame = True
                    
                if delay >= OPENING_DELAY:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            option_text = self.options[self.selected_option]
                            if (option_text == "Quit"):
                                self.closegame = True
                            else:
                            
                                #TODO: change game settings here
                                if option_text == "Story Flow":
                                    print("Starting " + option_text)
                                elif option_text == "Endless Flow":
                                    print("Starting " + option_text)
                                    
                                self.do_game = True
                                
                        elif event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) if self.selected_option > 0 else (len(self.options)-1) 
                        elif event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) if self.selected_option < (len(self.options)-1) else 0
                        
            option_pos = 0
            for option in self.options:
                option_color = (255, 255, 155) if self.options[self.selected_option] == option else (100, 100, 80)
                menuGameDisplay.blit(bigfont.render(option, True,  option_color), (80, 200 + option_pos))
                option_pos += 80
            
            if delay >= OPENING_DELAY:
                house.update({"ALWAYS":True}, clock)
            else:
                delay += 1
            
            bg.update(clock=clock)
            layer1.draw(menuGameDisplay)
            
            pygame.display.update()
            clock.tick(60)

class Game:
    
    def __init__(self):
        self.closegame = False
        self.game_state = "Initialising"
        self.return_to_menu = False

    def run(self):
        pygame.init()
        pygame.font.init()

        giantfont = pygame.font.Font('Assets/Fonts/tc_1_bold.ttf', 150)
        bigfont = pygame.font.Font('Assets/Fonts/tc_1_bold.ttf', 80)
        smallfont = pygame.font.Font('Assets/Fonts/tc_1.ttf', 40)

        ################################# START Game Config
        IMAGE_HOME = "Assets/Images/"
        display_width = 1280
        display_height = 720
        gameDisplay = pygame.display.set_mode((display_width,display_height))
        pygame.display.set_caption('Time Chicken from Chicken Coup')
        bg_col = (200, 170, 120)
        self.closegame = False
        self.return_to_menu = False
        reset = False
        clock = pygame.time.Clock()
        keys_pressed = {"ALWAYS" : True}
        timePassedLastFrame = 0
        TEXT_X = 475
        hp = 100
        distance = 0
        last_added_enemy_time=0
        add_enemy_interval=2000.0
        
        doing_bossfight = False
        boss_hp = 0
        bossfight_wins = 0
        distance_at_last_bossfight = 0
        distance_to_next_bossfight = 50.0
            
        Enemy.base_speed = 3
        Enemy.user_speed_modifier = 0
        Enemy.level_speed_modifier = 0
        Enemy.disable_scrolling = False
        
        ################################# END Game Config

        layer1 = pygame.sprite.LayeredUpdates()
        layer2 = pygame.sprite.LayeredUpdates()
        layer3 = pygame.sprite.LayeredUpdates()
        enemies = pygame.sprite.LayeredUpdates()
        background = pygame.sprite.LayeredUpdates()
        
        scene_groups = {
            "background": background
            ,"enemies": enemies
            ,"props" : layer2
            ,"player": layer1
            ,"effects" : layer3
        }
        
        #register the layers with TCGameObject so objects can spawn, e.g. effects
        TCGameObject.scene_groups = scene_groups
        TCGameObject.image_home = IMAGE_HOME
        
        chickenControls = {
            #"ALWAYS":[('walk', True)]
            str(pygame.K_RIGHT):[('x', 5), ('walk', True)]
            ,str(pygame.K_LEFT):[('x', -5), ('walk', True)]
            ,str(pygame.K_SPACE):[('frames-to-jump', 15)]
        }

        chickenAnims = {
            "walk" : ['chicken1.png', 'chicken2.png', 'chicken3.png', 'chicken4.png', 'chicken5.png']
            ,"default" : ['chicken.png']
            ,"cast": ['magic1.png', 'magic2.png', 'magic3.png', 'magic4.png', 'magic5.png', 'magic6.png', 'magic7.png', 'magic8.png']
        }

        chicken = TCGameObject("chicken", chickenAnims, chickenControls, (120,100), (0, 60))
        chicken.physics = True
        chicken.mass = 3
        chicken.setAnimationState('walk', True)
        
        layer1.add(chicken)
        
        
        house = TCGameObject("house", {"default":["house.png"]},{"ALWAYS":[('x-speed', -0.9), ('x-min', -500)]}, position=(0, 57))
        rock = TCGameObject("rock", {"default":["rock.png"]},{"ALWAYS":[('x-speed', -0.9), ('x-min', -500)]}, position=(100, 270))
        layer2.add(house)
        layer3.add(rock)
               
        eggAnims = {
            "default" : ['Egg_1.png', 'Egg_2.png', 'Egg_3.png', 'Egg_4.png', 'Egg_5.png', 'Egg_6.png', 'Egg_7.png', 'Egg_8.png' ]
        }

        eggControls = {
            "ALWAYS":[('frames-to-jump', chicken.jump)]
        }

        egg = TCGameObject("egg", eggAnims, eggControls, (-40, 10), (0, 0))

        egg.slowParentDelay = 10
        egg.parent = chicken

        
        layer1.add(egg)
        
        
        clouds = Background("clouds", {"default":["clouds_1.png"]}, None, position=(0, 50))
        clouds.scrollMultiplier = 0.2
        background.add(clouds)
        
        
        mountains = Background("mountains", {"default":["mountains.png"]}, None, position=(0, 450))
        mountains.scrollMultiplier = 0.5
        background.add(mountains)
        
        trees = Background("trees", {"default":["Oak.png"]}, None, position=(0, 375))
        trees.scrollMultiplier = 0.8
        #trees.randomFactor = True
        background.add(trees)
        
        grass = Background("grass", {"default":["grass_1.png"]}, None, position=(0, 550))
        background.add(grass)

        
        
        print(self.game_state + " Time Chicken...")

        spell = {"color":[255, 255, 255], "text":"", "position":(0,0)}
        cast = 0
        lastSpell = ""
        spell_queue = []
        spells = {
            "toot":"gets them everytime"
            ,"cluck":"???"
            ,"pipipi":"???"
            ,"kukareku":"???"
            ,"cockadoodledoo":"???"
            ,"cheekpeep":"???"
            ,"tocktock":"???"
            ,"gutgutgdak":"???"
        }
        message = {"text":"", "color": (255, 255, 255), "frames":0, "position":(0,0)}
        speech = {"text":"", "color": (255, 255, 255), "frames":0, "position":(400, 200)}

        spellbook = False
        paused = False

        while not self.closegame and not reset and not self.return_to_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.closegame = True

                ############################
                        
                if event.type == pygame.KEYDOWN:
                    keys_pressed[str(event.key)] = True
                    #allow typing even when cancelled for more seamless gameplay
                    if not paused and not spellbook and pygame.K_a <= event.key and pygame.K_z >= event.key:
                        spell["text"] += pygame.key.name(event.key)
                    elif not paused and not spellbook and pygame.K_BACKSPACE == event.key and message["text"] == "" and spell["text"] != "" and cast == 0:
                        spell["text"] = ""
                        message["text"] = "CANCEL!"
                        message["color"] = (255, 20, 20)
                        message["frames"] = 30
                    elif not paused and event.key == pygame.K_TAB:
                        spellbook = True
                        #tint current screen before pause text draws
                        gameDisplay.fill((0, 75, 40), special_flags=pygame.BLEND_RGBA_MULT)
                    elif event.key == pygame.K_ESCAPE:
                        spellbook = False
                        paused = not paused
                        #tint current screen before pause text draws
                        gameDisplay.fill((0, 40, 75), special_flags=pygame.BLEND_RGBA_MULT)
                    elif paused:
                        if (pygame.key.get_mods() & pygame.KMOD_CTRL) and event.key == pygame.K_x:
                            self.closegame = True
                        elif event.key == pygame.K_r:
                            reset = True
                            self.game_state = "Restarting"
                        elif event.key == pygame.K_m:
                            self.return_to_menu = True
                            print("Return to menu...")
                if event.type == pygame.KEYUP:
                    keys_pressed[str(event.key)] = False
                    if event.key == pygame.K_TAB:
                        spellbook = False
                ######################      
            
            current_ticks = pygame.time.get_ticks()
            random_delay = random.uniform(0.0, 1000.0)
            
            #if you are at (or a bit past) the next bossfight
            if distance - (distance_at_last_bossfight + distance_to_next_bossfight) >= 0:
                doing_bossfight = True
                Enemy.disable_scrolling = True
                distance_at_last_bossfight = distance
            
            
                
                
            if not doing_bossfight:
                #add enemies one at a time at random intervals
                if (current_ticks - last_added_enemy_time) > (add_enemy_interval + random_delay) and len(enemies.sprites()) == 0:
                    
                    #badgers return until next boss fight
                    last_added_enemy_time = current_ticks    
                    enemies.add(makeEnemy("badger"))
            else:
                #Chicken stops walking
                #WAIT THE CHICKEN ALREADY ISN'T WALKING!?
                #mind.blown=True, right?
                #chicken.setAnimationState('walk', False)
                               
                #add boss if not added
                #Modified: don't kill everything else in layer as in earlier implementation
                boss_is_added = False
                for sprite in enemies.sprites():
                    if sprite.type == "ENEMY" and sprite.name == "fox":
                        boss_is_added = True
                        boss_hp = sprite.hp
                        break
                
                if not boss_is_added:
                    boss = makeEnemy("fox")
                    enemies.add(boss)
                    boss_hp = boss.hp
                    
                    
                    #chicken.setAnimationState('default', True)
                                        
                    if speech["frames"] == 0 and speech["text"] != "HALT!":
                        speech["text"] = "STOP, CHICKEN!"
                        speech["color"] = (255, 0, 0)
                        speech["frames"] = 30
                
                if boss_hp <= 0:
                    #Continue only after defeating boss
                    Enemy.disable_scrolling = False
                    
                    
                    #chicken.setAnimationState('walk', True)
                    #chicken.setAnimationState('default', False)
                    
                    Enemy.boss_element = (Enemy.boss_element + 1) if Enemy.boss_element+1 < len(Enemy.boss_elements) else 0
                    doing_bossfight = False
                    bossfight_wins += 1
                    #next boss is further away
                    distance_to_next_bossfight += 10
                    #rotate colors/randomise bg layers after win
                    r = (bg_col[0] + 175) % 255
                    g = (bg_col[0] + 175) % 255
                    b = (bg_col[0] + 175) % 255
                    bg_col = (r,g,b)
                    tree_images = ["Oak.png", "Lime.png", "Pine.png", "NotPine.png"]
                    trees.setAnimations({"default":[tree_images[bossfight_wins%len(tree_images)]]}, True)
        
            if not spellbook and not paused:
                gameDisplay.fill(bg_col)
                
                for scene_group in scene_groups:
                    for gameobj in scene_groups[scene_group].sprites():
                        if (gameobj.type == "DEFAULT"):
                            gameobj.update(keys_pressed, clock)
                        elif (gameobj.type == "EFFECT"):
                            gameobj.update(keys_pressed, clock)
                        elif (gameobj.type == "ENEMY"):
                            gameobj.update(keys_pressed, clock)
                        elif (gameobj.type == "BACKGROUND"):
                            gameobj.update()
                            gameobj.draw(gameDisplay)
                    
                    if (scene_group != "background"):
                        scene_groups[scene_group].draw(gameDisplay)

                for enemy in enemies.sprites():
                    #now "EFFECT" can also appear in enemy layer
                    if enemy.type == "ENEMY":
                        #enemy can check for hits against the "effects" layer which contains spells
                        enemy.checkHits(layer3)
                        #enemy will add it's attacks into the "enemy" layer
                        enemy.attack(clock, chicken)
                
                #lose hp for touching enemies or enemy spells (which are spawned in "enemy" layer)
                collisions = pygame.sprite.spritecollide(chicken, enemies, False, pygame.sprite.collide_circle_ratio(0.5))
                
                if (len(collisions) > 0):
                    hp -= len(collisions) * (3 if doing_bossfight else 1)
                    if bool(random.getrandbits(1)):
                        layer3.add(makeEffect("hit-marker", chicken))
                
                spell["position"] = (chicken.rect.x + 50, chicken.rect.y - 80)
                
                gameDisplay.blit(bigfont.render(spell["text"], True, tuple(spell["color"])), spell["position"])
                
                if cast > 0:
                    cast -= 1
                    spell["color"][0] -= 2
                    spell["color"][1] -= 5
                    spell["color"][2] -= 10
                    
                    if cast == 0:
                        spell["color"] = [255, 255, 255]
                        chicken.setAnimationState('cast', False)
                        #chicken.setAnimationState('walk', True)
                        
                if not doing_bossfight and not Enemy.disable_scrolling and cast == 0:
                    chicken.setAnimationState("walk", True)
                else:
                    chicken.setAnimationState("walk", False)
                        
                if message["text"] != "" and message["frames"] > 0:
                    if (message["text"] == "CANCEL!"):
                        message["position"] = spell["position"]
                    else:
                        message["position"] = (spell["position"][0], spell["position"][1] - 60)
                    gameDisplay.blit(bigfont.render(message["text"], True, message["color"]), message["position"])
                    message["frames"] -= 1
                else:
                    message["text"] = ""
                    
                    
                if speech["text"] != "" and speech["frames"] > 0:
                    gameDisplay.blit(giantfont.render(speech["text"], True, speech["color"]), speech["position"])
                    speech["frames"] -= 1
                else:
                    speech["text"] = ""
                    
                     
                if spell["text"] in spells:
                    
                    spell_queue.append(spell["text"])        
                    
                    spell["color"] = [255, 255, 255]
                    
                    spell["text"] = ""
                    
                if cast == 0 and len(spell_queue) >= 1:
                    spellsList = list(spells.keys())
                    current_spell = spell_queue.pop(0)
                    
                    message["text"] = "No Effect!" if (current_spell == "cluck" and doing_bossfight) else "Cast "+current_spell+"!"
                    message["color"] = (255, 255, 155)
                    message["frames"] = 30
                    
                    if current_spell == spellsList[0]:
                        if (hp <= 195):
                            hp += 5
                            layer3.add(makeEffect("heal-spell", chicken))
                    elif current_spell == spellsList[1]:
                        if not doing_bossfight:
                            for sprite in enemies.sprites():
                                if (sprite.x_delta >= chicken.x_delta):
                                    sprite.x_delta = chicken.x_delta - 100
                    elif current_spell == spellsList[2]:
                        layer3.add(makeEffect("shoot-spell", chicken))
                    elif current_spell == spellsList[3]:
                        layer3.add(makeEffect("hit-spell", chicken))
                        
                    cast = 20
                    chicken.setAnimationState('walk', False)
                    chicken.setAnimationState('cast', True)
                
                iconImg = "icon1.png" if (hp >= 30) else "icon2.png"
                gameDisplay.blit(pygame.image.load(IMAGE_HOME + iconImg), (0, 10))
                
                gameDisplay.blit(smallfont.render("FPS:" + "{:.2f}".format(clock.get_fps()), True, (255, 255, 155)), (1100, 10))
                
                uiXPadding = 200
                
                gameDisplay.fill((200, 25, 25), pygame.Rect(uiXPadding, 90, (300*(hp/100) if hp > 0 else 1), 20))#,special_flags=pygame.BLEND_RGBA_MULT)
                hp_str = "0" if hp <= 0 else str(hp)
                gameDisplay.blit(bigfont.render(hp_str + "hp", True, (255,255,255)), (uiXPadding,95))
                
                
                if doing_bossfight and boss_hp > 0:
                    gameDisplay.fill((150, 25, 150), pygame.Rect(uiXPadding, 650, (800*(boss_hp/100) if boss_hp > 0 else 1), 20))
                    boss_hp_str = "0" if boss_hp <= 0 else str(boss_hp)
                    
                
                progress_to_bossfight = (distance-distance_at_last_bossfight)/(distance_to_next_bossfight if distance_to_next_bossfight > 0 else 1)
                gameDisplay.fill((25, 25, 200), pygame.Rect(uiXPadding, 5, (1000*(progress_to_bossfight) if progress_to_bossfight > 0 else 1), 5))#,special_flags=pygame.BLEND_RGBA_MULT)
                gameDisplay.blit(bigfont.render("{:.0f}".format(distance) + "m", True, (255,255,255)), (uiXPadding,0))
                
                distance += (Enemy.get_speed()/Enemy.base_speed)/50.0
                if hp <= 0:
                    reset = True
                    
            elif spellbook:
                gameDisplay.blit(bigfont.render("SPELLBOOK", True, (255, 255, 200)), (TEXT_X, 20))
                
                line_height = 60
                line = 1
                for desc in spells:                
                    gameDisplay.blit(smallfont.render(desc + " - " + spells[desc], True, (255, 255, 200)), (TEXT_X, 80+(line_height*line)))
                    line += 1
                
            elif paused:
                gameDisplay.blit(bigfont.render("PAUSED", True, (255, 255, 155)), (TEXT_X, 20))
                gameDisplay.blit(smallfont.render("ESC to resume", True, (255, 255, 155)), (TEXT_X, 150))
                gameDisplay.blit(smallfont.render("CTRL-X to quit", True, (255, 255, 155)), (TEXT_X, 280))
                gameDisplay.blit(smallfont.render("R to restart", True, (255, 255, 155)), (TEXT_X, 410))
                gameDisplay.blit(smallfont.render("M to return to menu", True, (255, 255, 155)), (TEXT_X, 540))
                
                
                
            pygame.display.update()
            clock.tick(60)

if __name__ == '__main__':

    

    menu = Menu()
    game = Game()
    
    while not menu.closegame and not game.closegame:
        menu.run(game)
        if menu.do_game:
            while not game.closegame and not game.return_to_menu:
                game.run()

    print("Quitting Time Chicken...")
    pygame.quit()
    quit()