from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from django.conf import settings
from rest_framework import status
from django.contrib.auth.models import User
from .models import Profile, Cat, CommunityCat, Thread, Comment, AdoptionRequest
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import os

class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='StrongP@ssw0rd!')
        self.profile = Profile.objects.create(user=self.user, bio='', profile_picture='') 

    def test_homepage_authenticated(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    def test_homepage_unauthenticated(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

    def test_sign_up_valid(self):
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'StrongP@ssw0rd!',
            'password2': 'StrongP@ssw0rd!',
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_sign_in_valid(self):
        self.client.post(reverse('sign_up'), {
            'username': 'signinuser',
            'email': 'signinuser@example.com',
            'first_name': 'Sign',
            'last_name': 'In',
             'password1': 'StrongP@ssw0rd!',
             'password2': 'StrongP@ssw0rd!',
        })
        response = self.client.post(reverse('sign_in'), {
            'username': 'signinuser',
            'password': 'StrongP@ssw0rd!',
        })
        self.assertEqual(response.status_code, 302) 

    def test_profile_detail_authenticated(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def create_image(self):
            image = Image.new('RGB', (100, 100), color='red')
            byte_io = io.BytesIO()
            image.save(byte_io, 'JPEG')
            byte_io.seek(0)
            return InMemoryUploadedFile(byte_io, 'ImageField', 'test_image.jpg', 'image/jpeg', byte_io.getbuffer().nbytes, None)

    def test_adoption_form(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')

        # Use the create_image method to generate a test image
        profile_picture = self.create_image()

        response = self.client.post(reverse('adoption'), {
            'name': 'Fluffy',
            'age': 2,
            'breed': 'Persian',
            'description': 'Fluffy cat',
            'profile_picture': profile_picture,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cat.objects.filter(name='Fluffy').exists())

    def test_handle_adoption(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        cat = Cat.objects.create(name='Fluffy', age=2, breed='Persian', description='Fluffy cat', submitted_by=self.user)
        response = self.client.post(reverse('handle_adoption'), json.dumps({'cat_id': cat.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AdoptionRequest.objects.filter(user=self.user, cat=cat).exists())

    def test_create_thread(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        response = self.client.post(reverse('api_create_thread'), {
            'title': 'New Thread',
            'content': 'This is the content of the thread',
            'image': 'path/to/image.jpg'
        })
        self.assertEqual(response.status_code, 201)  # Redirects
        self.assertTrue(Thread.objects.filter(title='New Thread').exists())

    def test_create_comment(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        thread = Thread.objects.create(title='Test Thread', content='Content', author=self.user)
        response = self.client.post(reverse('create_comment', args=[thread.id]), {
            'content': 'This is a comment'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Comment.objects.filter(content='This is a comment').exists())

    def test_create_checkout_session(self):
        response = self.client.post(reverse('create_checkout_session'), {'amount': 100})
        self.assertEqual(response.status_code, 201)
        self.assertIn('sessionId', json.loads(response.content))


class UserProfileTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongP@ssw0rd!')
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        self.profile = Profile.objects.create(user=self.user, bio='')

    def test_update_profile(self):
        url = reverse('api_profile')  # Ensure this matches the URL pattern for the API endpoint
        data = {'bio': 'testBio'}
        response = self.client.put(url, data, format='json')
        
        # Check that the response status code is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Reload the profile from the database to verify the change
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'testBio')
        
        # Optionally, you can also check the response content
        self.assertEqual(response.data['bio'], 'testBio')


class CommunityCatTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongP@ssw0rd!')
        self.client.login(username='testuser', password='StrongP@ssw0rd!')

    def create_image(self):
        image = Image.new('RGB', (100, 100), color='red')
        byte_io = io.BytesIO()
        image.save(byte_io, 'JPEG')
        byte_io.seek(0)
        return InMemoryUploadedFile(byte_io, 'ImageField', 'test_image.jpg', 'image/jpeg', byte_io.getbuffer().nbytes, None)

    def test_community_cat_list(self):
        CommunityCat.objects.create(
            name='Test Cat',
            cat_img=self.create_image(),
            location='Test Location',
            description='Test Description',
            last_seen='2024-08-22',
            reported_by=self.user
        )
        
        url = reverse('list_community_cats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_search_community_cat(self):
        CommunityCat.objects.create(
            name='Test Cat 1',
            cat_img=self.create_image(),
            location='Location 1',
            description='Description 1',
            last_seen='2024-08-22',
            reported_by=self.user
        )
        CommunityCat.objects.create(
            name='Test Cat 2',
            cat_img=self.create_image(),
            location='Location 2',
            description='Description 2',
            last_seen='2024-08-22',
            reported_by=self.user
        )
        
        url = reverse('search_community_cats') + '?q=Test Cat 1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Cat 1')

    def test_submit_community_cat_valid(self):
        # Path to the image in the static files directory
        image_path = os.path.join(settings.BASE_DIR, 'prototypeApp', 'static', 'cat1.jpg')
        
        # Open the image file and create SimpleUploadedFile
        with open(image_path, 'rb') as image_file:
            cat_img = SimpleUploadedFile('cat1.jpg', image_file.read(), content_type='image/jpeg')

        url = reverse('submit_community_cat')
        data = {
            'name': 'New Community Cat',
            'location': 'New Location',
            'description': 'New Description',
            'last_seen': '2024-08-22',
            'cat_img': cat_img,  # Ensure the image field is provided
        }
        
        # Perform the POST request
        response = self.client.post(url, data, format='multipart')
        # Assert the response and existence of the new entry
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(CommunityCat.objects.filter(name='New Community Cat').exists())

    def test_submit_community_cat_invalid(self):
        url = reverse('submit_community_cat')
        data = {
            'name': '',  # Invalid because 'name' cannot be empty
            'location': 'New Location',
            'description': 'New Description',
            'last_seen': '2024-08-22',
        }
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)


class ExtendedUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='StrongP@ssw0rd!')
        self.profile = Profile.objects.create(user=self.user, bio='', profile_picture='')

    def test_sign_up_invalid(self):
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'StrongP@ssw0rd!',
            'password2': 'WeakPassword',
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the same page with errors
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_handle_adoption_invalid_cat(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        response = self.client.post(reverse('handle_adoption'), json.dumps({'cat_id': 999}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_create_thread_invalid(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        response = self.client.post(reverse('api_create_thread'), {
            'title': '',
            'content': 'This is the content of the thread',
        })
        self.assertEqual(response.status_code, 302)  # Invalid data

    def test_create_comment_invalid(self):
        self.client.login(username='testuser', password='StrongP@ssw0rd!')
        thread = Thread.objects.create(title='Test Thread', content='Content', author=self.user)
        response = self.client.post(reverse('create_comment', args=[thread.id]), {
            'content': '',  # Empty content
        })
        self.assertEqual(response.status_code, 400)  # Invalid data

    def test_stripe_checkout_invalid_amount(self):
        response = self.client.post(reverse('create_checkout_session'), {'amount': -1})
        self.assertEqual(response.status_code, 400)  # Invalid amount
