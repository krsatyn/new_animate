import json
import numpy as np
import scipy
import warnings


class Endoscope_Minimize():
    '''
    Класс для определения координат положения и углов наклона эндоскопа при помощи 
    метода scipy.optimize.minimize.
    '''
    def __init__(self, input: np.ndarray, output: np.ndarray, e_len: float):
        '''
        Parameters:
        - input: np.ndarray.
            Координаты [x, y, z] входного отверстия. 
        - output: np.ndarray.
            Координаты [x, y, z] выходного отверстия.   
        - e_len: float.
            Длина эндоскопа.
        '''
        self.d = e_len

        self.input = input
        self.output = output

        # Глубина отверстия. 
        self.hole_depth = np.sqrt(np.sum((output - input)**2))

    def distance(self, m: list, d1: float, d2: float):
        '''
        Евклидово расстояние между двумя точками. 

        Parameters:
        - m: list. 
            Неизвестная переменная. Координаты искомой точки.
        - d1: float.
            Расстояние от точки крепления эндоскопа до входного отверстия. 
        - d2: float.
            Расстояние от точки крепления эндоскопа до выходного отверстия.

        Returns:
        - tuple.
            Система уравнений для определения координат точки m положения эндоскопа. 
        '''
        return (np.sqrt(np.sum((m - self.input)**2)) - d1, 
                np.sqrt(np.sum((m - self.output)**2)) - d2)

    def find_point(self, d1: float, d2: float):
        '''
        Метод для поиска координат начального/конечного положения эндоскопа. 

        Parameters:
        - d1: float.
            Расстояние от точки крепления эндоскопа до входного отверстия. 
        - d2: float.
            Расстояние от точки крепления эндоскопа до выходного отверстия.

        Returns:
        - list. 
            Координаты [x, y, z] начального положения эндоскопа. 
        '''
        # Начальные значения.  
        m0 = np.mean([self.input, self.output], axis=0)
        
        # Целевая функция. Сумма квадратов расстояний от точки m до input / output. 
        obj_func = lambda x: np.sum(np.square(self.distance(x, d1, d2)))
        
        # Минимизация функции. 
        result = scipy.optimize.minimize(obj_func, m0)

        print(result.success)
        print(result.message)

        return result.x
    
    def find_angles(self, d1: float, d2: float):
        '''
        Метод для поиска углов наклона эндоскопа в сферической системе координат для каждого
        отверстия. Центр сферической системы координат находится в точке начала отверстия.

        Parameters:
        - d1: float.
            Расстояние от точки крепления эндоскопа до входного отверстия. 
        - d2: float.
            Расстояние от точки крепления эндоскопа до выходного отверстия.

        Returns:
        - list. 
            Координаты [x, y, z] начального положения эндоскопа и углы наклона [phi, psi]. 
        '''
        # Найдем координаты начального положения эндоскопа в абсолютной СК. 
        xm, ym, zm = self.find_point(d1, d2)

        # Координаты стартового отверстия относительно координат эндоскопа.
        x = self.input[0] - xm 
        y = self.input[1] - ym # y=0 - вырожденный случай. 
        z = self.input[2] - zm

        # Углы сферической системы координат. Определяют наклон эндоскопа. 
        # phi - горизонтальный угол (в плоскости X Y).
        # psi - вертикальный угол.
        try:
            # Для задней боковой поверхности. 
            if x < 0 and y == 0:
                phi = - np.pi/2
            # Для передней боковой поверхности. 
            elif x > 0 and y == 0:
                phi = np.pi/2
            # Для верхней полуплоскости X Y.
            elif x > 0 and y > 0:
                phi = np.arctan(x / y)
            elif x < 0 and y > 0:
                phi = np.arctan(x / y)
            # Для нижней полуплоскости X Y.
            else: 
                phi = np.arctan(x / y) + np.pi
            
            psi = np.arcsin(z / np.sqrt(x**2 + y**2 + z**2))
        
        # Обработка исключения в случае нулевого значения в знаменателе phi. 
        except RuntimeWarning:
            phi = 0
            psi = np.arcsin(z / np.sqrt(x**2 + y**2 + z**2))

        phi = np.rad2deg(phi)
        psi = np.rad2deg(psi)

        return xm, ym, zm, phi, psi
    

