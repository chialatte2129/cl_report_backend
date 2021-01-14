from rest_framework.authtoken.models import Token

from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import pytz


# token checker if token expired or not
def is_token_expired(token):
    utc_now  = datetime.now(pytz.utc)
    dealine=token.created + timedelta(seconds =settings.REST_FRAMEWORK_TOKEN_EXPIRE_SECONDS)
    if utc_now < dealine :
        return True
    else :
        return False     

# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired :   #update extend time
        utc_now  = datetime.now(pytz.utc)  
        print('update token utc_now',utc_now)
        token.created =utc_now
        token.save()        
    return is_expired, token