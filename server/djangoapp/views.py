from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake, CarDealer, DealerReview
from .restapis import get_request, get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.contrib.auth.decorators import login_required

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        # pull from dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # check auth
        user = authenticate(username=username, password=password) 
        if user is not None:
            # login if valid
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # get user from session id
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    # redirect back to the index.html
    return render(request, 'djangoapp/index.html', context)

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # rend if it is a GET req
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # get user info
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            # create new user
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://kevinraguett-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        
        # Get dealers from the URL
        context = {
            "dealerships": get_dealers_from_cf(url),
        }
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
     if request.method == "GET":
         context = {}
         dealer_url = "https://kevinraguett-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
         dealer = get_dealer_by_id_from_cf(dealer_url, id = id)
         context['dealer'] = dealer

         review_url = "https://kevinraguett-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
         reviews = get_dealer_reviews_from_cf(review_url, id = id)
         context["reviews"] = reviews

         return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
@login_required
def add_review(request, id):
    context = {}
    dealer_url = "https://kevinraguett-3000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    
    # Get dealer information
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer
    
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            car_id = request.POST.get("car")
            
            # Get car information
            car = CarModel.objects.get(pk=car_id)
            
            # Prepare payload for the review
            payload = {
                "time": datetime.utcnow().isoformat(),
                "name": username,
                "dealership": id,
                "id": id,
                "review": request.POST.get("content"),
                "purchase": request.POST.get("purchasecheck") == 'on',
                "purchase_date": request.POST.get("purchasedate"),
                "car_make": car.car_make.name,
                "car_model": car.name,
                "car_year": int(car.year.strftime("%Y"))
            }
            
            # Prepare payload for the API request
            new_payload = {"review": payload}
            review_post_url = "https://kevinraguett-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            
            # Make the POST request
            post_request(review_post_url, new_payload, id=id)
            
            return redirect("djangoapp:dealer_details", id=id)
        else:
            # Handle the case where the user is not authenticated
            messages.error(request, "Please log in to add a review !!")
            return render(request, 'djangoapp/index.html')
