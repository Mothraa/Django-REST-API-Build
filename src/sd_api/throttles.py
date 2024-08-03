from rest_framework.throttling import SimpleRateThrottle


class CustomThrottle(SimpleRateThrottle):
    # limite à 10 requetes par min
    rate = '10/m'

    # IP en clé unique pour chaque utilisateur et suivre le nombre de requetes
    def get_cache_key(self, request, view):
        return self.get_ident(request)
    # limitation par utilisateur (id utilisé en clé)
        # user = request.user
        # if user.is_authenticated:
        #     return f"user_{user.id}"
