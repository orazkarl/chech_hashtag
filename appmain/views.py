from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.http import HttpResponse
from .models import Post, User, UserPost, UserLike, Hashtag, Shpion, ShpionFollowing, ShpionFollowingFollowers, BlackList
import requests
import datetime as dt
from django.conf import settings
import threading
import instaloader
from django.utils.timezone import pytz

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

zone = pytz.timezone(settings.TIME_ZONE)


class LockedIterator(object):
    def __init__(self, it):
        self.lock = threading.Lock()
        self.it = it.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        self.lock.acquire()
        try:
            return self.it.__next__()
        finally:
            self.lock.release()



class HomeView(generic.TemplateView):
    template_name = 'home.html'


@method_decorator(login_required, name='dispatch')
class ShpionView(generic.ListView):
    template_name = 'shpion.html'

    def get(self, request, *args, **kwargs):
        if request.GET:
            Shpion.objects.all().delete()
            ShpionFollowing.objects.all().delete()
            shpion = request.GET['username']
            password = request.GET['password']
            Shpion.objects.create(username=shpion, password=password)
            loader = instaloader.Instaloader()
            loader.login(shpion, password)
            # followees = instaloader.Profile.from_username(loader.context, shpion)
            # for profile in followees.get_followees():
            #     ShpionFollowing.objects.create(username=profile.username)
            # user = Shpion.objects.filter(username=shpion)[0]
            # followees_users = ShpionFollowing.objects.all()
            # for follow in followees_users:
            #     user.following.add(follow)
            # shpion_following = []
            # for i in user.following.all():
            #     shpion_following.append(i)
            # for i in shpion_following:
            #     followers = instaloader.Profile.from_username(loader.context, str(i)).get_followers()
            #     followers = LockedIterator(followers)
            #     for profile in followers:
            #         ShpionFollowingFollowers.objects.create(username=profile.username, user_id=profile.userid)
            #     user = ShpionFollowing.objects.filter(username=i)[0]
            #     for i in ShpionFollowingFollowers.objects.all():
            #         user.followers.add(i)
        self.queryset = Shpion.objects.all()
        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        hashtags = request.GET
        if len(hashtags) == 0:
            self.queryset = Hashtag.objects.all()
            return super().get(request, *args, **kwargs)
        elif request.GET['submit'] == 'Очистить':
            Hashtag.objects.all().delete()
            Post.objects.all().delete()
            UserPost.objects.all().delete()
        elif request.GET['submit'] == 'submit':
            Hashtag.objects.all().delete()
            ShpionFollowingFollowers.objects.all().delete()
            ShpionFollowing.objects.all().delete()
            shpion = Shpion.objects.all()[0]
            user = shpion.username
            password = shpion.password
            loader = instaloader.Instaloader()
            loader.login(user, password)
            followees = instaloader.Profile.from_username(loader.context, user).get_followees()
            followees = LockedIterator(followees)
            for profile in followees:
                followers = instaloader.Profile.from_username(loader.context, str(profile.username)).get_followers()
                followers = str(list(followers))
                ShpionFollowing.objects.create(username=profile.username, followers=followers)

            followees_users = ShpionFollowing.objects.all()
            for follow in followees_users:
                shpion.following.add(follow)

        l = []
        for hashtag in hashtags:
            if 'hashtag' in hashtag:
                l.append(hashtags[hashtag])
        hashtags = l
        # if request.GET['submit']=='Обновить':
        #     self.queryset = Hashtag.objects.all()
        #     hashtag = hashtags[0]
        #     Post.objects.filter(hashtag=hashtag).delete()
        #     UserPost.objects.filter(hashtag=hashtag).delete()
        #     return super().get(request, *args, **kwargs)
        for hashtag in hashtags:
            L = instaloader.Instaloader(sleep=False)
            h = instaloader.Hashtag.from_name(L.context, hashtag)
            Hashtag.objects.create(hashtag=hashtag, count=int(h.mediacount))

        self.queryset = Hashtag.objects.all()
        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class HashtagView(generic.ListView):
    template_name = 'hashtag.html'
    queryset =  UserPost.objects.all()
    def get(self, request, *args, **kwargs):
        hashtag = request.GET
        if len(hashtag) == 0:
            return render(request, self.template_name, {})

        if 'Обновить' in str(request.GET):
            Post.objects.all().delete()
        hashtag = hashtag['hashtag']
        L = instaloader.Instaloader()
        posts = instaloader.Hashtag.from_name(L.context, str(hashtag)).get_all_posts()
        # posts = LockedIterator(posts)
        shpion = Shpion.objects.all()[0]
        h = instaloader.Hashtag.from_name(L.context, hashtag)
        print(int(h.mediacount),  Post.objects.all().count())
        if int(h.mediacount) != Post.objects.all().count():
            # print(int(h.mediacount), Hashtag.objects.filter(hashtag=hashtag)[0].count)
            for post in posts:
                # print(post.likes)
                shortcode = post.shortcode
                user_id = post.owner_id
                username = post.owner_username
                # like_users = models.ManyToManyField(UserLike, null=True, blank=True)
                time = dt.datetime.fromtimestamp(int(post.date_local.timestamp()), tz=zone).strftime(
                    '%Y-%m-%d %H:%M:%S')
                is_bound_shpion = False
                for i in shpion.following.all():
                    if username in i.followers:
                        is_bound_shpion = True
                if not Post.objects.filter(username=username, shortcode=shortcode, hashtag=hashtag):
                    Post.objects.create(hashtag=hashtag, shortcode=shortcode, user_id=user_id, username=username,
                                        time=time, is_bound_shpion=is_bound_shpion, count_likes=int(post.likes))
            for post in Post.objects.all():
                has_secondary_user = False
                secondary_user = None
                past_posts = 0
                not_past_posts = 0
                past_posts_bound_shpion = 0
                not_past_posts_bound_shpion = 0
                not_past_posts_url = None
                not_past_posts_bound_shpion_url = None
                is_black_list = False
                if UserPost.objects.filter(user_id=post.user_id):
                    past_posts = UserPost.objects.filter(user_id=post.user_id)[0].past_posts
                    not_past_posts = UserPost.objects.filter(user_id=post.user_id)[0].not_past_posts
                    past_posts_bound_shpion = UserPost.objects.filter(user_id=post.user_id)[0].past_posts_bound_shpion
                    not_past_posts_bound_shpion = UserPost.objects.filter(user_id=post.user_id)[
                        0].not_past_posts_bound_shpion
                    secondary_user = UserPost.objects.filter(user_id=post.user_id)[0].secondary_user
                    has_secondary_user = UserPost.objects.filter(user_id=post.user_id)[0].has_secondary_user
                    not_past_posts_url = UserPost.objects.filter(user_id=post.user_id)[0].not_past_posts_url
                    not_past_posts_bound_shpion_url = UserPost.objects.filter(user_id=post.user_id)[
                        0].not_past_posts_bound_shpion_url
                if UserPost.objects.filter(user_id=post.user_id):
                    UserPost.objects.filter(user_id=post.user_id).delete()
                if BlackList.objects.filter(username=post.username):

                    is_black_list = True
                userposts = UserPost(user_id=post.user_id, hashtag=hashtag, username=post.username,
                                     secondary_user=secondary_user, has_secondary_user=has_secondary_user,
                                     is_bound_shpion=post.is_bound_shpion, past_posts=past_posts,
                                     not_past_posts=not_past_posts, past_posts_bound_shpion=past_posts_bound_shpion,
                                     not_past_posts_bound_shpion=not_past_posts_bound_shpion,
                                     not_past_posts_url=not_past_posts_url,
                                     not_past_posts_bound_shpion_url=not_past_posts_bound_shpion_url,
                                     is_black_list=is_black_list
                                     )
                userposts.save()
                l = Post.objects.filter(user_id=post.user_id)

                for i in l:
                    userposts.shortcodes.add(i)


        # self.queryset = UserPost.objects.filter(hashtag=hashtag)
        # self.queryset.
        self.extra_context ={
            'object_list': UserPost.objects.filter(hashtag=hashtag, is_bound_shpion=True, is_black_list=False),
            'hashtag': hashtag
        }


        # return render(request, self.template_name, {'count_posts': len(posts)})
        return super().get(request, *args, **kwargs)