class Endoscope_Root(Endoscope_Minimize):
    '''
    Класс для определения координат положения и углов наклона эндоскопа при помощи 
    метода scipy.optimize.root.
    '''
    def __init__(self, input: np.ndarray, output: np.ndarray, e_len: float):
        
        Endoscope_Minimize.__init__(self, input, output, e_len)
        
        self.X1, self.Y1, self.Z1 = self.input 
        self.X2, self.Y2, self.Z2 = self.output

    def system_equations(self, m: list, d1: float, d2: float):
        '''
        Система уравнений [eq1, eq2, eq3, eq4, eq5] для определения координат начального положения 
        эндоскопа для каждого отверстия. 
        - eq1, eq2, eq3 задают положение прямой, проходящей через заданные точки начала 
        и конца отверстия.
        - eq4 характеризует удаленность искомой точки m от начала отверстия на величину, 
        равную длине эндоскопа.
        - eq5 характеризует удаленность искомой точки m от конца отверстия на величину, равную 
        сумме длины эндоскопа и глубины отверстия.  

        Parameters:
        - m: list. 
            Неизвестная переменная. Координаты искомой точки.
        - d1: float.
            Расстояние от точки крепления эндоскопа до входного отверстия. 
        - d2: float.
            Расстояние от точки крепления эндоскопа до выходного отверстия 

        Returns:
        - list. Система из пяти уравнений. 
        '''
        # Каноническое уравнение прямой в пространстве.
        eq1 = ((m[0] - self.X1) * (self.Y2 - self.Y1) - (m[1] - self.Y1) * (self.X2 - self.X1)) 
        eq2 = ((m[0] - self.X1) * (self.Z2 - self.Z1) - (m[2] - self.Z1) * (self.X2 - self.X1)) 
        eq3 = ((m[1] - self.Y1) * (self.Z2 - self.Z1) - (m[2] - self.Z1) * (self.Y2 - self.Y1)) 
        
        # Уравнения для определения расстояний до точки m.
        eq4 = np.sqrt((m[0] - self.X1)**2 + 
                      (m[1] - self.Y1)**2 + (m[2] - self.Z1)**2) - d1
        
        eq5 = np.sqrt((m[0] - self.X2)**2 + 
                      (m[1] - self.Y2)**2 + (m[2] - self.Z2)**2) - d2

        return [eq1, eq2, eq3, eq4, eq5]
    
    def find_point(self, d1: float, d2: float):
        '''
        Решает систему уравнений методом Левенберга — Марквардта с начальными условиями [1, 1, 1]. 
        
        Parameters:
        - d1: float.
            Расстояние от точки крепления эндоскопа до входного отверстия. 
        - d2: float.
            Расстояние от точки крепления эндоскопа до выходного отверстия.

        Returns:
        - list. Координаты [x, y, z] начального положения эндоскопа. 
        '''
        system = lambda x: self.system_equations(x, d1, d2)

        initial_guess = np.mean([self.input, self.output], axis=0)

        return scipy.optimize.root(system, initial_guess, method='lm').x


class SolutionsChecker(Endoscope_Minimize):
    '''
    Поиск решений для различных начальных условий. Проверка решений на равенство. 
    '''
    def get_start_coordinate(self):

        # Список начальных условий для численного решения системы. 
        starting_values = []

        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in [-1, 1]:
                    starting_values.append([i,j,k])

        # Поиск решений для разных начальных условий. 
        solutions = []
        for i, value in enumerate(starting_values):

            sol = scipy.optimize.root(self.start_coordinates_equations, value, method='lm').x
            solutions.append([round(coord,3) for coord in sol])
        
        # Проверка решений на взаимное равенство. 
        if all(sol==solutions[0] for sol in solutions) == True:
            print('ЕДИНСТВЕННОЕ РЕШЕНИЕ')
            print(solutions[0])
        else:
            print('РЕШЕНИЯ РАЗНЫЕ')


