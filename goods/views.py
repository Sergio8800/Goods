from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView
from django.views.generic.base import View
from .models import *
from .forms import *


class GoodsList(View):
    def get(self, request):
        goods = Car.objects.all()
        category = Category.objects.all()
        return render(request, 'goods/index.html', {'goods_list': goods, 'category': category})
    #### NEW Class ListView   ##########
    # model = Car
    # queryset = Car.objects.all()
    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args,**kwargs)
    #     context["category"] = Category.objects.all()
    #     context["goods_list"] = Car.objects.all()
    #
    #     return context

class AddCar_View(LoginRequiredMixin, View):
    login_url = reverse_lazy('login_my')

    def get(self, request):
        template = 'goods/add_car.html'
        form = AddCar()
        contex = {
            'list_car': Car.objects.all().order_by('id'),
            'form': form
        }

        return render(request, template, context=contex)

    def post(self, request):
        success = False
        form = AddCar(request.POST, request.FILES)
        author = self.request.user

        if form.is_valid():
            form = form.save(commit=False)
            form.author = author
            form.save()

        # return redirect('/')
        else:
            print("hhhhhhhhhhhh")
        return render(request, 'goods/add_car.html', context={
            'list_car': Car.objects.all().order_by('id'),
            'success': success}
                      )


########### метод инициализации формы через класс UpdateView #######
# def get_form_kwargs(self):
#     """Return the keyword arguments for instantiating the form."""
#     kwargs = super().get_form_kwargs()
#     print(kwargs)
#     if hasattr(self, 'object'):
#         kwargs.update({'instance': self.object})
#     return kwargs

############# переопределяем метод для записи Пользователя в БД ######
# def form_valid(self, form):
#     """If the form is valid, save the associated model."""
#     self.object = form.save(commit=False)
#     self.object.author = self.request.user
#     self.object.save()
#     return super().form_valid(form)
# class LoginRequiredMixin(AccessMixin):
#     """Verify that the current user is authenticated."""
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         return super().dispatch(request, *args, **kwargs)

class Update_Car_View(LoginRequiredMixin, View):
    def get(self, request, pk):
        template = 'goods/add_car.html'
        form = AddCar(instance=Car.objects.get(pk=pk))
        obj = Car.objects.get(pk=pk)
        author = self.request.user
        author_real = obj.author
        print(author_real)

        if author == author_real or request.user.is_superuser:

            update = True
            contex = {
                'list_car': Car.objects.all().order_by('id'),
                'form': form,
                'update': update,
                'author': author,
                "author_real": author_real,
            }

            return render(request, template, context=contex)
        else:
            return redirect("/")

    def post(self, request, pk):
        template = 'goods/add_car.html'
        get_car = Car.objects.get(pk=pk)

        form = AddCar(request.POST, instance=get_car)  # для заполнения формы данными
        author = self.request.user

        if form.is_valid():
            form = form.save(commit=False)
            form.author = author
            form.save()

        context = {
            'get_car': get_car,
            'update': True,
            'form': AddCar(request.POST, instance=get_car)
        }
        # return reverse("add_car_new")
        # return redirect('/add_car.html')
        return render(request, template, context=context)


def delete_car(request, pk):
    get_car = Car.objects.get(pk=pk)
    author = request.user
    author_real = get_car.author
    if author == author_real or request.user.is_superuser:
        get_car.delete()
        return redirect(reverse('add_car_new'))
    else:
        return redirect("/")


###############    Registration      -------------------------------------------
class MyLoginUserView(LoginView):
    template_name = 'goods/login.html'
    form_class = AuthForm
    success_url = reverse_lazy('goods_list_url')

    def get_success_url(self):
        return self.success_url


class MyRegisterUserView(CreateView):
    # model = UserInRegistrated
    model = User
    template_name = 'goods/register_page.html'
    form_class = RegisterForm
    success_url = reverse_lazy('goods_list_url')

    ### переопределение метода для автоматической авторизации через переменную authenticate #######
    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user_auth = authenticate(username=username, password=password)
        login(self.request, user_auth)
        return form_valid


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('goods_list_url')


###############    Registration      -------------------------------------------


class CarDetail(View):
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['star_form'] = RatingForm()
    #     return context

    def get(self, request, slug):
        car = Car.objects.get(slug=slug)
        category = Category.objects.all()
        ############################## Paginanate #####################
        # review = Reviews.objects.all()
        # review = car.get_review()
        review = car.reviews_set.filter(parent__isnull=True)
        paginator = Paginator(review, 5)
        page_num = request.GET.get('page', 1)
        page = paginator.get_page(page_num)
        is_paginated = page.has_other_pages()
        if page.has_previous():
            prev_url = '?page={}'.format(page.previous_page_number())
        else:
            prev_url = ''
        if page.has_next():
            next_url = '?page={}'.format(page.next_page_number())
        else:
            next_url = ''
        # print(dir(review))
        context = {
            'posts': page,
            'is_paginated': is_paginated,
            'next_url': next_url,
            'prev_url': prev_url,
            'car': car,
            # 'rev': rev
            'category': category,

        }

        ############################## Paginanate #####################
        # return render(request, 'goods/product.html', {'car': car})

        return render(request, 'goods/product.html', context=context)


class AddReview(View):
    def post(self, request, pk):
        form = ReviewForm(request.POST)

        car = Car.objects.get(id=pk)
        # print(review)
        if form.is_valid():
            form = form.save(commit=False)

            form.car = car
            form.date_post = timezone.now()
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))

            form.save()

            # return redirect('/')
        return redirect(car.get_absolute_url())


class AddStars(View):
    def post(self, request, pk):
        form = RatingForm(request.POST)

        car = Car.objects.get(id=pk)
        # print(review)
        if form.is_valid():
            Rating.objects.update_or_create(
                # ip=self.get_client_ip(request),
                car_id=int(request.POST.get("car")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)
        # context['star_form'] = form
        # return context
        #     # return redirect('/')
        # return redirect(car.get_absolute_url())


class AddStarRating(View):
    """Добавление рейтинга фильму"""

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)

# Create your views here.
