#!/opt/anaconda2/envs/py360/bin/python
# -*- coding: utf-8 -*-

'''
    File name: insertMerraData.py
    Python Version: 3.6.0

    ##########   DATAPROCESSOR   ##########
    Ca

'''

__author__ = "Tiago Santos Buzato"
__version__ = "0.1"
__email__ = "tiago.buzato@climatempo.com.br"
__status__ = "Development"

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

import sys
import argparse
from datetime import datetime
from core.treats_NVDI_data import treats_NVDI_data
from configinit.setting import get_rootDir

parser = argparse.ArgumentParser(description='''''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-v", "--verbose", action='store_true', dest='verbose', help="Verbose", default=False)
parser.add_argument("-get", "--getting", action='store_true', dest='getting', help="Make download of ndvi data",
                    default=False)
parser.add_argument("-build", "--building", action='store_true', dest='building', help="Building only one image per month",
                    default=True)

args = parser.parse_args()

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[I] Inicio - {} ({}).".format(now, sys.argv[0]))

    treats_NVDI_data(building=args.building, getting=args.getting,  verbose=args.verbose)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[I] Fim - %s  (%s)." % (now, sys.argv[0]))
    sys.exit(0)
