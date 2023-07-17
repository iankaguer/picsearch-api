from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=1000)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['name', 'email', 'telephone']

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Create your models here.
class Image(models.Model):
    # image are stored in db
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images")
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="images", blank=True)

    def __str__(self):
        return self.name
