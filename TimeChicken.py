import pygame
from tc_utils import TCGameObject

pygame.init()
pygame.font.init()

myfont = pygame.font.Font('Assets/Fonts/tc_1_bold.ttf', 80)

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

scene_groups = [layer1, layer2]

chickenControls = {
    "ALWAYS":[('x', 1), ('walk', True)]
    ,str(pygame.K_SPACE):[('walk', False), ('frames-to-jump', 15)]
}
chickenAnims = {
    "walk" : ['chicken1.png', 'chicken2.png', 'chicken3.png', 'chicken4.png', 'chicken5.png']
    ,"default" : ['chicken.png']
}

chicken = TCGameObject("chicken", IMAGE_HOME, chickenAnims, chickenControls, (80,0), (0, 60))

eggAnims = {
    "default" : ['Egg_1.png', 'Egg_2.png', 'Egg_3.png', 'Egg_4.png', 'Egg_5.png', 'Egg_6.png', 'Egg_7.png', 'Egg_8.png' ]
}
egg = TCGameObject("egg", IMAGE_HOME, eggAnims, None, padding=(0, 10))

layer1.add(chicken)
layer2.add(egg)

print("Initialising Time Chicken...")

spell = ""

while not closegame:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            closegame = True

        ############################
                
        if event.type == pygame.KEYDOWN:
            keys_pressed[str(event.key)] = True
            if (pygame.K_a <= event.key and pygame.K_z >= event.key):
                spell += pygame.key.name(event.key)
            #TODO REMOVE SPACE AS TEXT
            if (pygame.K_SPACE == event.key):
                spell += " "
        if event.type == pygame.KEYUP:
            keys_pressed[str(event.key)] = False
        ######################        
    
    gameDisplay.fill(black)
    for scene in scene_groups:
        for gameobj in scene.sprites():
            gameobj.doPhysics()
            gameobj.updateAnimation(clock.get_time())
            if (gameobj.key_press_responses != None):
                gameobj.processKeys(keys_pressed)
            #gameobj.updateRect()
            gameobj.updatePosition()
            
        scene.draw(gameDisplay)
        
    gameDisplay.blit(myfont.render(spell, True, (255, 255, 255)), (0,0))
    
    pygame.display.update()
    clock.tick(60)

print("Quitting Time Chicken...")
pygame.quit()
quit()