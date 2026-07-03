from django.contrib.auth.models import AbstractUser
from django.db import models

# here i used django built in user model and i custmize the user model for email. 
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User' # admin dashboard better view
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email