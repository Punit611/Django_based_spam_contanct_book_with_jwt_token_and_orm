from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User

from .data_population import generate_sample_data
from .serializers import UserSerializer
from .models import CustomUser as User
from .models import PhoneNumber,OtherName


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    user_details = {
        'phone_number': user.phone_number,
        'email': user.email,
        'name':user.name
        # Include any other user details you want to expose
    }
    return Response(user_details)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_contact(request):
    user = request.user
    contacts = request.data.get('contacts', [])
    for contact in contacts:
        name = contact.get('name')
        number = contact.get('number')
        if(not name or not number):
            continue

        other_name, created = OtherName.objects.get_or_create(number=number, name=name,user=user.phone_number)
        if created:
            other_name.save()
        print(other_name,created)
    return Response(contacts)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mark_spam(request):
    user = request.user
    phone_number = request.query_params.get('phone_number')
    print(phone_number)
    if phone_number:
        try:
            other_names = OtherName.objects.filter(number=phone_number)
            other_names.update(is_spam=True)

            phone_number_list = PhoneNumber.objects.filter(number=phone_number)
            phone_number_list.update(is_spam=True)
            return Response({'detail': 'Phone number marked as spam.'}, status=200)
        except PhoneNumber.DoesNotExist:
            return Response({'detail': 'Phone number not found.'}, status=404)
    else:
        return Response({'detail': 'Please provide a phone number.'}, status=400)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_person_by_name(request):
    name = request.query_params.get('name', '')

    # Search for PhoneNumbers that match the query
    results = PhoneNumber.objects.filter(verified_name__icontains=name)
    other_name_results = OtherName.objects.filter(name__icontains=name)

    # Sort the results based on name matching
    sorted_results = sorted(results, key=lambda x: x.verified_name.startswith(name), reverse=True)
    other_name_sorted_results = sorted(other_name_results, key=lambda x: x.name.startswith(name), reverse=True)

    # Prepare the response data
    response_data = []
    for result in sorted_results:
        response_data.append({
            'name': result.verified_name,
            'phone_number': result.number,
            'spam_likelihood': result.is_spam,
            'registered': True,
        })
    for result in other_name_sorted_results:
        response_data.append({
            'name': result.name,
            'phone_number': result.number,
            'spam_likelihood': result.is_spam,
            'registered':False,
        })

    return Response(response_data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_person_by_number(request):
    phone_number = request.query_params.get('phone_number', '')
    user = request.user
    print(phone_number)
    if(not phone_number):
        return Response({'detail': 'Please provide a phone number.'}, status=400)
    # Search for a registered user with the given phone number
    registered_user = PhoneNumber.objects.filter(number=phone_number).first()
    contact_book = False
    email = ""

    if registered_user:
        results = OtherName.objects.filter(number=user.phone_number, user=registered_user.number)
        if results:
            contact_book = True

    if registered_user:
        # If a registered user is found, return only that result
        response_data = [{
            'name': registered_user.verified_name,
            'phone_number': registered_user.number,
            'spam_likelihood': registered_user.is_spam,
            'registered': True,
            'email': registered_user.email if contact_book else ""
        }]
    else:
        # If no registered user is found, search for all PhoneNumbers matching the phone number
        results = OtherName.objects.filter(number=phone_number)
        print(results)
        # Prepare the response data
        response_data = []
        for result in results:
            response_data.append({
                'name': result.name,
                'phone_number': phone_number,
                'spam_likelihood': result.is_spam,
                'registered': False,
                'user':result.user,

            })

    return Response(response_data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def populate_data(request):
    size = request.query_params.get('data_size', 5)

    generate_sample_data(size)
    return Response({'detail': 'Data population is done.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reset_system(request):
    PhoneNumber.objects.all().delete()
    Token.objects.all().delete()
    OtherName.objects.all().delete()
    User.objects.all().delete()

    return Response({'detail': 'System data is reset.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user, token = serializer.save()

        phone_number = PhoneNumber.objects.create(
            number=user.phone_number,
            verified_name=user.name,
            is_spam=False,
        )
        # phone_number.other_names.add(*other_names)
        phone_number.save()
        print(type(phone_number),phone_number)
        response_data = {
            'detail': 'User registered successfully.',
            'token': token.key,
            'user': {
                'name': user.name,
                'email': user.email,
                'phone_number': user.phone_number,
                # Include any other user details you want to include
            },
            'phone': {
                'verified_name': phone_number.verified_name,
                'phone_number': phone_number.number,
                # Include any other user details you want to include
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    user = User.objects.filter(phone_number=phone_number).first()
    if user and user.check_password(password):
        token, created = Token.objects.get_or_create(user=user)

        # Access the token value
        user_token = token.key
        print(user_token)
        return Response({'token': str(user_token)}, status=status.HTTP_200_OK)
    return Response({'detail': 'Invalid phone number or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def test_token(request):
    return Response({'detail': 'Token is valid.'}, status=status.HTTP_200_OK)
