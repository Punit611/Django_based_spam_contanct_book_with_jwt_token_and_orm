from django.urls import path
from .views import register, login, test_token,get_user_details,\
    add_contact,mark_spam,search_person_by_name,\
    search_person_by_number,populate_data,reset_system

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('test-token/', test_token, name='test_token'),
    path('get-user/', get_user_details, name='get-user'),

    path('add-contact/', add_contact, name='add-contact'),
    path('mark-spam/', mark_spam, name='mark-spam'),
    path('search-by-name/', search_person_by_name, name='search-by-name'),
    path('search-by-number/', search_person_by_number, name='search-by-number'),
    path('populate-data/', populate_data, name='populate-data'),
    path('reset-system/',reset_system,name="rest-system")
    # other URL patterns...
]
