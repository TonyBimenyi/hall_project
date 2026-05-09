from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'halls', views.HallViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'personnel', views.PersonnelViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'expenses', views.ExpenseViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', views.SummaryView.as_view(), name='summary'),
    path('me/', views.MeView.as_view(), name='me'),
    path('register/', views.RegisterView.as_view(), name='register'),
]