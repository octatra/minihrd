# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from karyawan.models import Karyawan
from kehadiran.models import Kehadiran, Izin
from kehadiran.forms import IzinForm

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from django.views.generic import View

# Create your views here.
class DaftarHadir(View):
    def get(self, request):
        template_name = "new/daftar_hadir.html"
        hadir = Kehadiran.objects.all()

        if 'bulan' and 'tahun' in request.GET:
            tahun = request.GET['tahun']
            bulan = request.GET['bulan']
            hadir = Kehadiran.objects.filter(waktu__year=tahun, waktu__month=bulan, karyawan__id=request.session['karyawan_id'])

        data = {
            'daftar_hadir' : hadir,
        }
        return render(request, template_name, data)


#@login_required(login_url=settings.LOGIN_URL)
#def daftar_hadir(request):
#    daftar_hadir = None
#    bulan = None
#    tahun = None
#    if request.method == 'POST':
#        bulan = request.POST['bulan']
#        tahun = request.POST['tahun']
#        daftar_hadir = Kehadiran.objects.filter(waktu__year=tahun, waktu__month=bulan, karyawan__id=request.session['karyawan_id'])

#    return render(request, 'new/daftar_hadir.html', {'daftar_hadir':daftar_hadir,'bulan':bulan,'tahun':tahun})
# Create your views here.
# @login_required(login_url=settings.LOGIN_URL)
# def pengajuan_izin(request):
#     if request.method == 'POST':
#         form_data = request.POST
#         form = IzinForm(form_data)
#         if form.is_valid():
#             izins = Izin(
#                     karyawan = Karyawan.objects.get(id=request.session['karyawan_id']),
#                     jenis_kehadiran = request.POST['jenis_kehadiran'],
#                     waktu_mulai = request.POST['waktu_mulai'],
#                     waktu_berhenti = request.POST['waktu_berhenti'],
#                     alasan = request.POST['alasan'],
#                     disetujui = False,
#                 )
#             izins.save()
#             return redirect('/')
#     else:
#         form = IzinForm()

#     return render(request, 'new/tambah_izin.html', {'form':form})
   
class PengajuanIzinView(View):
    def get(self, request):
        form = IzinForm(request.POST)
        return render(request, 'new/tambah_izin.html', {'form':form})

    def post(self, request):
        form = IzinForm(request.POST)
        if form.is_valid():
            izins = Izin(
                    karyawan = Karyawan.objects.get(id=request.session['karyawan_id']),
                    jenis_kehadiran = request.POST['jenis_kehadiran'],
                    waktu_mulai = request.POST['waktu_mulai'],
                    waktu_berhenti = request.POST['waktu_berhenti'],
                    alasan = request.POST['alasan'],
                    disetujui = False,
                )
            izins.save()
            return redirect('/')
        else:
            return self.get(request)



#@login_required(login_url=settings.LOGIN_URL)
class DaftarIzin(View):
    def get(self, request):
        template_name = "new/daftar_izin.html"
        izins = Izin.objects.all()
        data = {
            'daftar_izins' : izins,
            'form' : Izin.objects.filter(karyawan__id=request.session['karyawan_id']).order_by('-waktu_mulai'),
        }
        return render(request, template_name, data)

#def daftar_izins(request):
#    daftar_izins = Izin.objects.filter(karyawan__id=request.session['karyawan_id']).order_by('-waktu_mulai')

#    paginator = Paginator(daftar_izins, 5)
#    page = request.GET.get('page')
#    try:
#        daftar_izins = paginator.page(page)
#    except PageNotAnInteger:
#        daftar_izins = paginator.page(1)
#    except EmptyPage:
#        daftar_izins = paginator.page(paginator.num_pages)

#    return render(request, 'new/daftar_izin.html', {'daftar_izins':daftar_izins})
@login_required(login_url=settings.LOGIN_URL)
def tampil_grafik(request, bulan, tahun):
    temp_chart_data = []
    daftar_hadir = Kehadiran.objects.filter(waktu__year=tahun, waktu__month=bulan, karyawan__id=request.session['karyawan_id'])
    print daftar_hadir
    temp_chart_data.append({ "x":"hadir", "a":daftar_hadir.filter(jenis_kehadiran='hadir').count() })
    temp_chart_data.append({ "x":"izin", "a":daftar_hadir.filter(jenis_kehadiran='izin').count() })
    temp_chart_data.append({ "x":"alpa", "a":daftar_hadir.filter(jenis_kehadiran='alpa').count() })
    temp_chart_data.append({ "x":"cuti", "a":daftar_hadir.filter(jenis_kehadiran='cuti').count() })

    chart_data = json.dumps({"data":temp_chart_data})               
    print chart_data
    return render(request, 'new/tampil_grafik.html', {'chart_data':chart_data, 'bulan':bulan, 'tahun':tahun})

@login_required(login_url=settings.LOGIN_URL)
def cetak_daftar_hadir(request, bulan, tahun):
    # pengaturan respon berformat pdf
    filename = "daftar_hadir_" + str(bulan) + "_" + str(tahun)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.pdf"'

    # mengambil daftar kehadiran dan mengubahnya menjadi data ntuk tabel
    data = Kehadiran.objects.filter(waktu__year=tahun, waktu__month=bulan, karyawan__id=request.session['karyawan_id'])
    table_data = []
    table_data.append([ "Tanggal", "Status" ])
    for x in data:
        table_data.append([ x.waktu, x.jenis_kehadiran ])


    # membuat dokumen baru
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()

    # pengaturan tabel di pdf
    table_style = TableStyle([
                               ('ALIGN',(1,1),(-2,-2),'RIGHT'),
                               ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('VALIGN',(0,0),(0,-1),'TOP'),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ])
    kehadiran_table = Table(table_data, colWidths=[doc.width/4.0]*2)
    kehadiran_table.setStyle(table_style)

    # mengisi pdf
    content = []
    content.append(Paragraph('Daftar Kehadiran %s/%s' % (bulan, tahun), styles['Title']))
    content.append(Spacer(1,12))
    content.append(Paragraph('Berikut ini adalah hasil rekam jejak kehadiran Anda selama bulan %s tahun %s:' % (bulan, tahun), styles['Normal']))
    content.append(Spacer(1,12))
    content.append(kehadiran_table)
    content.append(Spacer(1,36))
    content.append(Paragraph('Mengetahui, ', styles['Normal']))
    content.append(Spacer(1,48))
    content.append(Paragraph('Mira Kumalasari, Head of Department PT. Ngabuburit Sentosa Sejahtera. ', styles['Normal']))

    # menghasilkan pdf untk di download
    doc.build(content)
    return response