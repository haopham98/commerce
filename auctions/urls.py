from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_auction", views.create_auction, name="create_auction"),
    path("listing/<int:auction_id>", views.auction_detail, name="auction_detail"),
    path("bid/<int:auction_id>", views.place_bid, name="place_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<int:auction_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:auction_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path('add_comment/<int:auction_id>', views.add_comment, name='add_comment'),
    path('close_auction/<int:auction_id>', views.close_auction, name='close_auction'),
    path('category/<str:category_name>', views.category_view, name='category_view'),
]
