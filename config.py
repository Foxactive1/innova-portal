#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     16/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False