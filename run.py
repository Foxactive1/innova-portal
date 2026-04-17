#---------------------------------------------------------------------------------------
# Name:        run
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     16/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------
from app import create_app
import os
app = create_app()

app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true",
    )