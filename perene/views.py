from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse, Http404
from django.views import View

from django.shortcuts import render, redirect
from .models import Produto
from django.urls import reverse

# def index(request):
#     return HttpResponse("aaaa")

# class MainView(View):
#     def get(self, request):

        
def index(request):
  	return render(request, 'index.html') 

class Produto_view(View):
    def get(self, request):
        try:
            produtos =  Produto.objects.all().order_by('-validade')
        except Produto.DoesNotExist:
            raise Http404("Produto inexistente")
        contexto = {'produto' : produtos}
        return render(request, 'lista_produtos.html', contexto)

class Add_produto(View):
    def get(self, request):
        return render(request, 'inserir_produto.html')

    def post(self, request):
        nome = request.POST.get('nome')
        detalhe = request.POST.get('detalhe')
        validade = request.POST.get('validade')
        
        produto = Produto(nome=nome, detalhe=detalhe, validade=validade)
        produto.save()

        return redirect(reverse('lista_produtos'))    

    # def lista(request):
    #     produtos = Produto.objects.all().order_by('validade')
    #     return render(request, 'lista.html', {'produtos': produtos})

# def add_produto(request):
#     if request.method == 'POST':
#         nome = request.POST.get('nome')
#         detalhe = request.POST.get('detalhe')
#         validade = request.POST.get('validade')

#         if nome:
#             Produto.objects.create(
#                 nome=nome,
#                 detalhe=detalhe,
#                 validade=validade,
#                 # status=Produto.status
#             )
        
#             return redirect('lista_produtos')

    # return render(request, 'form.html')


