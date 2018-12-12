import os
import sys
from logging import Formatter, FileHandler

APP_HOME = r"/home/winddori/dev/rfwatcher/api"


activate_this = os.path.join("/home/winddori/dev/rfwatcher/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, APP_HOME)
os.chdir(APP_HOME)

from api import app

handler = FileHandler("app.log")
handler.setFormatter(Formatter("[%(asctime)s | %(levelname)s] %(message)s"))
app.logger.addHandler(handler)
application = app