class GCodeMaker():

    def __init__(self, start_solution: list, end_solution: list, starting_height: int):
        
        self.X1, self.Y1, self.Z1, self.phi, self.psi = start_solution
        self.X2, self.Y2, self.Z2 = end_solution
        self.starting_height = starting_height

    def make_gcode(self, point_number: str):

        gcode_commands = [

            f'(Hole {point_number})',

            # Переход в абсолютную систему координат. Выбор метрической системы единиц.
            'G90 G21',         

            # Подъем эндоскопа на высоту starting_height.
            f'G0 X{self.X1} Y{self.Y1} Z{self.starting_height} F300', 

            # Выбор рабочей плоскости X-Y.
            'G17',                                
            # Поворот системы координат на угол R (против ч/c) вокруг точки (X, Y).
            f'G68 X{self.X1} Y{self.Y1} R{self.phi}',                              
            
            # Выбор рабочей плоскости Z-X.
            'G18',                                
            # Поворот системы координат на угол R (против ч/c) вокруг точки (X, Z).
            f'G68 X{self.X1} Z{self.Z1} R{self.psi}', 
            
            # Перемещение в точку X1 Y1 Z1.
            f'G0 X{self.X1} Y{self.Y1} Z{self.Z1} F300',  

            # Линейное перемещение в точку X2 Y2 Z2 со скоростью F в мм/мин.
            f'G1 X{self.X2} Y{self.Y2} Z{self.Z2} F100',  
                                      
            # Возврат в точку X1 Y1 Z1 со скоростью F в мм/мин.
            f'G1 X{self.X1} Y{self.Y1} Z{self.Z1} F300',  
            
            # Отмена поворота системы координат.
            'G69'                              
        ]
        return gcode_commands
    
    def make_terminal_command(self, point_number: str):

        terminal_commands = [

        f"// Hole {point_number}",

        "// Подъем эндоскопа на высоту starting_height",
        f"ComSendmacro('G1 Z{self.starting_height} F2000$0A');",

        "// Поворот эндоскопа линзой вниз",
        "ComSendmacro('G1 Q-91 F2000$0A');",

        "Delay(3000);",

        "// Поворот головки (против ч/c) в плоскости (X, Y)",
        f"ComSendmacro('G1 W{self.phi} F2000$0A');",

        "Delay(3000);",

        "// Поворот головки (против ч/c) в плоскости (X, Z)",
        f"ComSendmacro('G1 Q{self.psi} F2000$0A');",

        "Delay(3000);",

        "// Перемещение в точку X1 Y1 Z1 (старт)",
        f"ComSendmacro('G1 X{self.X1} Y{self.Y1} F200$0A');",
        f"ComSendmacro('G1 Z{self.Z1} F2000$0A');",

        "Delay(5000);"

        # "// Перемещение в точку X2 Y2 Z2 (финиш)",
        # f"ComSendmacro('G1 X{self.X2} Y{self.Y2} F200$0A');",
        # # f"ComSendmacro('G1 Z{self.Z2} F2000$0A');",

        # "// Возврат в точку X1 Y1 Z1",
        # f"ComSendmacro('G1 X{self.X1} Y{self.Y1} F200$0A');",
        # f"ComSendmacro('G1 Z{self.Z1} F2000$0A');",

        "// ........................................................."

        ]

        return terminal_commands
    
    def make_light_calibration(self):

        calibration = [

        "// КАЛИБРОВКА (Q W) ",

        "ComSendmacro('G1 X0 Y0 Z0$0A');",

        "Delay(10000);",

        "// Замыкание концевиков, обнуление координат ",
        "ComSendmacro('G1 Q-999 O$0A');",
        "ComSendmacro('G1 W-999 O$0A');",

        "Delay(5000);",

        "// Замыкание концевиков, обнуление координат ",
        "ComSendmacro('G1 Q90$0A');",
        "ComSendmacro('G1 W90$0A');",

        "Delay(5000);",

        "// Замыкание концевиков, обнуление координат ",
        "ComSendmacro('G1 Q-999 O$0A');",
        "ComSendmacro('G1 W-999 O$0A');",

        "Delay(5000);",

        "// Стартовое положение ",
        "ComSendmacro('G1 Q31$0A');",
        "ComSendmacro('G1 W60$0A');",

        "Delay(5000);",

        "// Обнуление координат стартового положения ",
        "ComSendmacro('G10$0A');",

        "// ........................................................."

        ]
        return calibration
    
    def make_full_calibration(self):

        calibration = [

        "// КАЛИБРОВКА (X Y Z) ",

        "// Замыкание концевиков, обнуление координат ",
        "ComSendmacro('G1 Z999 O$0A');",
        
        "Delay(20000);",

        "ComSendmacro('G1 Y-999 O$0A');",
        
        "Delay(20000);",

        "ComSendmacro('G1 X-999 O$0A');",

        "Delay(20000);",

        "// Стартовое положение ",
        "ComSendmacro('G1 Z-263$0A');",

        "Delay(20000);",

        "ComSendmacro('G1 Y488$0A');",

        "Delay(20000);",

        "ComSendmacro('G1 X442$0A');",

        "Delay(20000);",

        "// Обнуление координат стартового положения ",
        "ComSendmacro('G10$0A');",

        "// ........................................................."
        ]
        return calibration


    def make_json(self, point_number: str):
        
        points = {}

        points['hole_' + point_number]['start'] = {
            'X': self.X1, 'Y': self.Y1, 'Z': self.Z1, 'phi': self.phi, 'psi': self.psi}
        
        points['hole_' + point_number]['end'] = {'X': self.X2, 'Y': self.Y2, 'Z': self.Z2}

        return points


