from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # MAIN
    # =========================
    path('', views.villa_list, name='villa_list'),
    path('villa/<int:pk>/', views.villa_detail, name='villa_detail'),

    # =========================
    # AUTH
    # =========================
    path('signup/', views.signup, name='signup'),

    # =========================
    # BOOKING
    # =========================
    path('villa/<int:pk>/book/', views.book_villa, name='book_villa'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),

    # =========================
    # INCIDENTS
    # =========================
    path('villa/<int:villa_id>/report/', views.report_incident, name='report_incident'),
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/<int:pk>/resolve/', views.resolve_incident, name='resolve_incident'),
    path('incidents/<int:pk>/assign/', views.assign_staff, name='assign_staff'),

    # =========================
    # DASHBOARD
    # =========================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # =========================
    # STAFF MANAGEMENT
    # =========================
    path('staff/', views.staff_list, name='staff_list'),

    # 🔥 ADD THESE (FIX YOUR ERROR)
    path('staff/edit/<int:pk>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:pk>/', views.delete_staff, name='delete_staff'),
]