from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Entrer un nom d'utilisateur")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        superuser = self.create_user(username, password, **extra_fields)
        return superuser

    def modify_user(self, emalil, password=None):
        # pour conformité RGPD
        pass

    def delete_user(self, email, password=None, delete_confirmation=False):
        # autoriser la suppression pour conformité RGPD
        pass


class CustomUser(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=150, unique=True, blank=False)
    # email = models.EmailField(max_length=150, unique=True, blank=False)
    age = models.PositiveIntegerField(validators=[MinValueValidator(15), MaxValueValidator(120)],
                                      blank=True,
                                      null=True)
    can_be_contacted = models.BooleanField(blank=False, default=False)
    can_data_be_shared = models.BooleanField(blank=False, default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # last_login
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