if __name__ == '__main__':

    warnings.filterwarnings("error")

    # Имя JSON файла с координатами отверстий.  сг
    name = input('Введите название JSON файла с координатами: ')

    with open('src/json/' + name + '.json') as f:
        coordinates = json.load(f)

    # Длина эндоскопа.
    e_len = coordinates['endoscope_length']

    # Высота стартовой плоскости относительно нулевой координаты. 
    starting_height = coordinates['starting_height']

    points = {}

    # Счетчик измерений. 
    n = 0

    for point in coordinates['holes']:

        # Номер точки.
        *other, point_number = point.split('_')
        
        # Словари с координатами точек start и end. 
        input_point = coordinates['holes'][f'{point}']['start']
        output_point = coordinates['holes'][f'{point}']['end']

        # Массивы с координатами точек start и end.
        input = np.array(list(input_point.values()))
        output = np.array(list(output_point.values()))

        print(input)
        print(output)

        endoscope = Endoscope_Root(input, output, e_len)
        
        # Начальное расстояния от точки крепления эндоскопа до точек start и end.
        d1 = endoscope.d
        d2 = endoscope.d + endoscope.hole_depth
        
        # Координаты начального положения точки крепления эндоскопа и углы его наклона. 
        start = [round(x,3) for x in endoscope.find_angles(d1, d2)]
        print('Отверстие №' + point_number, '(начало)', start)

        # Конечное расстояния от точки крепления эндоскопа до точек start и end.
        d1 = endoscope.d - endoscope.hole_depth
        d2 = endoscope.d
        
        # Координаты конечного положения точки крепления эндоскопа. 
        stop = [round(x,3) for x in endoscope.find_point(d1, d2)]
        print('Отверстие №' + point_number, '(конец)', stop)
        print('..................................................')

        gcode = GCodeMaker(start, stop, starting_height)

        # Запись файла gcode программы.
        # gcode_commands = gcode.make_gcode(point_number)

        # with open(name + '.nc', 'a') as file:
        #     for command in gcode_commands:
        #         file.write(command + '\n')
        #     file.write('M30')

        # Запись файла с командами для терминала. 
        terminal_commands = gcode.make_terminal_command(point_number)

        light_calibration = gcode.make_light_calibration()

        full_calibration = gcode.make_full_calibration()

        with open('result/commands_sequence_for_' + name + '.tsc', 'a') as file:
            
            # Калибровка по X Y Z в начале цикла.
            if n == 0:
                for command in full_calibration:
                    file.write(command + '\n')
            # Калибровка по X Y Z через каждые 10 измерений.
            if n == 10:
                for command in full_calibration:
                    file.write(command + '\n')
                n = 1
            # Калибровка по Q W перед каждым измерением. 
            for command in light_calibration:
                file.write(command + '\n')
            # Проход по отверстию
            for command in terminal_commands:
                file.write(command + '\n')
        # Приращение счетчика. 
        n += 1


        # Запись координат в JSON файл.  
        points['hole_' + point_number] = {}
        # Координаты начала.
        points['hole_' + point_number]['start'] = {
            'X': start[0],
            'Y': start[1],
            'Z': start[2], 'phi': start[3], 'psi': start[4]}
        # Координаты конца. 
        points['hole_' + point_number]['end'] = {'X': stop[0], 'Y': stop[1], 'Z': stop[2]}

    with open('result/endoscope_coordinates_for_' + name + '.json', 'w') as file:
        json.dump(points, file, indent=4)    
        

        # Проверка. 
        # cheker = SolutionsChecker(start_coordinates, end_coordinates, e_len) 
        # cheker.get_start_coordinate()   
