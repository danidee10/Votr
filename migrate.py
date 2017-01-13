"""This script is a migration helper for deployments on gitlab
If you want to run migrations use flask db xxx instead of this file, if you use
this file outside the projects root directory, you'll get unexpected
results
"""

import os
print('Running migrations if any...')
os.system('export FLASK_APP=Votr/votr.py && flask db stamp -d Votr/migrations &&\
flask db migrate -d Votr/migrations && flask db upgrade -d Votr/migrations')
