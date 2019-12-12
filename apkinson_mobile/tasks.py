import os
import shutil
import re
from datetime import datetime
from django.conf import settings
from .models import Results
from celery import shared_task
import subprocess


@shared_task
def run_hello_sh():
    from random import randint
    wd = os.getcwd()
    subprocess.call([f'{wd}/hello_world.sh', f'{randint(0, 300)}'], shell=True)
    with open(f'{wd}/hello_file.txt') as f:
        lines = f.readlines()
    return lines[0]


@shared_task
def computeWER(id_name):
    principal_dir = settings.MEDIA_ROOT + id_name + '/'
    if os.path.isdir(settings.MEDIA_ROOT + id_name + '/AUDIOS'):
        for i in os.listdir(settings.MEDIA_ROOT + id_name + '/AUDIOS'):
            if 'Frase' in i:
                print(i)
                date = str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
                wd = '/home/luisparra/Documentos/gita/Apkinson/server/apkinson_server/intelligibility'
                data = principal_dir + 'DATA' + date
                compute_wer = 'compute-wer --text --mode=present ark:ref_text ark:' + data + '/transcript'
                process = subprocess.Popen(
                    './transcript.sh ' + data + '/../AUDIOS ' + data + ';' + compute_wer + '>' + data + '/wer', cwd=wd,
                    shell=True).wait()
                with open(data + '/wer') as f:
                    wer = f.read()
                    wer = re.findall(r'WER (\d{1,}.\d{1,})', wer)[0]
                    print(wer)
                    if Results.objects.filter(id_name=id_name).exists():
                        result = Results.objects.get(id_name=id_name)
                        result.WER = wer
                        result.save(update_fields=['WER'])
                    else:
                        result = Results(id_name=id_name, WER=wer)
                        result.save()
                shutil.rmtree(data, ignore_errors=True)
                break
