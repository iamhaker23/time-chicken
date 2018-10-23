import pygame
from tc_utils import TCGameObject, makeEnemy

class Game:
    def run(self):
        pygame.init()
        pygame.font.init()

        bigfont = pygame.font.Font('Assets/Fonts/tc_1_bold.ttf', 80)
        smallfont = pygame.font.Font('Assets/Fonts/tc_1.ttf', 40)

        ################################# START Game Config
        IMAGE_HOME = "Assets/Images/"
        display_width = 1280
        display_height = 720
        gameDisplay = pygame.display.set_mode((display_width,display_height))
        pygame.display.set_caption('Time Chicken from Chicken Coup')
        black = (60, 84, 145)
        white = (225,225,225)
        closegame = False
        clock = pygame.time.Clock()
        keys_pressed = {"ALWAYS" : True}
        timePassedLastFrame = 0
        ################################# END Game Config

        layer1 = pygame.sprite.LayeredUpdates()
        layer2 = pygame.sprite.LayeredUpdates()
        enemies = pygame.sprite.LayeredUpdates()

        scene_groups = {
            "enemies": enemies
            ,"player": layer1
            ,"foreground" : layer2
        }

        chickenControls = {
            "ALWAYS":[('walk', True)]
            ,str(pygame.K_RIGHT):[('x', 5)]
            ,str(pygame.K_LEFT):[('x', -5)]
            ,str(pygame.K_SPACE):[('walk', False), ('frames-to-jump', 20)]
        }

        chickenAnims = {
            "walk" : ['chicken1.png', 'chicken2.png', 'chicken3.png', 'chicken4.png', 'chicken5.png']
            ,"default" : ['chicken.png']
        }

        chicken = TCGameObject("chicken", IMAGE_HOME, chickenAnims, chickenControls, (80,0), (0, 60))

        eggAnims = {
            "default" : ['Egg_1.png', 'Egg_2.png', 'Egg_3.png', 'Egg_4.png', 'Egg_5.png', 'Egg_6.png', 'Egg_7.png', 'Egg_8.png' ]
        }

        eggControls = {
            "ALWAYS":[('frames-to-jump', chicken.jump)]
        }

        egg = TCGameObject("egg", IMAGE_HOME, eggAnims, eggControls, (-40, 27), (0, 0))

        egg.slowParentDelay = 10
        egg.parent = chicken
        egg.physics = False


        layer1.add(chicken)
        layer2.add(egg)

        print("Initialising Time Chicken...")

        spell = {"color":[255, 255, 255], "text":"", "position":(0,0)}
        cast = 0

        spells = {
            "toot":"gets them everytime"
            ,"cluck":"???"
            ,"pipipi":"???"
            ,"kukareku":"???"
            ,"cock a doodle doo":"???"
            ,"cheek peep":"???"
            ,"tock tock":"???"
            ,"gut gut gdak":"???"
            }
        message = {"text":"", "color": (255, 255, 255), "frames":0, "position":(0,0)}

        spellbook = False
        paused = False

        while not closegame:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    closegame = True

                ############################
                        
                if event.type == pygame.KEYDOWN:
                    keys_pressed[str(event.key)] = True
                    #allow typing even when cancelled for more seamless gameplay
                    if not paused and not spellbook and pygame.K_a <= event.key and pygame.K_z >= event.key and cast == 0: #and message["frames"] == 0:
                        spell["text"] += pygame.key.name(event.key)
                    elif not paused and not spellbook and pygame.K_RETURN == event.key and message["text"] == "" and spell["text"] != "" and cast == 0:
                        spell["text"] = ""
                        message["text"] = "CANCEL!"
                        message["color"] = (255, 155, 155)
                        message["frames"] = 30
                    elif not paused and event.key == pygame.K_TAB:
                        spellbook = True
                    elif event.key == pygame.K_ESCAPE:
                        spellbook = False
                        paused = not paused
                        #tint current screen before pause text draws
                        gameDisplay.fill((0, 40, 75), special_flags=pygame.BLEND_RGBA_MULT)
                    elif paused and (pygame.key.get_mods() & pygame.KMOD_CTRL) and event.key == pygame.K_s:
                        closegame = True
                if event.type == pygame.KEYUP:
                    keys_pressed[str(event.key)] = False
                    if event.key == pygame.K_TAB:
                        spellbook = False
                ######################        
            
            if pygame.time.get_ticks() % 150.0 == 0.0 and len(enemies.sprites()) == 0:
                enemies.add(makeEnemy("badger", IMAGE_HOME))
            
            if not spellbook and not paused:
                gameDisplay.fill(black)
                for scene_group in scene_groups:
                    if scene_group == "enemies":
                        collisions = pygame.sprite.spritecollide(chicken, enemies, False, pygame.sprite.collide_circle_ratio(0.5))
                        for enemy in scene_groups[scene_group].sprites():
                            enemy.update(keys_pressed, clock, collisions)
                    else:
                        for gameobj in scene_groups[scene_group].sprites():
                            gameobj.update(keys_pressed, clock)
                    scene_groups[scene_group].draw(gameDisplay)
                    
                spell["position"] = (chicken.rect.x + 50, chicken.rect.y - 80)
                
                gameDisplay.blit(bigfont.render(spell["text"], True, tuple(spell["color"])), spell["position"])
                
                if cast > 0:
                    cast -= 1
                    spell["color"][0] -= 2
                    spell["color"][1] -= 5
                    spell["color"][2] -= 10
                    if cast == 0:
                        spell["text"] = ""
                        spell["color"] = [255, 255, 255]
                
                if message["text"] != "" and message["frames"] > 0:
                    if (message["text"] == "CANCEL!"):
                        message["position"] = spell["position"]
                    else:
                        message["position"] = (spell["position"][0], spell["position"][1] - 60)
                    gameDisplay.blit(bigfont.render(message["text"], True, message["color"]), message["position"])
                    message["frames"] -= 1
                else:
                    message["text"] = ""
            elif spellbook:
                gameDisplay.blit(bigfont.render("SPELLBOOK", True, (255, 255, 200)), (580, 20))
                
                line_height = 60
                line = 1
                for desc in spells:                
                    gameDisplay.blit(smallfont.render(desc + " - " + spells[desc], True, (255, 255, 200)), (580, 80+(line_height*line)))
                    line += 1
                
                
            elif paused:
                gameDisplay.blit(bigfont.render("PAUSED", True, (255, 255, 155)), (580, 20))
                gameDisplay.blit(smallfont.render("ESC to resume", True, (255, 255, 155)), (580, 150))
                gameDisplay.blit(smallfont.render("CTRL-S to save and quit", True, (255, 255, 155)), (580, 280))
                
                
            pygame.display.update()
            clock.tick(60)
            
            if spell["text"] in spells and cast == 0:
                spell["color"] = [255, 255, 255]
                message["text"] = "Cast "+spell["text"]+"!"
                message["color"] = (255, 255, 155)
                message["frames"] = 30
                cast = 20
                
        print("Quitting Time Chicken...")
        pygame.quit()
        quit()

if __name__ == '__main__':
    Game().run()