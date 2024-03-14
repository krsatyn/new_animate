#visualization_script.py

import ursina
import numpy as np

from endoscope import Endoscope
from hole_center import Hole_center

'''Установка путей'''
# Путь до модели
model_path = 'src/stl/ImageToStl.com_p60k_301.stl'
# Путь до json файла(центры отверстия)
hole_center_coordinate_path = 'src\json\hole_coordinate.json'
# Путь до json файла(Координат положения энлоскопа)
endoscope_coordinate_path = ''

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


'''Классы'''
endscp = Endoscope()
hc = Hole_center(json_path=hole_center_coordinate_path)

'''Обьекты выводимые на экран'''

#Индоскоп
endscp.create_endoscope()

#Центры отверстий
hc.main()

# Деталь
detail = ursina.Entity(model=model_path, color = ursina.color.hsv(0, 0, 1, .5))

# Камера 
ursina.EditorCamera()

'''настройки запуска приоложения '''
app.run()