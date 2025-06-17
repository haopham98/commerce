from django.contrib.auth.models import AbstractUser
from django.db import models
from auctions.common import CATEGORY_CHOICES


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return str(self.username)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(2000, blank=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    won_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    end_date = models.DateTimeField(blank=True, null=True)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.current_bid:
            self.current_bid = self.starting_bid
        if not self.image_url:
            self.image_url = "https://placehold.co/600x400"
        if not self.end_date:
            from django.utils import timezone
            self.end_date = timezone.now() + timezone.timedelta(days=7)
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.title} - {self.owner.username}"
    

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid {self.amount} by {self.user.username} on {self.listing.title}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchlist')

    def __str__(self):
        return f"{self.user.username} is watching {self.listing.title}"
