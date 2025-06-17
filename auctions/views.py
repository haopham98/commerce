from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from auctions.common import CATEGORY_CHOICES
from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    listings = Listing.objects.filter(is_active=True).order_by('created_at')
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": [category[0] for category in CATEGORY_CHOICES]
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_auction(request):
    
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html", {
            "message": "You must be logged in to create an auction."
        })
    
    categories_list = [category[0] for category in CATEGORY_CHOICES]
    if request.method == "GET":
        return render(request, "auctions/auction_form.html", {
            "user": request.user,
            "categories": categories_list
        })
                      
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        end_date = request.POST["end_date"]
        image_auction = request.POST.get("image_auction", None)
        categories = request.POST["category"]
        auction = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            end_date=end_date,
            category=categories,
            owner=request.user
        )
        if image_auction:
            auction.image_url = image_auction
        else:
            auction.image_url = "https://placehold.co/600x400"
        auction.save()
        return render(request, "auctions/index.html", {
            "message": "Auction created successfully!"
        })

@login_required
def auction_detail(request, auction_id):
    listing = Listing.objects.get(id=auction_id)
    return render(request, "auctions/auction_detail.html", {
        "listing": listing
    })

@login_required
def place_bid(request, auction_id):
    if request.method == "POST":
        item = Listing.objects.get(id=auction_id)
        bid_amount = request.POST["bid_amount"]
        
        if float(bid_amount) <= item.current_bid:
            return render(request, "auctions/auction_detail.html", {
                "listing": item,
                "message": "Your bid must be higher than the current bid."
            })

        item.current_bid = bid_amount
        item.save()
        return render(request, "auctions/auction_detail.html", {
            "listing": item,
            "message": "Your bid has been placed successfully."
        })

@login_required
def watchlist(request):
    user_watchlist = Watchlist.objects.filter(user=request.user)
    for item in user_watchlist:
        print(item.listing.id, item.listing.title)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user_watchlist,
    })

@login_required
def add_to_watchlist(request, auction_id):
    item = Listing.objects.get(id=auction_id)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, listing=item)
    # If the item was not created, it means it already exists in the watchlist
    if not created:
        message = "Item already in your watchlist."
    else:
        message = "Item added to your watchlist."
    return render(request, "auctions/auction_detail.html", {
        "listing": item,
        "message": message
    })

@login_required
def remove_from_watchlist(request, auction_id):
    """
        remove an item from the user's watchlist
    """
    item = Listing.objects.get(id=auction_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, listing=item)
    if watchlist_item.exists():
        watchlist_item.delete()
        message = "Item removed from your watchlist."
    else:
        message = "Item not found in your watchlist."
    return render(request, "auctions/watchlist.html", {
        "listing": item,
        "message": message
    })