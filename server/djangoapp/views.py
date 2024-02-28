from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .restapis import post_request
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    return render(request, 'djangoapp/index.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp/index.html')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp/index.html')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp/index.html")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://mcmonigalr25-8000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


def get_dealer_details(request, dealer_id):
    # Specify the URL for fetching dealer reviews
    url = "https://mcmonigalr25-8000.theiadocker-1.proxy.cognitiveclass.ai/dealer/reviews"   
    # Call the get_dealer_reviews_from_cf method to fetch reviews by dealer id
    reviews = get_dealer_reviews_from_cf(url, dealer_id) 
    # Create a list to store review details
    review_details = []
    
    # Iterate through each review and append details to the list
    for review in reviews:
        # Analyze sentiment for each review
        analyze_review_sentiments(review)
        
        # Append details to the list
        review_details.append({
            'name': review.name,
            'purchase': review.purchase,
            'review': review.review,
            'purchase_date': review.purchase_date,
            'car_make': review.car_make,
            'car_model': review.car_model,
            'car_year': review.car_year,
            'sentiment': review.sentiment,
            'id': review.id,
        })
    
    # Create a context dictionary with the list of review details
    context = {
        'review_details': review_details,
    }
    
    # Return an HttpResponse with the review details
    return HttpResponse(json.dumps(context), content_type='application/json')

@login_required
def add_review(request, dealer_id):
    if request.method == 'POST':
        # Check if user is authenticated
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

        # Create a dictionary object called review
        review = {
            'time': datetime.utcnow().isoformat(),
            'name': user.username,
            'dealership': dealer_id,  # Assuming the dealership ID is passed in the URL or obtained in some way
            'review': request.POST.get('review'),
            'purchase': request.POST.get('purchase'),
        }

        # Create another dictionary object called json_payload
        json_payload = {'review': review}

        # Specify the URL for posting a review
        url = f"https://mcmonigalr25-8000.theiadocker-1.proxy.cognitiveclass.ai/dealer/{dealer_id}/reviews"

        # Call the post_request method to add the review
        response = post_request(url, json_payload, dealerId=dealer_id)

        if response:
            # Log the response in the console
            print(response)

            # You can append the response to the HTTPResponse and render it on the browser
            return JsonResponse({'status': 'success', 'response': response})
        else:
            # Return an error response
            return JsonResponse({'status': 'error', 'message': 'Failed to add review'})
    else:
        # Return a method not allowed response for non-POST requests
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)