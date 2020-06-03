from django.db import models

# Create your models here.

class Hashtag(models.Model):
    hashtag = models.CharField(max_length=150)
    count = models.PositiveIntegerField()

    def __str__(self):
        return self.hashtag
class PostList(models.Model):
    hashtag = models.CharField(max_length=150)
    posts = models.CharField(max_length=2500000)

    def __str__(self):
        return self.posts
class Post(models.Model):
    hashtag = models.CharField(max_length=150)
    shortcode = models.CharField(max_length=150)
    user_id = models.CharField(max_length=150)
    username = models.CharField(max_length=150, null=True, blank=True)
    # like_users = models.ManyToManyField(UserLike, null=True, blank=True)
    count_likes = models.PositiveIntegerField()
    time = models.CharField(max_length=150, null=True, blank=True)
    is_bound_shpion = models.BooleanField(default=False)
    def __str__(self):
        return self.shortcode


class UserPost(models.Model):
    hashtag = models.CharField(max_length=150)
    user_id = models.CharField(max_length=150)
    username = models.CharField(max_length=150, null=True, blank=True)
    secondary_user = models.CharField(max_length=150, null=True, blank=True)
    has_secondary_user = models.BooleanField(default=False)
    shortcodes = models.ManyToManyField(Post)
    past_posts = models.PositiveIntegerField(null=True, blank=True)
    not_past_posts = models.PositiveIntegerField(null=True, blank=True)
    past_posts_bound_shpion =models.PositiveIntegerField(null=True, blank=True)
    not_past_posts_bound_shpion = models.PositiveIntegerField(null=True, blank=True)
    is_bound_shpion = models.BooleanField(default=False)
    is_black_list = models.BooleanField(default=False)
    not_past_posts_url = models.CharField(max_length=150, null=True, blank=True)
    not_past_posts_bound_shpion_url = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.user_id



class ShpionFollowingFollowers(models.Model):
    user_id = models.CharField(max_length=250, null=True, blank=True)
    username = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.username
class ShpionFollowing(models.Model):
    username = models.CharField(max_length=150)
    # followers = models.ManyToManyField(ShpionFollowingFollowers)
    followers = models.CharField(max_length=250000, null=True, blank=True)
    def __str__(self):
        return self.username
class Shpion(models.Model):
    username = models.CharField(max_length=150)
    following =  models.ManyToManyField(ShpionFollowing)
    password = models.CharField(max_length=250, null=True, blank=True)
    def __str__(self):
        return self.username

class BlackList(models.Model):
    user_id = models.CharField(max_length=250, null=True, blank=True)
    username = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.username

class SecondaryUser(models.Model):
    username = models.CharField(max_length=250, null=True, blank=True)
    secondary_user = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.username