import os
print('Running migrations if any...')
os.system('export FLASK_APP=Votr/votr.py && flask db stamp -d Votr/migrations &&\
flask db migrate -d Votr/migrations && flask db upgrade -d Votr/migrations')
