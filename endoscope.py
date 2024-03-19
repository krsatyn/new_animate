#endoscope.py

import ursina
import numpy as np
import json

from hole_center import Hole_center

class Endoscope():
    
    def __init__(self, 
                 json_path:str=None,                # Путь до json файла
                 input_coordinate_dict:dict=None,   # Словарь координат используется в случае если подается не json а заготовленный словарь 
                 diameter_endoscope:float=5.0,      # Диаметр эндоскопа
                 len_endoscope=300,                 # Длина энадоскопа
                 point_objects_list:list=None       # Точки конца отверстия
                ) -> None:
        
        self.json_path = json_path                         # Путь до json файла
        self.input_coordinate_dict = input_coordinate_dict # Входной словарь (в случае отсуствия json)
        self.radius_endoscope = diameter_endoscope / 2     # Диаметр эндоскопа
        self.len_endoscope = len_endoscope                 # Длина эндоскопа
        self.point_objects_list = point_objects_list       # Список обьектов
        
    def update():
        print(1)
    
    # Распоковщик json файла
    def unpucking_json(self,) -> dict:
        """
        Если подаётся словарь то он должен иметь структуру приведенную ниже

        !!! len(input_coordinate_dict[start]) и len(input_coordinate_dict[end]) должно быть равным иначе произойдет ошибка!!!
        
        dict{
                "start":[{'X':float, 'Y':float,'Z':float},],
                "end":  [{'X':float, 'Y':float,'Z':float},]
        }
        
        """
        start_coordinates = []
        end_coordinates   = []
        phi_angles = []
        psi_angles = []
        
        
        if self.json_path is not(None):
            
            #Считывание с json файла    ян
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
        
        phi_list = []
        psi_list = []
        
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
            
            phi_list.append(point_dict['start'][index_hole]['phi'])
            psi_list.append(point_dict['start'][index_hole]['psi'])   
            
        self.vec_3_point_dict = vec_3_point_dict
        self.hole_counter = len(point_dict['start'])
        self.pints_counter = len(point_dict['start']) * 2 # так как у отверстия есть вход и выход
        
        self.phi_list = phi_list
        self.psi_list = psi_list
        
    # Получение координат точек c point_objects_list
    def get_point_objects_coordinate(self,) -> None:
        point_objects_list = self.point_objects_list
        
        # тестовый прототип
        if point_objects_list == None:
            point_objects_list = {                                                                         # Список обьектов
                     'start':[ursina.Entity(model='sphere', position=(0,0,0), color=ursina.color.green),], # Точки начала отверстий 
                     'end': [ursina.Entity(model='sphere', position=(0,20,0), color=ursina.color.red),]}   # Точки конца отверстий
                    
        
        
        coordinate_point_dict = {'start':[], 'end':[]}

        for index_hole in range(self.hole_counter):
                #print(type(point_objects_list['start'][index_hole]), "<============================================================================================================================")
                start_coordinate = point_objects_list[0]['start'][index_hole].get_position() # Получение координаты расположение точки старта
                coordinate_point_dict['start'].append(start_coordinate) 
                
                end_coordinate = point_objects_list[0]['end'][index_hole].get_position()     # Получение координаты расположение точки конца
                coordinate_point_dict['end'].append(end_coordinate)
        
        self.coordinate_point_dict = coordinate_point_dict
        
        
    # Создание эндоскопа (длинй 300)
    def create_endoscope(self, start_coordinate:dict=ursina.Vec3((0,0,0)),):
    
        
        # Создание обьекта эндоскопа
        endoscope = ursina.Entity(model=ursina.Cylinder(resolution=8,                         # Количество граней
                                                        radius=self.radius_endoscope,         # Конечная координата:tuple(x,y,z)
                                                        height=-self.len_endoscope,            # Длина обьекта
                                                        ),
                                                        color=ursina.color.orange,        
                                                        position=(start_coordinate))          # Позиция  начала
        
        
        endoscope_list = []
        endoscope_list.append(endoscope)
        endoscope_list.append(ursina.Entity(model='sphere', scale=5,  position=(start_coordinate), color=ursina.color.pink))
        
        return endoscope_list
    
    # Перемещение эндоскопа на заданную позицию
    def moving_endoscope_to_input_coordinate(self,
                                            endoscope:ursina.Entity,  
                                            phi:float=0,
                                            psi:float=90,
                                            start_coordinate = (0,0,0),
                                            end_coordinate = (0,0,0),):
        
        #endoscope = endoscope.rotate_x(alpha_angle)
        endoscope.world_rotation = (phi,0,psi)
        endoscope.world_position = start_coordinate
        endoscope.animate_position(end_coordinate, duration=5, loop=True)

        #return endoscope
        
    
    # Основная функция
    def main(self,):
        
        #Список всех обьектов    
        object_list = []
        
        # распаковываем json
        self.unpucking_json()
        
        # Конвертация координат под формат ursina.Vec3
        self.convertor_dict_coordinate_to_Vec3_coordinate()
        
        # Получение координат точек для дальнейшего их соответсвия
        self.get_point_objects_coordinate()
        endoscope = self.create_endoscope()
        
        endoscope[0] = self.moving_endoscope_to_input_coordinate(endoscope=endoscope[0], 
                                                                 start_coordinate=self.vec_3_point_dict['start'][-1], 
                                                                 end_coordinate=self.vec_3_point_dict['end'][-1],
                                                                 phi=self.psi_list[-1],
                                                                 psi=self.phi_list[-1])
        
    
        return endoscope