from django.db import models
from django.contrib.auth.models import User


class Villa(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)

    # EXISTING
    image = models.ImageField(upload_to='villas/', blank=True, null=True)

    # ✅ NEW (ADD THESE)
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class VillaImage(models.Model):
    villa = models.ForeignKey(Villa, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='villa_gallery/')

    def __str__(self):
        return f"Image for {self.villa.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ linked to logged-in user
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    villa = models.ForeignKey(Villa, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest_name} - {self.villa.name}"


class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    assigned_villa = models.ForeignKey(
        Villa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.role}"


class Incident(models.Model):
    villa = models.ForeignKey(Villa, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # ✅ assigned staff
    description = models.TextField()
    date_reported = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Incident at {self.villa.name} reported by {self.user.username}"