from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from datetime import datetime
import base64
import re
import wave
import os
import subprocess
from django.views.decorators.csrf import csrf_exempt
from .models import Paciente, Medicine, Results
from django.conf import settings
import subprocess
import threading
import shutil

@csrf_exempt
def index(request):
	if request.method == "POST":
		#print(request.POST)
		
		if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
			obj = Paciente.objects.get(id_name=request.POST['id_name'])
			number_sessions_send=int(request.POST['number_session'])
			principal_dir=settings.MEDIA_ROOT+obj.id_name+'/'
			if not os.path.isdir(principal_dir+'AUDIOS'):
				os.makedirs(principal_dir+'AUDIOS')
			for key in request.POST.keys():
				if key != 'id_name' and key != 'number_session':
					audio64=request.POST[key].decode('base64')
					name=re.sub(r'.*(Frase \d{1,}).*',r'\1',key).replace(' ','_')
					f=open(principal_dir+'AUDIOS/'+name+".wav","wb")

					f.write(audio64)
					f.close()
			return HttpResponse('Datos enviados')# Create your views here.
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
	if request.method == "POST":
		if Paciente.objects.filter(id_name=int(request.POST['id_name'])).exists():
			t1 = threading.Thread(target=saveWER, args=(int(request.POST['id_name']),))
			t1.start()
		if Results.objects.filter(id_name=int(request.POST['id_name'])).exists():
			obj= Results.objects.get(id_name=request.POST['id_name'])
			return HttpResponse(obj.WER)
		else:
			return HttpResponse("0")


