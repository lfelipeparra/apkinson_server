from django.conf.urls import  url
from . import views

urlpatterns = [
    url(r'^$',views.index, name='index' ),
    url(r'^CreatePacient/$',views.CreatePacient, name='CreatePacient' ),
    url(r'^NumberSession/$',views.NumberSession, name='NumberSession' ),
    url(r'^CreateMedicine/$',views.CreateMedicine, name='CreateMedicine' ),
    url(r'^UploadMovement/$',views.UploadMovement, name='UploadMovement' ),
    url(r'^UploadVideo/$',views.UploadVideo, name='UploadVideo' ),
    url(r'^LoadResults/$',views.LoadResults, name='LoadResults' ),
]
