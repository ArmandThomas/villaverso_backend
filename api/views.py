from rest_framework.response import Response

from .models import VillaversoUser

from dotenv import dotenv_values
from rest_framework.decorators import api_view
from rest_framework import status

import bcrypt

import jwt

env_vars = dotenv_values('.env')

SECRET_JWT = env_vars['SECRET_JWT']


@api_view(['POST'])
def login(request):
    content = {'message': ''}
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        content['message'] = 'Email and password are required'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = VillaversoUser.objects.get(email=email)
    except VillaversoUser.DoesNotExist:
        content['message'] = 'User does not exist'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        content['message'] = 'Incorrect password'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    token = jwt.encode({'id': user.id}, SECRET_JWT, algorithm='HS256')
    content['data'] = {
        'token': token
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    print("register")
    content = {'message': ''}

    # get data from request
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')


    if not email or not password or not confirm_password:
        content['message'] = 'All fields are required'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        content['message'] = 'Passwords do not match'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        content['message'] = 'Password must be at least 8 characters long'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not any(char.isdigit() for char in password):
        content['message'] = 'Password must contain at least 1 digit'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not any(char.isupper() for char in password):
        content['message'] = 'Password must contain at least 1 uppercase character'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not any(char.islower() for char in password):
        content['message'] = 'Password must contain at least 1 lowercase character'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not any(char in ['$', '@', '#', '%', '&', '*', '!', '?'] for char in password):
        content['message'] = 'Password must contain at least 1 special character'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if VillaversoUser.objects.filter(email=email).exists():
        content['message'] = 'Email already exists'
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

    user = VillaversoUser(
        email=email,
        password=password
    )
    user.save()

    content['message'] = 'User created successfully'

    # generate token
    token = jwt.encode({'email': email}, SECRET_JWT, algorithm='HS256')

    content['data'] = {
        'token': token
    }

    return Response(content, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def me(request):
    content = {'message': ''}
    token = request.headers.get('Authorization')

    if not token:
        content['message'] = 'Token is required'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    # convert bearer token to jwt token
    token = token.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_JWT, algorithms=['HS256'])

        user = VillaversoUser.objects.get(id=payload['id'])

        content['data'] = {
            'id': user.id,
            'email': user.email,
        }

        return Response(content, status=status.HTTP_200_OK)
    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

