from hole_center import Hole_center
import ursina


'''Основные настройки ursina'''
ursina.window.title = "Визуализация"    
app = ursina.Ursina(borderless=False)

# Настройки окна
ursina.window.exit_button.enable = True
ursina.window.cog_button.enable = False
ursina.window.fps_counter.enable = False
ursina.window.fullscreen = False



# Камера 
ursina.EditorCamera()

'''настройки запуска приоложения '''
app.run()