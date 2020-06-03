from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Hashtag)
# admin.site.register(UserLike)
admin.site.register(Post)
admin.site.register(UserPost)
admin.site.register(PostList)
admin.site.register(Shpion)
admin.site.register(ShpionFollowing)

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ['hashtag', 'shortcode', 'user_id', 'username']
#
# @admin.register(UserPost)
# class UserPostAdmin(admin.ModelAdmin):
#     list_display = ['hashtag',  'user_id', 'username']
# @admin.register(UserLike)
# class UserLikeAdmin(admin.ModelAdmin):
#     list_display = ['shortcode']
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ['user_id', 'username']
#
# @admin.register(Shpion)
# class ShpionAdmin(admin.ModelAdmin):
#     list_display = ['username']