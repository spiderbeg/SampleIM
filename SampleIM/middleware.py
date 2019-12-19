from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User

ONLINE_THRESHOLD = getattr(settings, 'ONLINE_THRESHOLD', 3) # 先从settings 中拿 ONLINE_THRESHOLD 的配置，没有就用这里的配置 3
ONLINE_MAX = getattr(settings, 'ONLINE_MAX', 20) # 最大在线人数

def get_online_now(self): 
    return User.objects.filter(id__in=self.online_now_ids or [])


class OnlineNowMiddleware(object):
    """
    Maintains a list of users who have interacted with the website recently.
    Their user IDs are available as ``online_now_ids`` on the request object,
    and their corresponding users are available (lazily) as the
    ``online_now`` property on the request object.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        self.process_request(request)

        response = self.get_response(request)  # 这是分界线

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        # First get the index
        uids = cache.get('online-now', [])
        
        # Perform the multiget on the individual online uid keys
        online_keys = ['online-%s' % (u,) for u in uids]
        fresh = cache.get_many(online_keys).keys()
        online_now_ids = [int(k.replace('online-', '')) for k in fresh]
        
        # If the user is authenticated, add their id to the list
        if request.user.is_authenticated:
            uid = request.user.id
            # If their uid is already in the list, we want to bump it
            # to the top, so we remove the earlier entry.
            if uid in online_now_ids:
                online_now_ids.remove(uid)
            online_now_ids.append(uid)
            if len(online_now_ids) > ONLINE_MAX:
                del online_now_ids[0]
        
        # Attach our modifications to the request object 
        request.__class__.online_now_ids = online_now_ids 
        request.__class__.online_now = property(get_online_now) # property 将方法作为属性调用，这里是作为 request 类的方法
        
        # Set the new cache https://docs.djangoproject.com/en/2.2/topics/cache/#cache-arguments Basic usage
        cache.set('online-%s' % (request.user.pk,), True, ONLINE_THRESHOLD)
        cache.set('online-now', online_now_ids, ONLINE_THRESHOLD)