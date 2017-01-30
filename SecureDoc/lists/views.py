from django.shortcuts import render, get_object_or_404
from .models import List


# Create your views here.


def home(request):
    lists = List.objects.order_by('title')
    return render(request, "lists/home.html", {'lists': lists})


def list_detail(request, list_id):
    listdetails = get_object_or_404(List, pk=list_id)
    return render(request, 'lists/list_detail.html', {'list': listdetails})

