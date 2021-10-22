from django.shortcuts import render
from django.http import HttpResponse
from store.models import Customer

# Create your views here.
def data(request):
    query_set = Customer.objects.filter(id__range=(0,5))
    
    # for customer in query_set:
    #  print(customer)
    return render(request,'index.html',{'customers': query_set})