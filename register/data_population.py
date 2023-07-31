import random
import string
from django.contrib.auth import get_user_model
from register import models
from faker import Faker

fake = Faker()
User = get_user_model()


# Generate and save sample data
def generate_sample_data(num_records):
    for _ in range(num_records):

        # Generate random
        phone_number = fake.phone_number()
        verified_name = fake.name()
        email = fake.email()
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))


        # Create a CustomUser instance
        user = User.objects.create_user(
            phone_number=phone_number,
            name=verified_name,
            email=email,
            password=password
        )
        # Save the CustomUser instance
        user.save()

        print(verified_name,password,email,phone_number)

        # Create a PhoneNumber instance
        phone_number_obj = models.PhoneNumber.objects.create(
            number=phone_number,
            verified_name=verified_name,
            is_spam = random.choice([True, False])
        )
        phone_number_obj.save()

        # Generate random OtherName data
        for _ in range(random.randint(0, 5)):
            name = fake.name()
            number = fake.phone_number()
            is_spam = random.choice([True, False])
            print("---> ",name,number,is_spam)
            # Create an OtherName instance
            contact_obj=models.OtherName.objects.create(
                name=name,
                number=number,
                is_spam=is_spam,
                user=phone_number_obj.number
            )
            contact_obj.save()


