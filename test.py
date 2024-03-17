from hole_center import Hole_center
import ursina
import time

'''Основные настройки ursina'''
ursina.window.title = "Визуализация"    
app = ursina.Ursina(borderless=False)

# Настройки окна
ursina.window.exit_button.enable = True
ursina.window.cog_button.enable = False
ursina.window.fps_counter.enable = False
ursina.window.fullscreen = False


coordinate_list = [[0.1, 0, 0]]

# def create_obj(to, i):
#     to.coordi += i
#     return to

# def update():
    
#     for i in range(6):
#         create_obj(to=test_obj, i=i)
        
    

#Стартовое положение
starts = ursina.Entity(model='sphere', scale=5,  position=[0,30,0], color=ursina.color.green)

#Ожидаемое конечное
ends = ursina.Entity(model='sphere', scale=5,  position=[30,0,0], color=ursina.color.pink)
# Испытыуемый
test_obj = ursina.Entity(model=ursina.Cylinder(resolution=8, height=30, radius=2.5))

test_obj.animate_position((10,0,0), duration=2, loop=True)

#test_obj.world_rotation += (30,0,20)
#test_obj.position = ends.position

#Центр мира
ursina.Entity(model='sphere', scale=5, color=ursina.color.red)

# Камера 
ursina.EditorCamera()

'''настройки запуска приоложения '''
app.run()