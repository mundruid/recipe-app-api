from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicaly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login ise required accross the endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        res.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApuTests(TestCase):
    """ Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """"Test retrieving a list of ingredients"""
        Ingredients.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test the ingredients for the authenticated user are returned"""
        user2 = get_user_model().create_user(
            'other@test.com',
            'testpass'
        )

        Ingredient.objects.create(user=user2, name='Vinegar')

        ingt