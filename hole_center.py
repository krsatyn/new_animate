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
    
    
    
    # Генерация списка созданных обьектов
    def generate_entity_point_group(self) -> dict:
        
        point_dict = self.point_dict
        object_dict = {'start':[], 'end':[]}
        
        for index in range(len(point_dict['start'])):
            
            coordinate_Vec3 = ( float(point_dict['start'][index]['X']),             # Конвертация X координаты для начальной позиции
                                float(point_dict['start'][index]['Y']),             # Конвертация Y координаты для начальной позиции
                                float(point_dict['start'][index]['Z']))             # Конвертация Z координаты для начальной позиции

            
            object_dict['start'].append(ursina.Entity(model='sphere',             # Тип обьекта
                                                      color=ursina.color.green,   # Цвет обьекта
                                                      position=coordinate_Vec3))  # Позиция    
            
            coordinate_Vec3 = ( float(point_dict['end'][index]['X']),               # Конвертация X координаты для конечной позиции
                                float(point_dict['end'][index]['Y']),               # Конвертация Y координаты для конечной позиции
                                float(point_dict['end'][index]['Z']))               # Конвертация Z координаты для конечной позиции
            
            
            object_dict['end'].append(ursina.Entity(model='sphere',               # Тип обьекта
                                                    color=ursina.color.red,       # Цвет обьекта
                                                    position=coordinate_Vec3))    # Позиция    
            
            
        self.object_point_dict = object_dict
        
        return object_dict
        
    
    def main(self,):
        
        self.unpucking_json() # распаковываем json
        object_list = self.generate_entity_point_group() #создаем список Entity точек центров отверстий 
        
        return object_list
        