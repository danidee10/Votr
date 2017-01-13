import os
print('Running migrations if any...')
os.system('export FLASK_APP=Votr/votr.py && flask db stamp &&\
          flask db migrate && flask db upgrade')
