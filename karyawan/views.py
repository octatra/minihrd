# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from karyawan.models import Karyawan
# Create your views here.
@login_required(login_url=settings.LOGIN_URL)
def profil(request):
    karyawan = Karyawan.objects.get(id=request.session['karyawan_id'])
    return render(request, 'profil.html', {"karyawan":karyawan})

# Create your views here.
