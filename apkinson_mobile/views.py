from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseGone, HttpResponseNotFound
from datetime import datetime
import re
import os
from django.views.decorators.csrf import csrf_exempt
from .models import Paciente, Medicine, Results
from django.conf import settings
import subprocess
import threading
import shutil
from apkinson_mobile.tasks import computeWER


@csrf_exempt
def index(request):
    if request.method == "POST":
        # print(request.POST)
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            obj = Paciente.objects.get(id_name=request.POST['id_name'])
            number_sessions_send=int(request.POST['number_session'])
            principal_dir=settings.MEDIA_ROOT+obj.id_name+'/'
            if not os.path.isdir(principal_dir+'AUDIOS'):
                os.makedirs(principal_dir+'AUDIOS')
            for key in request.POST.keys():
                if key != 'id_name' and key != 'number_session': # this is not a good enough check
                    audio64=request.POST[key].decode('base64')
                    name=re.sub(r'.*(Frase \d{1,}).*',r'\1',key).replace(' ','_')
                    f=open(principal_dir+'AUDIOS/'+name+".wav","wb")

                    f.write(audio64)
                    f.close()
            # start wer computation here and return the key, so the client can ask for results
            result = computeWER.delay(int(request.POST['id_name']))
            return HttpResponse(result.id)
        else:
            return HttpResponse('El paciente no ha sido creado en el servidor')
    else:
        return HttpResponse('No POST method')


@csrf_exempt
def CreatePacient(request):
    if request.method == "POST":
        if(Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists()):
            return HttpResponse('Este paciene ya existe')
    else:
        birthday=datetime.strptime(request.POST['birthday'][4:10]+' '+request.POST['birthday'][-4:], '%b %d %Y')
        db_register= Paciente(name=request.POST['name_pacient'],id_name=request.POST['id_name'],gender=request.POST['gender'],birthday=birthday,smoker=bool(request.POST['smoker']),year_diag=int(request.POST['year_diag']),other_disorder=request.POST['other_disorder'],educational_level=int(request.POST['educational_level']),weight=request.POST['weight'],height=int(request.POST['height']),session_count=0)
        db_register.save()
        os.mkdir('media/'+request.POST['id_name'])
        return HttpResponse('El paciente ha sido creado')

    return HttpResponse('')


@csrf_exempt
def NumberSession(request):
    if request.method == "POST":
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            obj= Paciente.objects.get(id_name=request.POST['id_name'])
            return HttpResponse(str(obj.session_count))
        else:
            return HttpResponse(str(1))


@csrf_exempt
def CreateMedicine(request):
    if request.method == "POST":
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            number_medicine=int(request.POST['number_medicine'])
            count_medicine=0
            for medicine in range(0,number_medicine):
                if not(Medicine.objects.filter(id_name=int(request.POST['id_name'])).exists() and Medicine.objects.filter(medicinename=request.POST['name_medicine'+str(medicine)]).exists()and Medicine.objects.filter(dose=int(request.POST['dose'+str(medicine)])).exists()and Medicine.objects.filter(intaketime=int(request.POST['intaketime'+str(medicine)])).exists()):
                    print(Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists())

                    db_medicine= Medicine(medicinename=request.POST['name_medicine'+str(medicine)],id_name=request.POST['id_name'],dose=int(request.POST['dose'+str(medicine)]),intaketime=int(request.POST['intaketime'+str(medicine)]))
                    db_medicine.save()
                    count_medicine=count_medicine+1

            return HttpResponse('Se almacenaron '+str(count_medicine)+' medicinas nuevas')
        else:
            return HttpResponse('El paciente no ha sido creado en el servidor')


@csrf_exempt
def UploadMovement(request):
    if request.method == "POST":
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            obj= Paciente.objects.get(id_name=request.POST['id_name'])
            number_sessions_send=int(request.POST['number_session'])
            principal_dir=settings.MEDIA_ROOT+obj.id_name+'/'
            if not os.path.isdir(principal_dir+'MOVEMENTS'):
                os.makedirs(principal_dir+'MOVEMENTS')
            for key in request.POST.keys():
                        if key != 'id_name' and key != 'number_session':
                            Move64=request.POST[key].decode('base64')
                            f=open(principal_dir+'MOVEMENTS/'+key,"wb")

                            f.write(Move64)
                            f.close()
        else:
            return HttpResponse('El paciente no ha sido creado en el servidor')


