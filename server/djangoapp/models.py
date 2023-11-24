from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
    """
    Model to save data about a car make.
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    
    def __str__(self):
        return self.name


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
    """
    Model to save data about a car model.
    """
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField() 
    name = models.CharField(max_length=100)
    
    CAR_TYPE_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Wagon', 'Wagon'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Hatchback', 'Hatchback'),
        ('Truck', 'Truck'),
    ]

    car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES)
    year = models.DateField()
    
    def __str__(self):
        return f"{self.car_make} - {self.name}"


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
