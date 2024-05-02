# from django.contrib import admin
# from .models import User
# # class UserAdmin(admin.ModelAdmin):
# #     list_display = ('email', 'username','phone_number', 'date_joined', 'last_login', 'is_staff', 'is_superuser', 'is_active', 'auth_provider')
# #     search_fields = ('email', 'username')
# #     list_filter = ('is_staff', 'is_superuser', 'is_active')
# # admin.site.register(User, UserAdmin)
from django.contrib import admin
from accounts.models import User,OTP,WishList,Reservation,Rating
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','phone_number', 'username','first_name','last_name', 'date_joined', 'last_login', 'is_staff', 'is_superuser', 'is_active','email','is_vendor','password'] 
class WhishListAdmin(admin.ModelAdmin):
    list_display = ['id','user','room','created_at']

class RatingAdmin(admin.ModelAdmin):
    list_display = ['id','user','room','rating','feedback']

class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'room',
        'created_at',
        'check_in',
        'check_out',
        'total_guest',
        'reservation_status',
        'is_active',
        'amount',
        'email',
        'last_name',
        'first_name',
        'contact_number'

    )
    list_filter = ('reservation_status', 'is_active', 'room', 'user')
    search_fields = ('user__username', 'room__name')
    date_hierarchy = 'check_in'
    ordering = ('-check_in',)
    readonly_fields = ('amount',)
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'room',
                'check_in',
                'check_out',
                'total_guest',
                'reservation_status',
                'is_active',
                'amount',
            )
        }),
    )
    list_editable = ('reservation_status', 'is_active')
    list_per_page = 25

admin.site.register(Reservation, ReservationAdmin)

admin.site.register(User, UserAdmin)
admin.site.register(OTP)
admin.site.register(WishList,WhishListAdmin)
admin.site.register(Rating,RatingAdmin)