from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response

from .models import VillaversoUser, House, ImageHouse, Disponibility

from dotenv import dotenv_values
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from datetime import datetime

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


@api_view(['POST'])
def create_house(request):
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

        # get data from request corresponding to house

        name = request.data.get('name')
        nbr_rooms = request.data.get('nbr_rooms')
        nbr_people = request.data.get('nbr_people')
        m2_house = request.data.get('m2_house')
        m2_garden = request.data.get('m2_garden')
        pool = False
        if request.data.get('pool') == True:
            pool = True
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        localisation = request.data.get('localisation')
        description = request.data.get('description')

        if not name or not nbr_rooms or not nbr_people or not m2_house or not m2_garden or not latitude or not longitude or not localisation or not description:
            content['message'] = 'All fields are required'
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        house = House(
            name=name,
            nbr_rooms=nbr_rooms,
            nbr_people=nbr_people,
            m2_house=m2_house,
            m2_garden=m2_garden,
            pool=pool,
            latitude=latitude,
            longitude=longitude,
            localisation=localisation,
            description=description,
            owner=user,
        )

        house.save()

        content['message'] = 'House created successfully'
        content['data'] = {
            'id': house.id,
            'name': house.name,
            'nbr_rooms': house.nbr_rooms,
            'nbr_people': house.nbr_people,
            'm2_house': house.m2_house,
            'm2_garden': house.m2_garden,
            'pool': house.pool,
            'latitude': house.latitude,
            'longitude': house.longitude,
            'localisation': house.localisation,
            'description': house.description,
            'owner': house.owner.email,
        }

        return Response(content, status=status.HTTP_200_OK)


    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_houses(request):
    houses = House.objects.all()
    images = ImageHouse.objects.all()
    content = {'message': '', 'data': []}
    for house in houses:
        house_dict = {
            'id': house.id,
            'name': house.name,
            'nbr_rooms': house.nbr_rooms,
            'nbr_people': house.nbr_people,
            'm2_house': house.m2_house,
            'm2_garden': house.m2_garden,
            'pool': house.pool,
            'latitude': house.latitude,
            'longitude': house.longitude,
            'localisation': house.localisation,
            'description': house.description,
            'owner': house.owner.email,
            'images': []
        }
        for image in images:
            if image.house.id == house.id:
                house_dict['images'].append(image.image.url)
        content['data'].append(house_dict)

    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_one_house(request, id):
    house = House.objects.get(id=id)
    images = ImageHouse.objects.filter(house=house)
    content = {'message': '', 'data': []}
    house_dict = {
        'id': house.id,
        'name': house.name,
        'nbr_rooms': house.nbr_rooms,
        'nbr_people': house.nbr_people,
        'm2_house': house.m2_house,
        'm2_garden': house.m2_garden,
        'pool': house.pool,
        'latitude': house.latitude,
        'longitude': house.longitude,
        'localisation': house.localisation,
        'description': house.description,
        'owner': house.owner.email,
        'images': []
    }
    for image in images:
        house_dict['images'].append(image.image.url)
    content['data'].append(house_dict)

    return Response(content, status=status.HTTP_200_OK)