def get_username(request):
    user_id = request.GET['user_id']
    hashtag = request.GET['hashtag']
    l = 'https://www.instagram.com/graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables={"user_id":"' + user_id + '","include_chaining":false,"include_reel":true,"include_suggested_users":false,"include_logged_out_extras":false,"include_highlight_reels":false,"include_related_profiles":false}'
    response = requests.get(l).json()
    username = response['data']['user']['reel']['user']['username']
    if not User.objects.filter(username=username):
        User.objects.create(user_id=user_id, username=username)
    UserPost.objects.filter(user_id=user_id).update(username=username)
    red = '/hashtag/?hashtag=' + hashtag
    return redirect(red)

@login_required()
def get_past_posts(request):
    user_id = request.GET['user_id']
    post_id = request.GET['post_id']
    hashtag = request.GET['hashtag']
    true_shortcodes = set()
    shortcodes = set()
    for post in UserPost.objects.filter(hashtag=hashtag):
        for i in post.shortcodes.all():
            shortcodes.add(i)
    for post in UserPost.objects.filter(hashtag=hashtag, is_black_list=False, is_bound_shpion=True):
        for i in post.shortcodes.all():
            true_shortcodes.add(i)

    L = instaloader.Instaloader(sleep=False)
    all_users = UserPost.objects.filter(hashtag=hashtag)
    my_users = UserPost.objects.filter(hashtag=hashtag, is_black_list=False, is_bound_shpion=True)
    for user in all_users:
        temp = []
        count = 0
        for shortcode in shortcodes:
            post = instaloader.Post.from_shortcode(L.context, str(shortcode))
            # if user.username != str(post.owner_username):
            # post = post.get_likes()
            # post = LockedIterator(post)

            if user.username in str(list(LockedIterator(post.get_likes()))):
                count += 1
            else:
                temp.append(post.shortcode)

        user.not_past_posts_url = str(temp)
        # print(user.not_past_posts_url)
        user.past_posts = count
        user.not_past_posts = len(shortcodes) - count
        user.save()
    for user in my_users:
        temp = []
        count = 0
        for shortcode in true_shortcodes:
            post = instaloader.Post.from_shortcode(L.context, str(shortcode))
            # if user.username != str(post.owner_username):
            # post = post..get_likes()
            # post = LockedIterator(post)
            if user.username in str(list(LockedIterator(post.get_likes()))):
                count += 1
            else:
                temp.append(post.shortcode)

        user.not_past_posts_bound_shpion_url = str(temp)
        user.past_posts_bound_shpion = count
        user.not_past_posts_bound_shpion = len(true_shortcodes) - count
        # print(user.past_posts_bound_shpion)
        user.save()
        # print('okarlitto' in str(list(post)))
        # if str() in str(list(post):

    #     for like in Post1:
    #
    #         if not UserLike.objects.filter(shortcode=shortcode, user_id=like.userid):
    #             UserLike.objects.create(shortcode=shortcode, user_id=like.userid, username=like.username)
    #     post = Post.objects.get(shortcode=shortcode)
    #     user_like = UserLike.objects.filter(shortcode=shortcode)
    #     post.like_users.filter(shortcode=shortcode).delete()
    #     for i in user_like:
    #         post.like_users.add(i)
    red = '/hashtag/?hashtag=' + hashtag
    return redirect(red)

