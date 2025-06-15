from django.contrib import admin
from .models import (
    User,
    Auction,
    Bid,
    Comment,
    AuctionCategory,
    AuctionCategoryMapping,
    Watchlist,
    AuctionImage,
    ClosedAuction
)
# Register your models here.
admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(AuctionCategory)
admin.site.register(AuctionCategoryMapping)
admin.site.register(Watchlist)
admin.site.register(AuctionImage)
admin.site.register(ClosedAuction)