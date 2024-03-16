#visualization_script.py

'''=====================>   Переделать под связи и эндоскоп    <=====================
ursina.Entity(model=ursina.Pipe(base_shape=ursina.Circle()))
'''

import ursina
import numpy as np

from endoscope import Endoscope
from hole_center import Hole_center

'''Установка путей'''
# Путь до модели
model_path = 'src/stl/ImageToStl.com_p60k_301.stl'
# Путь до json файла(центры отверстия)
hole_center_coordinate_path = 'src\json\hole_coordinate.json'
# Путь до json файла(Координат положения эндоскопа)
endoscope_coordinate_path = 'src\json\combine.json'

'''Просмотр на отдельном отверстии'''
hole_number = ""

'''Основные настройки ursina'''
ursina.window.title = "Визуализация"    
app = ursina.Ursina(borderless=False)

# Настройки окна
ursina.window.exit_button.enable = True
ursina.window.cog_button.enable = False
ursina.window.fps_counter.enable = False
ursina.window.fullscreen = False


'''Центы отверстий'''
hc = Hole_center(json_path=hole_center_coordinate_path)
object_point_list = hc.main()

#encp = Endoscope(input_coordinate_dict={'start':[{'X':0, 'Y':0, 'Z':0}],
#                                        'end':  [{'X':0, 'Y':20, 'Z':0}]})

# Эндоскоп
encp = Endoscope(json_path=endoscope_coordinate_path, point_objects_list=object_point_list)
encp.main()

# Деталь
#detail = ursina.Entity(model=model_path, color = ursina.color.hsv(0, 0, 1, .5))

# Камера 
ursina.EditorCamera()

'''настройки запуска приоложения '''
app.run()