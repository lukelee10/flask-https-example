activate_this = '/var/www/smart/app/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/smart/app/')

from app import app as application

if __name__ == "__main__":
        application.run()