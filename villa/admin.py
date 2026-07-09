from django.contrib import admin
from .models import Villa, VillaImage, Booking, Incident, Staff


# =========================
# INLINE IMAGES (GALLERY)
# =========================
class VillaImageInline(admin.TabularInline):
    model = VillaImage
    extra = 3  # number of empty slots


# =========================
# VILLA ADMIN
# =========================
class VillaAdmin(admin.ModelAdmin):
    inlines = [VillaImageInline]


# =========================
# REGISTER MODELS
# =========================
admin.site.register(Villa, VillaAdmin)
admin.site.register(Booking)
admin.site.register(Incident)
admin.site.register(Staff)