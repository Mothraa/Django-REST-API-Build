from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):  # **kwargs
        if not email:
            raise ValueError("Entrer un email")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def modify_user(self, emalil, password=None):
        # pour conformité RGPD
        pass

    def delete_user(self, email, password=None, delete_confirmation=False):
        # autoriser la suppression pour conformité RGPD
        pass

    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class CustomUser(AbstractUser):

    # utilisation de l'email comme identifiant à la place du username par défaut dans AbstractUser
    # email = models.EmailField(max_length=150, unique=True, blank=False)

    # username = None
    # USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = []

    # age minimal RGPD : 15 ans // plutot mettre un champ j'ai plus de 15 ans OUI/NON ?
    age = models.PositiveIntegerField(validators=[MinValueValidator(15), MaxValueValidator(120)])

    can_be_contacted = models.BooleanField(blank=False)  # default=False
    can_data_be_shared = models.BooleanField(blank=False)  # default=False

    # nickname = models.CharField(max_length=80, unique=True, blank=False, verbose_name='Pseudo')
    # profil_photo = models.ImageField(verbose_name='Photo de profil')

    objects = CustomUserManager()
