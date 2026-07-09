from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count

from .models import Villa, Booking, Incident, Staff, VillaImage
from .forms import BookingForm, IncidentForm


# =========================
# Villa List
# =========================
def villa_list(request):
    today = timezone.now().date()
    villas = Villa.objects.all()
    villa_status = []

    for villa in villas:
        booked_today = Booking.objects.filter(
            villa=villa,
            check_in_date__lte=today,
            check_out_date__gte=today
        ).exists()

        villa_status.append({
            'villa': villa,
            'is_available': not booked_today
        })

    return render(request, 'villa/villa_list.html', {'villa_status': villa_status})


# =========================
# Villa Detail
# =========================
def villa_detail(request, pk):
    villa = get_object_or_404(Villa, pk=pk)
    images = VillaImage.objects.filter(villa=villa)

    return render(request, 'villa/villa_detail.html', {
        'villa': villa,
        'images': images
    })


# =========================
# Book Villa
# =========================
@login_required
def book_villa(request, pk):
    villa = get_object_or_404(Villa, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.villa = villa
            booking.user = request.user

            existing_bookings = Booking.objects.filter(
                villa=villa,
                check_in_date__lt=booking.check_out_date,
                check_out_date__gt=booking.check_in_date
            )

            if existing_bookings.exists():
                form.add_error(None, "This villa is already booked for those dates.")
            else:
                booking.save()
                messages.success(request, "🎉 Booking successful!")
                return redirect('booking_success', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'villa/book_villa.html', {
        'form': form,
        'villa': villa
    })


# =========================
# Booking Success
# =========================
@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user != request.user and not request.user.is_staff:
        return redirect('villa_list')

    return render(request, 'villa/booking_success.html', {'booking': booking})


# =========================
# Report Incident
# =========================
@login_required
def report_incident(request, villa_id):
    villa = get_object_or_404(Villa, pk=villa_id)

    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.villa = villa
            incident.user = request.user
            incident.save()
            return redirect('villa_list')
    else:
        form = IncidentForm()

    return render(request, 'villa/report_incident.html', {
        'form': form,
        'villa': villa
    })


# =========================
# Incident List
# =========================
@login_required
def incident_list(request):
    if request.user.is_staff:
        incidents = Incident.objects.all().order_by('-date_reported')
    else:
        incidents = Incident.objects.filter(user=request.user).order_by('-date_reported')

    return render(request, 'villa/incident_list.html', {'incidents': incidents})


# =========================
# Assign Staff
# =========================
@login_required
def assign_staff(request, pk):
    if not request.user.is_staff:
        return redirect('villa_list')

    incident = get_object_or_404(Incident, pk=pk)
    staff_members = Staff.objects.all()

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        staff = get_object_or_404(Staff, id=staff_id)

        incident.staff = staff
        incident.save()

        return redirect('incident_list')

    return render(request, 'villa/assign_staff.html', {
        'incident': incident,
        'staff_members': staff_members
    })


# =========================
# Resolve Incident
# =========================
@login_required
def resolve_incident(request, pk):
    if not request.user.is_staff:
        return redirect('villa_list')

    incident = get_object_or_404(Incident, pk=pk)
    incident.resolved = True
    incident.save()
    return redirect('incident_list')


# =========================
# Staff List + Create Staff
# =========================
@staff_member_required
def staff_list(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        phone = request.POST.get('phone_number')
        villa_id = request.POST.get('assigned_villa')

        villa = None
        if villa_id:
            villa = Villa.objects.get(id=villa_id)

        Staff.objects.create(
            name=name,
            role=role,
            phone_number=phone,
            assigned_villa=villa
        )

    staff_members = Staff.objects.all()
    villas = Villa.objects.all()

    return render(request, 'villa/staff_list.html', {
        'staff_members': staff_members,
        'villas': villas
    })


# =========================
# EDIT STAFF
# =========================
@staff_member_required
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        staff.name = request.POST.get('name')
        staff.role = request.POST.get('role')
        staff.phone_number = request.POST.get('phone_number')
        staff.save()
        return redirect('staff_list')

    return render(request, 'villa/edit_staff.html', {'staff': staff})


# =========================
# DELETE STAFF
# =========================
@staff_member_required
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.delete()
    return redirect('staff_list')


# =========================
# Signup
# =========================
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            login(request, user)
            return redirect('villa_list')
    else:
        form = UserCreationForm()

    return render(request, 'villa/signup.html', {'form': form})


# =========================
# User Dashboard
# =========================
@login_required
def dashboard(request):
    if request.user.is_staff:
        bookings = Booking.objects.all().order_by('-check_in_date')
        incidents = Incident.objects.all().order_by('-date_reported')
    else:
        bookings = Booking.objects.filter(user=request.user).order_by('-check_in_date')
        incidents = Incident.objects.filter(user=request.user).order_by('-date_reported')

    return render(request, 'villa/dashboard.html', {
        'bookings': bookings,
        'incidents': incidents
    })


# =========================
# Admin Analytics Dashboard
# =========================
@staff_member_required
def admin_dashboard(request):
    total_villas = Villa.objects.count()
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    total_incidents = Incident.objects.count()
    resolved_incidents = Incident.objects.filter(resolved=True).count()
    pending_incidents = Incident.objects.filter(resolved=False).count()

    bookings_per_month = (
        Booking.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = [b['month'].strftime('%b %Y') for b in bookings_per_month]
    booking_counts = [b['count'] for b in bookings_per_month]

    context = {
        'total_villas': total_villas,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_incidents': total_incidents,
        'resolved_incidents': resolved_incidents,
        'pending_incidents': pending_incidents,
        'months': months,
        'booking_counts': booking_counts,
    }

    return render(request, 'villa/admin_dashboard.html', context)