@login_required()
def info(request):
    user_id = request.GET['user_id']
    hashtag = request.GET['hashtag']
    status = request.GET['status']
    l = []

    user = UserPost.objects.filter(user_id=user_id)[0]
    shortcodes = ''
    if status == 'shpion':
        shortcodes = user.not_past_posts_bound_shpion_url[1:len(user.not_past_posts_url) - 1]
    if status == 'all':
        shortcodes = user.not_past_posts_url[1:len(user.not_past_posts_url) - 1]

    for post in shortcodes.split(','):
        post = post[1:len(post) - 1]
        for char in post:
            if char in " ?.!/;:[]''":
                post = post.replace(char, '')
        l.append(post)

    red = '/hashtag/?hashtag=' + hashtag
    # return redirect(red)
    return render(request, 'info.html', {'list_posts': l})

@method_decorator(login_required, name='dispatch')
class SecondaryUserView(generic.ListView):
    template_name = 'secondary_user.html'

    def get(self, request, *args, **kwargs):
        if request.GET:
            if len(request.GET) == 0:
                self.queryset = UserPost.objects.filter(has_secondary_user=True)
                return super().get(request, *args, **kwargs)
            elif request.GET['submit'] == 'delete':
                user = UserPost.objects.filter(user_id=request.GET['username'])[0]
                user.secondary_user = None
                user.has_secondary_user = False
                user.save()
            elif request.GET['submit'] == 'Отправить':
                username = request.GET['username']
                secondary_user = request.GET['secondary_user']
                if UserPost.objects.filter(username=username):
                    user = UserPost.objects.filter(username=username)[0]
                    user.secondary_user = secondary_user
                    user.has_secondary_user = True
                    user.save()
        self.queryset = UserPost.objects.filter(has_secondary_user=True)

        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class DetailCheckView(generic.ListView):
    template_name = 'detailcheck.html'

    def get(self, request, *args, **kwargs):


        hashtag = request.GET['hashtag']
        self.queryset = UserPost.objects.filter(hashtag=hashtag)

        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class BlackListView(generic.ListView):
    template_name = 'blacklist.html'

    def get(self, request, *args, **kwargs):
        if request.GET:
            if len(request.GET) == 0:
                # self.queryset = UserPost.objects.filter(is_black_list=True)
                self.queryset = BlackList.objects.all()
                return super().get(request, *args, **kwargs)
            elif request.GET['submit'] == 'delete':
                username = request.GET['username']
                print(username)
                BlackList.objects.filter(username=username).delete()
                # user = UserPost.objects.filter(user_id=request.GET['username'])[0]
                # user.is_black_list = False
                # user.save()
            elif request.GET['submit'] == 'Отправить':
                username = request.GET['username']
                secondary_user = request.GET['username']

                # user = UserPost.objects.filter(username=request.GET['username'])
                # print(user)
                # if user:
                BlackList.objects.create(username=username)
                # if UserPost.objects.filter(username=username):
                #     user = UserPost.objects.filter(username=username)[0]
                #     user.is_black_list = True
                #     user.save()

        self.queryset = BlackList.objects.all()
        return super().get(request, *args, **kwargs)

@login_required()
def parse(request):
    hashtag = request.GET['hashtag']
    l = []
    for user in UserPost.objects.filter(hashtag=hashtag, is_bound_shpion=False):
        l.append('@' + str(user.username))

    return render(request, 'parse.html', {'list_posts': l})

@login_required()
def parse_users(request):
    users = ''
    l = []
    if request.GET:
        users = request.GET['users']

    users = users.splitlines()

    for user in users:
        if '@' in user:
            user = user.replace('@', '')
        if not UserPost.objects.filter(username=user, is_bound_shpion=True):
            l.append('@' + str(user))

    # hashtag = str(request.GET['hashtag']).split('=')[1]

    # for user in UserPost.objects.filter(hashtag=hashtag, is_bound_shpion=True):
    #
    #     l.append('@' + str(user.username))

    return render(request, 'parse_users.html', {'list_posts': l})
@login_required()
def refresh(request):
    hashtag = request.GET['hashtag']
    Post.objects.filter(hashtag=hashtag).delete()
    UserPost.objects.filter(hashtag=hashtag).delete()
    red = '/hashtag/?hashtag=' + hashtag
    return redirect(red)