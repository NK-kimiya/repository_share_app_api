from django.db import models
from django.contrib.auth.models import  AbstractBaseUser,BaseUserManager,PermissionsMixin
import  uuid
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
# Create your models here.
def load_path_video(instance, filename):
    return '/'.join(['video', str(instance.title)+str(".mp4")])

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is must')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    def __str__(self):
        return self.email

class Room(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)  # ルームのパスワード
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    def __str__(self):
        return self.name

class Repository(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    url = models.URLField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    demo_video = models.FileField(blank=False, upload_to=load_path_video)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="repositories")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="repositories")
    categories = models.ManyToManyField("Category", related_name="repositories")

    def __str__(self):
        return self.title

class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="categories")
    def __str__(self):
        return self.name


class GitProject(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()

    subheading1 = models.CharField(max_length=200, blank=True)
    url1 = models.URLField(blank=True)

    subheading2 = models.CharField(max_length=200, blank=True)
    url2 = models.URLField(blank=True)

    subheading3 = models.CharField(max_length=200, blank=True)
    url3 = models.URLField(blank=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False)
    content = models.TextField()
    repository = models.ForeignKey(Repository,on_delete=models.CASCADE,related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Message to {self.repository.title}: {self.content[:20]}"

#リポジトリのお気に入りのモデル
class FavoriteRepository(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_repositories")
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="favorited_by")

    class Meta:
        unique_together = ('user', 'repository')  # 同じユーザーが同じリポジトリを複数回お気に入りできないように

    def __str__(self):
        return f"{self.user.email} likes {self.repository.title}"

