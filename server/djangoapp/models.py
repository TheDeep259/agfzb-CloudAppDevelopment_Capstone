from django.db import models
from django.utils.timezone import now

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.description}"

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=30)
    dealer_ID = models.IntegerField()
    type_choices = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('wagon', 'Wagon'),
        ('hatchback', 'Hatchback'),
        ('convertible', 'Convertible')
    ]
    type = models.CharField(max_length=15, choices=type_choices)
    year = models.DateField(null=True)
    colour = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year.year}) - {self.type} ({self.colour})"


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
