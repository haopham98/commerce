from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from auctions.common import CATEGORY_CHOICES
from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    listings = Listing.objects.filter().order_by('created_at')
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": [category[0] for category in CATEGORY_CHOICES] # List of categories for the dropdown
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
    return redirect("/", {
        "message": "Auction created successfully!"
    })
    

def auction_detail(request, auction_id):
    """
        Render the auction detail page for a specific auction
        with the auction item, comments, and check if the user is the owner
        If the auction is closed, display the user who won the auction
    """
    item = Listing.objects.get(id=auction_id)
    if not item.is_active:
        #if item.won_price > 0 and item.current_bid != item.starting_bid:
        winner = Bid.objects.filter(listing=item).order_by('-amount').first()
        if winner:
            is_winner = winner.user == request.user
        else:
            is_winner = False
        return render(request, "auctions/auction_detail.html", {
            "listing": item,
            "comments": item.comments.all(),
            "is_owner": item.owner == request.user,
            "is_active": item.is_active,
            "is_winner": is_winner,
            "winner": winner if winner else None
        })
    else:
        winner = None
        is_winner = False
        return render(request, "auctions/auction_detail.html", {
            "listing": item,
            "comments": item.comments.all(),
            "is_owner": item.owner == request.user,
            "is_active": item.is_active,
            "is_winner": is_winner
        })

@login_required
def place_bid(request, auction_id):
    """
        Get bid of current user for a specific auction
        check if the bid is higher than the current bid
        if so, update the current bid and create a new Bid object
    """
    item = Listing.objects.get(id=auction_id)
    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount", None) 
        if bid_amount is None:
            return render(request, "auctions/auction_detail.html", {
                "listing": item,
                "message": "Please enter a bid amount."
            })
        try:
            bid_amount = float(bid_amount) #parse the bid amount to float
            if bid_amount <= item.current_bid:
                return render(request, "auctions/auction_detail.html", {
                    "listing": item,
                    "message": "Bid must be higher than the current bid."
                })
            # Update the current bid of the item
            item.current_bid = bid_amount
            item.save()
            # Create a new Bid object
            new_bid = Bid(listing=item, user=request.user, amount=bid_amount)
            new_bid.save()
            return render(request, "auctions/auction_detail.html", {
                "listing": item,
                "message": "Bid placed successfully!"
            })
        except ValueError:
            return render(request, "auctions/auction_detail.html", {
                "listing": item,
                "message": "Invalid bid amount. Please enter a valid number."
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

@login_required
def add_comment(request, auction_id):
    """
        Add a comment to an auction listing
        after the user is authenticated
        and render the auction detail page with the new comment
    """
    if request.method == "POST":
        item = Listing.objects.get(id=auction_id)
        comment_content = request.POST.get("comment_content", None)

        if comment_content:
            new_comment = Comment(listing=item, user=request.user, content=comment_content)
            new_comment.save()
            
            return render(request, "auctions/auction_detail.html", {
                "listing": item,
                "comments": item.comments.all(),
                "message": "Comment added successfully!",
                "page_url": request.build_absolute_uri()
            })
        else:
            return redirect(request, "auctions/auction_detail.html", {
                "listing": item,
                "comments": item.comments.all(),
                "message": "Comment content cannot be empty."
            })

@login_required
def close_auction(request, auction_id):
    """
        Check if the auction is active
        and current user is the owner of the auction
        If so, close the auction and update the won price
    """
    item = Listing.objects.get(id=auction_id)
    if item.is_active and item.owner == request.user:
        item.is_active = False
        item.won_price = item.current_bid
        item.save()
        return render(request, "auctions/auction_detail.html", {
            "listing": item,
            "message": "Auction closed successfully!",
            "comments": item.comments.all(),
            "is_owner": True
        })
    else:
        return render(request, "auctions/auction_detail.html", {
            "listing": item,
            "comments": item.comments.all(),
            "is_owner": False
        })

def category_view(request, category_name):
    """
        Render the auction listings for a specific category
    """
    listings = Listing.objects.filter(category=category_name, is_active=True).order_by('created_at')
    return render(request, "auctions/category.html", {
        "category": category_name,
        "listings": listings,
        "categories": [category[0] for category in CATEGORY_CHOICES]
    })