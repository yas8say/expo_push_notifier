import json
import requests
from firebase_admin import credentials, initialize_app
from exponent_server_sdk import PushClient, PushMessage, DeviceNotRegisteredError, PushServerError, PushTicketError
from requests.exceptions import ConnectionError, HTTPError

# Initialize Firebase Admin SDK with the Service Account Key
cred = credentials.Certificate("/home/ismail-baig/frappe-bench/apps/expo_push_notifier/expo_push_notifier/expo_push_notifier/al-ummah-app-firebase-adminsdk-fbsvc-034b0d4fcf.json")
firebase_app = initialize_app(cred)

# Function to send a push notification
def send_push_message(token, message, extra=None):
    print(token)
    try:
        # Set up session with Firebase authentication
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Bearer {cred.get_credential().token}",
                "accept": "application/json",
                "accept-encoding": "gzip, deflate",
                "content-type": "application/json",
            }
        )

        # Create a PushMessage object with the target token, message body, and optional extra data
        push_message = PushMessage(
            to=token,  # The device push token
            body=message,  # The message you want to send
            data=extra  # Any additional data you want to send along with the notification (optional)
        )

        # Send the push notification using the PushClient
        push_client = PushClient(session=session)
        response = push_client.publish(push_message)

    except PushServerError as exc:
        # Encountered some likely formatting/validation error. Handle the error.
        print(f"Push Server Error: {exc.errors}")
        raise exc
    except (ConnectionError, HTTPError) as exc:
        # Encountered some connection or HTTP error - retry a few times if transient.
        print(f"Connection Error: {exc}")
        raise exc

    # Validate the response
    try:
        response.validate_response()
    except DeviceNotRegisteredError:
        # If the device is not registered, mark the push token as inactive
        print(f"Device token {token} is not registered.")
        # Handle token invalidation logic if needed
    except PushTicketError as exc:
        # Handle errors specific to the push notification
        print(f"Push Ticket Error: {exc.push_response._asdict()}")
        raise exc

    # If the push was successfully sent
    print("Push notification sent successfully!")
    return response
