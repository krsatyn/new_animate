#hole center

import ursina
import json
import numpy as np

class Hole_center():
    
    def __init__(self, json_path:str=None, input_coordinate_dict:dict=None,) -> None:
        self.json_path = json_path
        self.input_coordinate_dict = input_coordinate_dict     
    
    
    # Распоковщик json файла
    def unpucking_json(self,) -> dict:
        """
        Если подаётся словарь то он должен иметь структуру приведенную ниже

        !!! len(input_coordinate_dict[start]) и len(input_coordinate_dict[end]) должно быть равным иначе произойдет ошибка!!!
        
        dict{
                "start":[{'X':float, 'Y':float,'Z':float}, next_point],
                "end":  [{'X':float, 'Y':float,'Z':float}, next_point]
        }
        
        """
        start_coordinates = []
        end_coordinates   = []
        
        if self.json_path is not(None):
            
            #Считывание с json файла    
            with open(self.json_path) as json_file:
                coordinate_dict = json.load(json_file)
        
            #получение координат 
            # Вид {start:[[start_coordinate_1],[start_coordinate_2]], end:[[end_coordinate_1],[end_coordinate_2]]}
            
            for key in coordinate_dict:
                point_name = "hole_" + str(key.split("_")[1])
                start_coordinates.append(coordinate_dict[point_name]['start'])
                end_coordinates.append(coordinate_dict[point_name]['end'])

            self.point_dict = {'start':start_coordinates, 'end':end_coordinates}
        
        # В случае если подается не json а заготовленный словарь 
        elif self.input_coordinate_dict is not(None):
            self.point_dict = self.input_coordinate_dict
    
    
    # Конвертор координат под формат Vec3 (так же записывает количество отверстий в self.hole_counter:int и self.pints_counter:int количество точек)
    def convertor_dict_coordinate_to_Vec3_coordinate(self,) -> dict:
        '''Необходим для предворительного конвртировния координат'''
        
        vec_3_point_dict = {'start':[], 'end':[]}
        point_dict = self.point_dict
        for index_hole in range(len(point_dict['start'])):
            
            start_point_coordinate = ursina.Vec3((float(point_dict['start'][index_hole]['X']), # получение начальной координаты по оси X
                                                  float(point_dict['start'][index_hole]['Y']), # получение начальной координаты по оси Y
                                                  float(point_dict['start'][index_hole]['Z']))) # получение начальной координаты по оси Z)
            
            end_point_coordinate  =  ursina.Vec3((float(point_dict['end'][index_hole]['X']),   # получение конечной координаты по оси X
                                                  float(point_dict['end'][index_hole]['Y']),   # получение конечной координаты по оси Y
                                                  float(point_dict['end'][index_hole]['Z'])))   # получение конечной координаты по оси Z

            vec_3_point_dict['start'].append(start_point_coordinate)
            vec_3_point_dict['end'].append(end_point_coordinate)
        
        self.vec_3_point_dict = vec_3_point_dict
        self.hole_counter = len(point_dict['start'])
        self.pints_counter = len(point_dict['start']) * 2 # так как у отверстия есть вход и выход
 
 
    # Генерация списка созданных обьектов
    def generate_entity_point_group(self,) -> dict:
        
        # Получение конвертированных координат
        point_dict = self.vec_3_point_dict
        
        # Получение количества отверситий
        hole_counter = self.hole_counter
        

        # Словарь Entity sphere где ключ start входные отверстия а end выходные
        object_dict = {'start':[], 'end':[]}
        
        for hole_index in range(hole_counter):

            object_dict['start'].append(ursina.Entity(model='sphere',                             # Тип обьекта
                                                      color=ursina.color.green,                   # Цвет обьекта
                                                      position=point_dict['start'][hole_index]))  # Позиция    
            
            object_dict['end'].append(ursina.Entity(model='sphere',                               # Тип обьекта
                                                    color=ursina.color.red,                       # Цвет обьекта
                                                    position=point_dict['end'][hole_index]))      # Позиция    
            
            
        self.object_point_dict = object_dict
        
        return object_dict
    
    
    # Создает связи между точками
    def generate_connections_with_points(self, color_connection:ursina.color.Color=ursina.color.pink,) -> list:
        
        # Получение конвертированных координат
        point_dict = self.vec_3_point_dict
        
        # Получение количества отверситий
        hole_counter = self.hole_counter
        
        # Список Entity Cylinder выполняющие роль соединений
        connection_list = []

        # Создание связей 
        for index_hole in range(hole_counter):
            
            # Получение координаты повнаправление цилиндра (координаты конца - координаты начала)
            turn_coordinate =  np.subtract(np.array(point_dict['end'][index_hole]), np.array(point_dict['start'][index_hole]))
            
            # Создание обьекта Цилиндр по заданными параметрам
            connection = ursina.Entity(model=ursina.Cylinder(resolution=6,                              # Количество граней
                                                             direction=(                                # Конечная координата:tuple(x,y,z)     
                                                                    turn_coordinate[0],                 # Конечная координата X
                                                                    turn_coordinate[1],                 # Конечная координата Y
                                                                    turn_coordinate[2])),               # Конечная координата Z
                                                            position=point_dict['start'][index_hole],   #Стартовая координата
                                                            color=color_connection)                     # Цвет соединения 
            

            connection_list.append(connection)
        
        self.connection_list = connection_list
        
        return connection_list
       
        
    # Основной метод запуска скрипта          
    def main(self,):
        
        #Список всех обьектов    
        object_list = []
        
        # распаковываем json
        self.unpucking_json() 

        # Конвертация координат под формат ursina.Vec3
        self.convertor_dict_coordinate_to_Vec3_coordinate()
        
        #создаем список Entity точек центров отверстий 
        entity_point_group = self.generate_entity_point_group()
        
        #создаем список Entity цилиндров выполняюших роль соединения центров отверстий (соединяет start и end)  
        connections_points = self.generate_connections_with_points()
        
        #Заполнение списка обьектов
        object_list.append(entity_point_group)
        object_list.append(connections_points)
        
        return object_list
        