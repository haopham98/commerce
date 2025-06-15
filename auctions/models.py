from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return str(self.username)

 
class Auction(models.Model):
    """
    Model representing an auction.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)

    current_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auctions'
    )
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)


class Bid(models.Model):
    """
    Model representing a bid in an auction.
    """
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if (
            self.auction.is_active
            and (
                self.amount > self.auction.current_bid
                or self.auction.current_bid is None
            )
        ):
            self.auction.current_bid = self.amount
            self.auction.save()
        else:
            raise ValueError(
                "Bid amount must be higher than the current bid or starting bid."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.auction.title}"

class Comment(models.Model):
    """
    Model representing a comment on an auction.
    """
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} commented on "
            f"{self.auction.title}: {self.content}"
        )


class AuctionCategory(models.Model):
    """
    Model representing a category for auctions.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.name)

class AuctionCategoryMapping(models.Model):
    """
    Model representing the mapping of auctions to categories.
    """
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    category = models.ForeignKey(
        AuctionCategory,
        on_delete=models.CASCADE,
        related_name='auctions'
    )

    class Meta:
        unique_together = ('auction', 'category')

    def __str__(self):
        return f"{self.auction.title} in {self.category.name}"


class Watchlist(models.Model):
    """
    Model representing a user's watchlist for auctions.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_watchlists'
    )
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='auction_watchlists'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'auction')

    def __str__(self):
        return f"{self.user.username} watching {self.auction.title}"
    

class ClosedAuction(models.Model):
    """
    Model representing a closed auction.
    """
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='closed_auction')
    closed_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_auctions'
    )

    def __str__(self):
        return f"{self.auction.title} closed at {self.fin:winneral_price} on {self.closed_at}"

    @property
    def final_price(self):
        return self.auction.current_bid if self.auction.current_bid else self.auction.starting_bid


def validate_image_size(image):
    """
    Kiểm tra kích thước hình ảnh, không vượt quá 5MB.
    """
    from django.core.exceptions import ValidationError
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("Kích thước hình ảnh không được vượt quá 5MB.")


def auction_image_path(instance, filename):
    """
    Tạo đường dẫn lưu trữ hình ảnh theo thời gian: auction_images/YYYY/MM/DD/filename.
    
    Args:
        instance: Đối tượng AuctionImage đang được lưu.
        filename: Tên tệp gốc của hình ảnh (ví dụ: photo.jpg).
    
    Returns:
        Đường dẫn tương đối như: auction_images/2025/06/15/photo.jpg
    """
    from datetime import datetime
    date_str = datetime.now().strftime('%Y/%m/%d')
    return f'auction_images/{date_str}/{filename}'


class AuctionImage(models.Model):
    """
    Model representing an image associated with an auction.
    """
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=auction_image_path,
        validators=[validate_image_size]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.auction.title} uploaded at {self.uploaded_at}"
