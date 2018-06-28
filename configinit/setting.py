# -*- coding: utf-8 -*-

'''
    File name: settings.py
    Python Version: 3.6
    Configurações padrão
'''

__author__ = "Tiago S. Buzato"
__version__ = "0.1"
__email__ = "tiago.buzato@climatempo.com.br"
__status__ = "Development"

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

import os

def get_rootDir():
    # Referência do diretorio do projeto
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return BASE_DIR

def get_coordinates(region):
    #Coordinates registred
    COORDINATES = {
        'RS':{
            'upper_left':[-57.6422931, -27.0806650],
            'lower_right':[-49.6882581, -33.7528050]
        },'SP':{
            'upper_left': [-53.1096381, -19.7799250],
            'lower_right': [-44.1588231, -25.3138500]
        },
    }

    return COORDINATES[region]