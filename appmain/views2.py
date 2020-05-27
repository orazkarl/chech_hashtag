# from django.shortcuts import render, get_object_or_404, redirect
# from django.views import generic
# from django.http import HttpResponse
# from .models import Post, User, UserPost,UserLike, Hashtag, Shpion, ShpionFollowing,ShpionFollowingFollowers
# import requests
# import datetime as dt
# from django.conf import settings
# import threading
# import instaloader
#
#
# class LockedIterator(object):
#     def __init__(self, it):
#         self.lock = threading.Lock()
#         self.it = it.__iter__()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         self.lock.acquire()
#         try:
#             return self.it.__next__()
#         finally:
#             self.lock.release()
#
# class ShpionView(generic.ListView):
#     template_name = 'shpion.html'
#     def get(self, request, *args, **kwargs):
#         if request.GET:
#             Shpion.objects.all().delete()
#             ShpionFollowing.objects.all().delete()
#             shpion = request.GET['username']
#             password = request.GET['password']
#             Shpion.objects.create(username=shpion, password=password)
#             loader = instaloader.Instaloader()
#             loader.login(shpion, password)
#             followees = instaloader.Profile.from_username(loader.context, shpion)
#             for profile in followees.get_followees():
#                 ShpionFollowing.objects.create(username=profile.username)
#             user = Shpion.objects.filter(username=shpion)[0]
#             followees_users = ShpionFollowing.objects.all()
#             for follow in followees_users:
#                 user.following.add(follow)
#             shpion_following = []
#             for i in user.following.all():
#                 shpion_following.append(i)
#             for i in shpion_following:
#                 followers = instaloader.Profile.from_username(loader.context, str(i)).get_followers()
#                 followers = LockedIterator(followers)
#                 for profile in followers:
#                     ShpionFollowingFollowers.objects.create(username=profile.username, user_id=profile.userid)
#                 user = ShpionFollowing.objects.filter(username=i)[0]
#                 for i in ShpionFollowingFollowers.objects.all():
#                     user.followers.add(i)
#         self.queryset = Shpion.objects.all()
#         return super().get(request, *args, **kwargs)
#
# class IndexView(generic.ListView):
#     template_name = 'index.html'
#
#     def get(self, request, *args, **kwargs):
#         hashtags = request.GET
#
#         if hashtags:
#             Hashtag.objects.all().delete()
#         l = []
#         for hashtag in hashtags:
#             if 'hashtag' in hashtag:
#                 l.append(hashtags[hashtag])
#         hashtags = l
#         for hashtag in hashtags:
#             L = instaloader.Instaloader(sleep=False)
#             h = instaloader.Hashtag.from_name(L.context, hashtag)
#             Hashtag.objects.create(hashtag=hashtag, count=int(h.mediacount))
#
#         self.queryset = Hashtag.objects.filter()
#         return super().get(request, *args, **kwargs)
#
#
# class HashtagView(generic.ListView):
#     template_name = 'hashtag.html'
#
#     def get(self, request, *args, **kwargs):
#         hashtag = request.GET
#         if len(hashtag) == 0:
#             return render(request, self.template_name, {})
#         # Post.objects.all().delete()
#         hashtag = hashtag['hashtag']
#         url = 'https://www.instagram.com/graphql/query/?query_hash=298b92c8d7cad703f7565aa892ede943&variables={"tag_name":"' + hashtag + '","first":100}'
#         responce = requests.get(url).json()
#         responce = responce['data']['hashtag']
#         posts = []
#         for i in responce['edge_hashtag_to_media']['edges']:
#             post = i['node']['shortcode']
#             owner = i['node']['owner']['id']
#             time = i['node']['taken_at_timestamp']
#             # Post.objects.create(hashtag=hashtag, shortcode=post, user_id=owner, display_url=display_url)
#             posts.append([post, owner, time])
#         if len(responce['edge_hashtag_to_media']['edges']) > 9:
#             for i in responce['edge_hashtag_to_top_posts']['edges']:
#                 post = i['node']['shortcode']
#                 owner = i['node']['owner']['id']
#                 time = i['node']['taken_at_timestamp']
#                 # Post.objects.create(hashtag=hashtag, shortcode=post, user_id=owner, display_url=display_url)
#                 posts.append([post, owner, time])
#         end_cursor = responce['edge_hashtag_to_media']['page_info']['end_cursor']
#         while True:
#             if end_cursor is not None:
#                 # url2 = ['https://www.instagram.com/graphql/query/?query_hash=298b92c8d7cad703f7565aa892ede943&variables={"tag_name":"' + hashtag + '","first":100, "after":"'+ end_cursor +'"}']
#                 url2 = 'https://www.instagram.com/graphql/query/?query_hash=298b92c8d7cad703f7565aa892ede943&variables={"tag_name":"' + hashtag + '","first":100, "after":"' + end_cursor + '"}'
#                 # next_responce = [grequests.get(u) for u in url2]
#                 # next_responce = grequests.map(responce)[0].json()
#                 next_responce = requests.get(url2).json()
#                 next_responce = next_responce['data']['hashtag']
#                 for i in next_responce['edge_hashtag_to_media']['edges']:
#                     post = i['node']['shortcode']
#                     owner = i['node']['owner']['id']
#                     time = i['node']['taken_at_timestamp']
#                     # Post.objects.create(hashtag=hashtag, shortcode=post, user_id=owner, display_url=display_url)
#                     posts.append([post, owner, time])
#                 end_cursor = next_responce['edge_hashtag_to_media']['page_info']['end_cursor']
#             else:
#                 break
#         shpion = Shpion.objects.all()[0]
#         shpion_following = []
#         for i in shpion.following.all():
#             shpion_following.append(i)
#
#         for i in posts:
#             from django.utils.timezone import pytz
#             post = i[0]
#             owner = i[1]
#             time_1 = i[2]
#             is_bound = False
#             for i in shpion_following:
#                 for user in i.followers.all():
#                     if owner == user.user_id:
#                         is_bound = True
#             zone = pytz.timezone(settings.TIME_ZONE)
#             time =  dt.datetime.fromtimestamp(int(time_1),tz=zone).strftime('%Y-%m-%d %H:%M:%S')
#
#             # display_url = i[2]
#             if User.objects.filter(user_id=owner):
#                 username = User.objects.filter(user_id=owner)
#                 username = username[0].username
#                 if not Post.objects.filter(shortcode=post):
#                     Post.objects.create(hashtag=hashtag, shortcode=post, user_id=owner, username=username, time=time, is_bound_shpion=is_bound)
#                 else:
#                     Post.objects.filter(shortcode=post).update(username=username)
#             if not Post.objects.filter(shortcode=post):
#                 Post.objects.create(hashtag=hashtag, shortcode=post, user_id=owner, time=time,  is_bound_shpion=is_bound)
#
#
#         for i in posts:
#             post = i[0]
#             owner = i[1]
#             is_bound = False
#             for i in shpion_following:
#                 for user in i.followers.all():
#                     if owner == user.user_id:
#                         is_bound = True
#
#
#
#             if UserPost.objects.filter(user_id=owner):
#                 secondary_user = UserPost.objects.filter(user_id=owner)[0].secondary_user
#                 has_secondary_user = UserPost.objects.filter(user_id=owner)[0].has_secondary_user
#                 UserPost.objects.filter(user_id=owner).delete()
#                 if User.objects.filter(user_id=owner):
#                     username = User.objects.filter(user_id=owner)
#                     username = username[0].username
#                     userposts = UserPost(user_id=owner, hashtag=hashtag, username=username, secondary_user=secondary_user, has_secondary_user=has_secondary_user, is_bound_shpion=is_bound)
#                 else:
#                     userposts = UserPost(user_id=owner, hashtag=hashtag,  secondary_user=secondary_user, has_secondary_user=has_secondary_user,is_bound_shpion=is_bound)
#
#                 userposts.save()
#                 l = Post.objects.filter(user_id=owner)
#                 for i in l:
#                     userposts.shortcodes.add(i)
#             else:
#                 userposts = UserPost(user_id=owner, hashtag=hashtag,is_bound_shpion=is_bound)
#                 userposts.save()
#                 l = Post.objects.filter(user_id=owner)
#                 for i in l:
#                     userposts.shortcodes.add(i)
#         summa_bound = 0
#         for i in UserPost.objects.filter(hashtag=hashtag, is_bound_shpion=True):
#             summa_bound += (i.shortcodes.all().count())
#         for user in UserPost.objects.filter(hashtag=hashtag):
#             count = 0
#             bound_count = 0
#             for post in Post.objects.filter(hashtag=hashtag):
#                 if user.has_secondary_user:
#                     if post.like_users.filter(post__like_users__username__icontains=user.secondary_user):
#                         count+=1
#                 else:
#                     if post.like_users.filter(post__like_users__user_id__icontains=user.user_id):
#                         count+=1
#                 if user.is_bound_shpion and post.is_bound_shpion:
#                     if user.has_secondary_user:
#                         if post.like_users.filter(post__like_users__username__icontains=user.secondary_user):
#                             bound_count += 1
#                     else:
#                         if post.like_users.filter(post__like_users__user_id__icontains=user.user_id):
#                             bound_count += 1
#
#
#
#             summa = Post.objects.filter(hashtag=hashtag).count()
#
#
#             user.past_posts = count
#             user.not_past_posts = summa - count
#             if user.is_bound_shpion:
#
#                 user.past_posts_bound_shpion = bound_count
#                 user.not_past_posts_bound_shpion = summa_bound - bound_count
#             user.save()
#
#
#
#         self.queryset = UserPost.objects.filter(hashtag=hashtag)
#
#         # print(len(posts))
#         # return render(request, self.template_name, {'count_posts': len(posts)})
#         return super().get(request, *args, **kwargs)
#         # return HttpResponse('Найдено ' + str(len(posts)) + ' постов')
#
#
# def get_username(request):
#     user_id = request.GET['user_id']
#     hashtag = request.GET['hashtag']
#     l = 'https://www.instagram.com/graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables={"user_id":"' + user_id + '","include_chaining":false,"include_reel":true,"include_suggested_users":false,"include_logged_out_extras":false,"include_highlight_reels":false,"include_related_profiles":false}'
#     response = requests.get(l).json()
#     username = response['data']['user']['reel']['user']['username']
#     if not User.objects.filter(username=username):
#         User.objects.create(user_id=user_id, username=username)
#     UserPost.objects.filter(user_id=user_id).update(username=username)
#     # print(user.username, 1)
#     # return HttpResponse('asd')
#     red = '/hashtag/?hashtag=' + hashtag
#     return redirect(red)
#
#
# def get_past_posts(request):
#     user_id = request.GET['user_id']
#     post_id = request.GET['post_id']
#     hashtag = request.GET['hashtag']
#     shortcodes = set()
#     for post in UserPost.objects.filter(hashtag=hashtag):
#         for i in post.shortcodes.all():
#             shortcodes.add(i)
#     for shortcode in shortcodes:
#         L = instaloader.Instaloader(sleep=False)
#         Post1 = instaloader.Post.from_shortcode(L.context, str(shortcode)).get_likes()
#         Post1 = LockedIterator(Post1)
#         # print('okarlitto' in str(list(Post1.get_likes())))
#
#         for like in Post1:
#
#             if not UserLike.objects.filter(shortcode=shortcode, user_id=like.userid):
#                 UserLike.objects.create(shortcode=shortcode, user_id=like.userid, username=like.username)
#         post = Post.objects.get(shortcode=shortcode)
#         user_like = UserLike.objects.filter(shortcode=shortcode)
#         post.like_users.filter(shortcode=shortcode).delete()
#         for i in user_like:
#             post.like_users.add(i)
#     red = '/hashtag/?hashtag=' + hashtag
#     return redirect(red)
#
#
# def info(request):
#     user_id = request.GET['user_id']
#     hashtag = request.GET['hashtag']
#     l = []
#     user = UserPost.objects.filter(user_id=user_id)[0]
#     for post in Post.objects.filter(hashtag=hashtag):
#         # if not post.like_users.filter(post__like_users__user_id__icontains=user_id):
#         if user.has_secondary_user:
#             if post.like_users.exclude(post__like_users__username__icontains=user.secondary_user) or post.like_users.count() == 0:
#                 l.append(post)
#         else:
#             if post.like_users.exclude(post__like_users__user_id__icontains=user_id):
#                 l.append(post)
#
#     red = '/hashtag/?hashtag=' + hashtag
#     # return redirect(red)
#     return render(request, 'info.html', {'list_posts': l})
#
#
#
# class SecondaryUserView(generic.ListView):
#     template_name = 'secondary_user.html'
#
#     def get(self, request, *args, **kwargs):
#
#
#         if request.GET:
#             if len(request.GET) == 0:
#                 self.queryset = UserPost.objects.filter(has_secondary_user=True)
#                 return super().get(request, *args, **kwargs)
#             elif request.GET['submit'] == 'delete':
#
#                 user = UserPost.objects.filter(user_id=request.GET['username'])[0]
#                 del user.secondary_user
#                 user.has_secondary_user = False
#                 user.save()
#             elif request.GET['submit'] == 'Отправить':
#                 username = request.GET['username']
#                 secondary_user = request.GET['secondary_user']
#                 if UserPost.objects.filter(username=username):
#                     user = UserPost.objects.filter(username=username)[0]
#                     user.secondary_user = secondary_user
#                     user.has_secondary_user = True
#                     user.save()
#         self.queryset = UserPost.objects.filter(has_secondary_user=True)
#
#         return super().get(request, *args, **kwargs)
#
#
# class DetailCheckView(generic.ListView):
#     template_name = 'detailcheck.html'
#
#     def get(self, request, *args, **kwargs):
#         hashtag = str(request.GET['hashtag']).split('=')[1]
#
#         self.queryset = UserPost.objects.filter(hashtag=hashtag, is_bound_shpion=True)
#         return super().get(request, *args, **kwargs)