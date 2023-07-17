from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from . import views
from .views import LoginView, RegisterView, UserView, LogoutView

urlpatterns = [
    path('home', views.home, name='home'),
    path("images", views.ImageView.as_view()),
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("user", UserView.as_view()),
    path("logout", LogoutView.as_view()),
    path('openapi', get_schema_view(
        title="PicSearch",
        public=True,
        
        description="API for all things …",
    ), name='openapi-schema'),
    path('docs', TemplateView.as_view(
        template_name='docs.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),

]
