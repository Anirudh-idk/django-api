from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

# Authentication Models


class userManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        if not password:
            raise ValueError("The password must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        if not password:
            raise ValueError("The password must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.save()
        return user


class user(AbstractBaseUser):
    is_customer = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_restaurant = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, unique=True)

    USERNAME_FIELD = "email"
    objects = userManager()

    def has_module_perms(self, food):
        return True

    def has_perm(self, food):
        return True


class customer(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=80)
    lastname = models.CharField(max_length=80)


class restaurant(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    rest_name = models.CharField(max_length=80, unique=True)

    def __str__(self) -> str:
        return self.rest_name


class Dishes(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    restaurant = models.ForeignKey(to=restaurant, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    email = models.EmailField(max_length=100, unique=True)


class Cartitem(models.Model):
    dish = models.ForeignKey(to=Dishes, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()


class Orders(models.Model):
    customer = models.ForeignKey(to=user, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(to=restaurant, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=40,
        choices=[
            ("A", "Accepted"),
            ("R", "Rejected"),
            ("F", "Finished"),
            ("D", "Delivered"),
            ("W", "Waiting"),
        ],
        default="Waiting",
    )


class Orderitem(models.Model):
    dish = models.ForeignKey(to=Dishes, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(to=Orders, on_delete=models.CASCADE)


"""
class Custommanager(BaseUserManager):
    def create_user(self,email,password,type_of_user,**extra_fields):
        if not email:
            raise ValueError("No email")
        email = self.normalize_email(email)
        if type_of_user == 'R':
            user = self.model(email=email,**extra_fields)

        elif type_of_user == 'C':
            
            user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    
class Cust_User(AbstractBaseUser):
    email = models.EmailField(max_length=100,unique=True,blank=False)
    type_of_user = models.CharField(max_length=1,choices = [('R','Restaurant'),('C','Customer')],default='C')
    firstname = models.CharField(max_length=50,blank=True,null=True )
    lastname = models.CharField(max_length=50,blank=True ,null=True)
    restaurant_name = models.CharField(max_length=50,blank=True,null=True )

    USERNAME_FIELD = 'email'

    objects = Custommanager()

    def __str__(self) -> str:
        return self.email
    """
