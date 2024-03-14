#endoscope.py

import ursina
import numpy
import json

class Endoscope():
    def __init__(self, json_path:str=None, ) -> None:
        self.json_path = json_path
    
    def create_endoscope(self):
        return ursina.Entity(model=ursina.Cylinder()) 
    
    def main():
        return 0