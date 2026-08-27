import json
from itsdangerous import URLSafeTimedSerializer, BadSignature

SECRET_KEY = 'REPLACE_WITH_A_REAL_RANDOM_KEY'  # load from env var in real deployment
serializer = URLSafeTimedSerializer(SECRET_KEY)

def create(response, username):
    session = serializer.dumps({'username': username})
    response.set_cookie('vulpy_session', session, httponly=True, samesite='Lax')
    return response

def load(request):
    session = {}
    cookie = request.cookies.get('vulpy_session')
    try:
        if cookie:
            session = serializer.loads(cookie, max_age=3600)
    except BadSignature:
        pass
    return session

def destroy(response):
    response.set_cookie('vulpy_session', '', expires=0)
    return response
