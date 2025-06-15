from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, AuctionCategory


def index(request):
    return render(request, "auctions/index.html")


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
    categories = AuctionCategory.objects.all()
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html", {
           "message": "You must be logged in to create an auction."
    })

    if request.method == "GET":
        return render(request, "auctions/auction_form.html", {
            "user": request.user,
            "categories": categories
        })
                      
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        end_date = request.POST["end_date"]
        image_auction = request.POST.get("image_auction", None)
        print(request.POST)
        auction = Auction(
            title=title,
            description=description,
            starting_bid=starting_bid,
            end_date=end_date,
            user=request.user
        )
        if image_auction:
            auction.image_auction = image_auction
        else:
            auction.image_auction = "https://placehold.co/600x400"
        auction.save()
        return render(request, "auctions/index.html", {
            "message": "Auction created successfully!"
        })

