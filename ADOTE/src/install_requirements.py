import os
import subprocess

requirements_file = os.environ.get('REQUIREMENTS_FILE', 'um-amigo-for-life/ADOTE/requirements.txt') 
subprocess.run(['pip', 'install', '-r', requirements_file])
