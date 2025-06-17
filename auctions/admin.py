from django.contrib import admin
from .models import (
    User,
    Bid,
    Comment,
    Watchlist,
    Listing
)
# Register your models here.
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Listing)