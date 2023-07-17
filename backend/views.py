import datetime

import coreapi
import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Image, User
from backend.serializer import ImageSerializer, UserSerializer






def get_current_user(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return None
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    user_id = payload.get('id')
    return User.objects.filter(id=user_id).first()


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        coreapi.Document(
            title='Register',
            content={
                'username': 'username',
                'email': 'email',
                'password': 'password',
            },
            url='/register/',
            description='Register'
        )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is not None:
            if user.check_password(password):
                payload = {
                    'id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
                response = Response()
                response.set_cookie(key='jwt', value=token, httponly=True)
                response.data = {
                    'jwt': token
                }
                return response
            return Response({"error": "Wrong credentials"})
        return Response({"error": "Wrong credentials"})


class UserView(APIView):
    def get(self, request):
        user = get_current_user(request)
        if user is None:
            return Response({'error': 'Authentication credentials were not provided.'}, status=401)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error': 'Authentication credentials were not provided.'}, status=401)
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Signature has expired.'}, status=401)
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class LogoutView(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


# Create your views here.
class ImageView(APIView):
    def get(self, request):
        # get query params
        # get image from db
        # return image
        query_params = request.query_params
        search = query_params.get("search")
        if search:
            # get imahge where tags contain search
            images = Image.objects.filter(tags__name__icontains=search)
        else:
            images = Image.objects.all()

        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        # get image from request
        # save image to db
        # return image
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def home():
    return "Hello World"