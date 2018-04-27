from django.forms import ModelForm
from django import forms
from kehadiran.models import Izin

class IzinForm(ModelForm):
    class Meta:
        model = Izin
        fields = ['jenis_kehadiran', 'waktu_mulai', 'waktu_berhenti', 'alasan']
        labels = {
            'jenis_kehadiran':"Jenis Izin",
            'waktu_mulai':'Waktu Mulai Izin',
            'waktu_berhenti':'Waktu Berhenti Izin',
            'alasan':'Alasan Izin',
        }
        error_messages = {
            'jenis_kehadiran': {
                'required': 'Anda harus memilih jenis izin'
            },
            'waktu_mulai' : {
                'required': "Anda harus menentukan tanggal izin dimulai"
            },
            'waktu_berhenti' : {
                'required': "Anda harus menentukan tanggal izin berakhir"
            },
            'alasan':{
                'required': "Alasan harus diisi agar dapat disetujui oleh HRD"
            }
        }
        widgets = {
            'alasan': forms.Textarea(attrs={ 'cols':50, 'rows': 10 })
        }