@csrf_exempt
def UploadVideo(request):
    if request.method == "POST":
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            obj= Paciente.objects.get(id_name=request.POST['id_name'])
            number_sessions_send=int(request.POST['number_session'])
            principal_dir=settings.MEDIA_ROOT+obj.id_name+'/'
            if not os.path.isdir(principal_dir+'VIDEOS'):
                os.makedirs(principal_dir+'VIDEOS')
            for key in request.POST.keys():
                        if key != 'id_name' and key != 'number_session':
                            Video64=request.POST[key].decode('base64')
                            f=open(principal_dir+'VIDEOS/'+key,"wb")

                            f.write(Video64)
                            f.close()
            return HttpResponse('Datos enviados')
        else:
            return HttpResponse('El paciente no ha sido creado en el servidor')


def saveWER(id_name):
    obj = Paciente.objects.get(id_name=id_name)
    principal_dir=settings.MEDIA_ROOT+obj.id_name+'/'
    if os.path.isdir(settings.MEDIA_ROOT+obj.id_name+'/AUDIOS'):
        for i in os.listdir(settings.MEDIA_ROOT+obj.id_name+'/AUDIOS'):
            if 'Frase' in i:
                print(i)
                date=str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
                wd='/home/luisparra/Documentos/gita/Apkinson/server/apkinson_server/intelligibility'
                data=principal_dir+'DATA'+date
                compute_wer='compute-wer --text --mode=present ark:ref_text ark:'+data+'/transcript'
                process = subprocess.Popen('./transcript.sh '+data+'/../AUDIOS '+data+';'+compute_wer+'>'+data+'/wer',cwd=wd,shell=True).wait()
                with open(data+'/wer') as f:
                    wer=f.read()
                    wer=re.findall(r'WER (\d{1,}.\d{1,})',wer)[0]
                    print(wer)
                    if Results.objects.filter(id_name=id_name).exists():
                        result = Results.objects.get(id_name=obj.id_name)
                        result.WER = wer
                        result.save(update_fields=['WER'])
                    else:
                        result = Results(id_name=obj.id_name,WER=wer)
                        result.save()
                shutil.rmtree(data, ignore_errors=True)
                break


@csrf_exempt
def LoadResults(request):
    if request.method == "POST": # why post and not get, you are getting(loading) a result
        if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
            t1 = threading.Thread(target=saveWER, args=(int(request.POST['id_name']),))
            t1.start()
        if Results.objects.filter(id_name=int(request.POST['id_name'])).exists():
            obj= Results.objects.get(id_name=request.POST['id_name'])
            return HttpResponse(obj.WER)
        else:
            return HttpResponse("0")


######### EXAMPLE IMPLEMENTATION STARTS HERE #################
# the task is startet in the index method
# Example with your implementation, did only change to make it a workflow, would go about it a bit differently, especially not using post
from celery.result import AsyncResult
from apkinson_server import celery_app as capp
@csrf_exempt
def LoadAsyncResults(request):
    if request.method == "POST": # why post and not get, you are getting(loading) a result, if you want to get it from queue you need to send the task id along
        id_name = int(request.POST['id_name'])
        if Paciente.objects.filter(id_name=id_name).exists():
            task_id = request.POST['task_id']
            result = AsyncResult(task_id, app=capp)
            if result.ready():
                if result.successful():
                    if Results.objects.filter(id_name=int(request.POST['id_name'])).exists():
                        obj = Results.objects.get(id_name=request.POST['id_name'])
                        result.forget()
                        return HttpResponse(obj.WER)
                    else:
                        return HttpResponseNotFound(f'{id_name}, {task_id}')
                else:
                    result.forget() # here you could return error details, would not recommend though
                    return HttpResponseGone('Computation went wrong, please try to resubmit the data for computation')
            else:
                HttpResponse(f'Computation for {task_id} not ready, ask again later')
        else:
            return HttpResponseNotFound(id_name)

######### EXAMPLE IMPLEMENTATION ENDS HERE #################


######### DUMMY IMPLEMENTATION FOR HELLO WORLD EXAMPLE HERE #################
from apkinson_mobile.tasks import run_hello_sh
@csrf_exempt
def hello(request):
    if request.method == 'GET':
        result = run_hello_sh.delay()
        return HttpResponse(result.id)
    else:
        return HttpResponseNotAllowed()


@csrf_exempt
def get_hello(request, task_id):
    if request.method == 'GET':
        result = AsyncResult(task_id, app=capp)
        # should look up result in normal database first, otherwise this is just one shot
        if result.ready():
            if result.successful():
                res_val = result.get(1.0)
                # write shit where it belongs
                result.forget()
                return HttpResponse(res_val)
            else:
                print('Something went wrong, please resubmit request')
                result.forget()
                return HttpResponseGone(f'Computation of {task_id} failed, please resubmit request and/or data')
        else:
            return HttpResponse(f'Result for {task_id} not available, please try again later')

######### DUMMY IMPLEMENTATION ENDS HERE #################