@api_view(['POST'])
def upload_somes_images(request, home_id) :
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

        images = request.FILES.getlist('images')

        if not images:
            content['message'] = 'All fields are required'
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        house = House.objects.get(id=home_id)

        if user.id != house.owner.id:
            content['message'] = 'You are not the owner of this house'
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        for image in images:
            image_house = ImageHouse(
                house=house,
                image=image,
            )
            image_house.save()

        content['message'] = 'Image uploaded successfully'

        return Response(content, status=status.HTTP_200_OK)

    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def my_houses(request):
    content = {'message': '', 'data': []}
    token = request.headers.get('Authorization')

    if not token:
        content['message'] = 'Token is required'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    # convert bearer token to jwt token
    token = token.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_JWT, algorithms=['HS256'])

        user = VillaversoUser.objects.get(id=payload['id'])

        houses = House.objects.filter(owner=user)
        images = ImageHouse.objects.all()
        for house in houses:
            house_dict = {
                'id': house.id,
                'name': house.name,
                'nbr_rooms': house.nbr_rooms,
                'nbr_people': house.nbr_people,
                'm2_house': house.m2_house,
                'm2_garden': house.m2_garden,
                'pool': house.pool,
                'latitude': house.latitude,
                'longitude': house.longitude,
                'localisation': house.localisation,
                'description': house.description,
                'owner': house.owner.email,
                'images': []
            }
            for image in images:
                if image.house.id == house.id:
                    house_dict['images'].append(image.image.url)
            content['data'].append(house_dict)

        return Response(content, status=status.HTTP_200_OK)

    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def get_house_disponibilities(request, id):
    house = House.objects.get(id=id)
    disponibilities = Disponibility.objects.filter(house=house)
    content = {'message': '', 'data': []}
    for disponibility in disponibilities:
        disponibility_dict = {
            'id': disponibility.id,
            'start_date': disponibility.date_start,
            'end_date': disponibility.date_end,
            'house': disponibility.house.id,
        }
        content['data'].append(disponibility_dict)

    return Response(content, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
def create_disponibility(request, id):
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

        house = House.objects.get(id=id)

        if user.id != house.owner.id:
            content['message'] = 'You are not authorized to create disponibility for this house'
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not start_date or not end_date:
            content['message'] = 'All fields are required'
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')

        formatted_start_date = start_datetime.date().isoformat()
        formatted_end_date = end_datetime.date().isoformat()

        print(formatted_start_date)
        print(formatted_end_date)


        disponibility = Disponibility(
            date_start=formatted_start_date,
            date_end=formatted_end_date,
            house=house,
            status='available'
        )

        disponibility.save()

        content['message'] = 'Disponibility created successfully'
        content['data'] = {
            'id': disponibility.id,
            'start_date': disponibility.date_start,
            'end_date': disponibility.date_end,
            'house': disponibility.house.id,
            'status': disponibility.status
        }

        return Response(content, status=status.HTTP_200_OK)

    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT'])
@csrf_exempt
def update_disponibility(request, id_home, id_disponibility):
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

        house = House.objects.get(id=id_home)

        if user.id != house.owner.id:
            content['message'] = 'You are not authorized to update disponibility for this house'
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        disponibility = Disponibility.objects.get(id=id_disponibility)

        start_date = disponibility.start_date

        if request.data.get('start_date'):
            start_date = request.data.get('start_date')

        end_date = disponibility.end_date

        if request.data.get('end_date'):
            end_date = request.data.get('end_date')

        d_status = disponibility.status

        if request.data.get('status'):
            d_status = request.data.get('status')

        disponibility.start_date = start_date
        disponibility.end_date = end_date
        disponibility.status = d_status

        disponibility.save()

        content['message'] = 'Disponibility updated successfully'
        content['data'] = {
            'id': disponibility.id,
            'start_date': disponibility.start_date,
            'end_date': disponibility.end_date,
            'status': disponibility.status,
            'house': disponibility.house.id,
        }

        return Response(content, status=status.HTTP_200_OK)

    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


# write me method in django for get image and house name, upload image in folder and save path in database model ImageHouse
@api_view(['POST'])
@csrf_exempt
def upload_image(request):
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

        house_id = request.data.get('house_id')
        image = request.FILES.get('image')

        if not house_id or not image:
            content['message'] = 'All fields are required'
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        house = House.objects.get(id=house_id)

        if house.owner != user:
            content['message'] = 'You are not the owner of this house'
            return Response(content, status=status.HTTP_403_FORBIDDEN)

        new_image = ImageHouse(image=image, house=house)
        new_image.save()

        content['message'] = 'Image uploaded successfully'
        content['data'] = {
            'id': new_image.id,
            'image': new_image.image.url,
            'house': new_image.house.name,
        }

        return Response(content, status=status.HTTP_200_OK)


    except jwt.InvalidTokenError:
        content['message'] = 'Invalid token'
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)
