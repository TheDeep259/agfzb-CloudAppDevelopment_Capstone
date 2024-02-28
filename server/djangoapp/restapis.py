import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key), params=kwargs)
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def post_request(url, json_payload, **kwargs):
    """
    Perform HTTP POST request with JSON payload.
    
    Parameters:
    - url (str): The URL for the POST request.
    - json_payload (dict): The JSON payload to be sent.
    - kwargs (dict): Additional parameters for the request.
    
    Returns:
    - dict: The JSON response from the server.
    """
    try:
        # Call post method of requests library with URL, JSON payload, and parameters
        response = requests.post(url, json=json_payload, params=kwargs, 
                                 headers={'Content-Type': 'application/json'},
                                 auth=HTTPBasicAuth('apikey', 'your_api_key'))
        
        # Check if the request was successful (status code 2xx)
        response.raise_for_status()
        
        # Parse the JSON response
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        # Handle exceptions if any
        print(f"Error in POST request: {e}")
        return None

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            print("DEaler",dealer_doc)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


def get_dealer_reviews_from_cf(url, dealer_id, api_key):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result
        
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            # Create a DealerReview object with values in `doc` object
            review_obj = DealerReview(
                dealership=review_doc.get("dealership", ""),
                name=review_doc.get("name", ""),
                purchase=review_doc.get("purchase", ""),
                review=review_doc.get("review", ""),
                purchase_date=review_doc.get("purchase_date", ""),
                car_make=review_doc.get("car_make", ""),
                car_model=review_doc.get("car_model", ""),
                car_year=review_doc.get("car_year", ""),
                sentiment="Unknown",  # Initialize sentiment as Unknown
                id=review_doc.get("id", "")
            )
            
            # Analyze sentiment and update the sentiment attribute of the review_obj
            analyze_review_sentiments(review_obj, api_key)

            results.append(review_obj)

    return results

def analyze_review_sentiments(dealerreview, api_key):
    # Watson NLU URL for sentiment analysis
    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/your_instance_id/v1/analyze'

    # Parameters for sentiment analysis
    params = {
        "text": dealerreview.review,
        "version": "2021-08-01",
        "features": "sentiment",
        "return_analyzed_text": True
    }

    try:
        # Call get_request with specified arguments
        response = get_request(url, api_key=api_key, **params)
        
        # Get the sentiment label from the response
        sentiment_label = response.get("sentiment", {}).get("document", {}).get("label", "Unknown")

        # Update the sentiment attribute of the dealerreview object
        dealerreview.sentiment = sentiment_label

    except Exception as e:
        print(f"Error analyzing sentiments: {e}")

