import datetime
import json
from firebase_admin import messaging
from scripts.common.model import *

def send_to_token(device_token, message_data):
  # See documentation on defining a message payload.
  message = messaging.Message(
    data = message_data,
    token=device_token,
  )

  # Send a message to the device corresponding to the provided
  # registration token.
  response = messaging.send(message)
  # Response is a message ID string.
  print('Successfully sent message:', response)
  # [END send_to_token]


def send_to_multi_tokens(message_data, timestamp):
  devices = get_push_devices(message_data['recipient'])
  
  if len(devices) == 0:
    return

  device_tokens = []
  for device in devices:
    device_tokens.append(device[0])
  
  message = messaging.MulticastMessage(
    data={
      'product_url': message_data['product_url'],
      'recipient': message_data['recipient'],
    },
    tokens=device_tokens,
    notification=messaging.Notification(
      title=message_data['title'],
      body=message_data['body'],
      image=message_data['image'],
    ),
    android=messaging.AndroidConfig(
      ttl=datetime.timedelta(seconds=3600),
      priority='normal',
    ),
    apns=messaging.APNSConfig(
      payload=messaging.APNSPayload(
        aps=messaging.Aps(badge=42),
      ),
    ),
  )
  message_id = add_push_message(
    message_token=message_data['recipient'], 
    content=json.dumps(message_data),
    tokens=len(device_tokens), 
    timestamp=timestamp
  )
  message.data['message_id'] = str(message_id)
  response = messaging.send_multicast(message)

  if response.success_count > 0:
    print('Successfully sent message to: ', message_data['recipient'])

  responses = response.responses
  for idx, resp in enumerate(responses):
    if not resp.success:
      print('Firebase Error============================')
      print(resp.__dict__)
    create_push_receipt(
      device_token=device_tokens[idx], 
      message_token=message_id, 
      status = 'success' if resp.success else 'fail', 
      timestamp=timestamp
    )
  # [END send_to_multi_tokens]


def generate_message(product, track_flag, criteria):
  template = {
    'title': '',
    'body': '',
    'image': 'https://savyor.co{}'.format(product['PictureURL']),
    'recipient': product['LogIn_username'],
    'product_url': product['ProductURL']
  }

  price_difference = round((product['CurrentPrice'] - product['LatestPrice']), 2)

  if criteria == "Period Met":
    template['title'] = "Time is Up!"
    template['body'] = "Hey there, the item you tracked does not drop to your target price, ${} in time.".format(product['TargetPrice'])
  
  elif criteria == "Product Not Found (404 ERROR)":
    template['title'] = "Gone in the Wind"
    template['body'] = "My friend, the retailer has removed the product you tracked from its website."
  
  elif criteria == "Out Of Stock":
    template['title'] = "Out of Stock"
    template['body'] = "Heads up, the item you are tracking appears to be out of stock at this point."
  
  elif criteria == "Back Not Met":
    template['title'] = "Baby Comes Back"
    template['body'] = "Wake up! The item previously out of stock is now back in stock!!"
  
  elif criteria == "Back Price Met":
    template['title'] = "Believe it or Not"
    template['body'] = "Stop dreaming! The item you tracked has just returned back to stock and dropped its price to give you a total saving of ${}!!".format(price_difference)
  
  elif criteria == "Price Increase":
    template['title'] = "Price Increase Alert"
    template['body'] = "Hey there, the item you track just increased its price by ${}.".format(price_difference)
  
  elif criteria == "Price Met":
    template['title'] = "Price Drop Notice"
    template['body'] = "You lucky baby, the item you tracked has just dropped its price to give you a total saving of ${}!!".format(price_difference)
  
  elif criteria == "Price Drop":
    template['title'] = "Price Drop Notice"
    template['body'] = "time to wake up, the item you tracked has just dropped its price to give you a total saving of ${} even though it has not drop to your target.".format(price_difference)
  
  else:
    template['title'] = "Product Update Notice"
    template['body'] = "Hey there, just want to let you know that the item you tracked has been updated."
    
  return template


def send_to_topic():
  # [START send_to_topic]
  # The topic name can be optionally prefixed with "/topics/".
  topic = 'highScores'

  # See documentation on defining a message payload.
  message = messaging.Message(
    data={
      'score': '850',
      'time': '2:45',
    },
    topic=topic,
  )

  # Send a message to the devices subscribed to the provided topic.
  response = messaging.send(message)
  # Response is a message ID string.
  print('Successfully sent message:', response)
  # [END send_to_topic]


def send_to_condition():
  # [START send_to_condition]
  # Define a condition which will send to devices which are subscribed
  # to either the Google stock or the tech industry topics.
  condition = "'stock-GOOG' in topics || 'industry-tech' in topics"

  # See documentation on defining a message payload.
  message = messaging.Message(
    notification=messaging.Notification(
      title='$GOOG up 1.43% on the day',
      body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
    ),
    condition=condition,
  )

  # Send a message to devices subscribed to the combination of topics
  # specified by the provided condition.
  response = messaging.send(message)
  # Response is a message ID string.
  print('Successfully sent message:', response)
  # [END send_to_condition]


def send_dry_run():
  message = messaging.Message(
    data={
      'score': '850',
      'time': '2:45',
    },
    token='token',
  )

  # [START send_dry_run]
  # Send a message in the dry run mode.
  response = messaging.send(message, dry_run=True)
  # Response is a message ID string.
  print('Dry run successful:', response)
  # [END send_dry_run]


def android_message():
  # [START android_message]
  message = messaging.Message(
    android=messaging.AndroidConfig(
      ttl=datetime.timedelta(seconds=3600),
      priority='normal',
      notification=messaging.AndroidNotification(
        title='$GOOG up 1.43% on the day',
        body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        icon='stock_ticker_update',
        color='#f45342'
      ),
    ),
    topic='industry-tech',
  )
  # [END android_message]
  return message


def apns_message():
  # [START apns_message]
  message = messaging.Message(
    apns=messaging.APNSConfig(
      headers={'apns-priority': '10'},
      payload=messaging.APNSPayload(
        aps=messaging.Aps(
          alert=messaging.ApsAlert(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
          ),
          badge=42,
        ),
      ),
    ),
    topic='industry-tech',
  )
  # [END apns_message]
  return message


def webpush_message():
  # [START webpush_message]
  message = messaging.Message(
    webpush=messaging.WebpushConfig(
      notification=messaging.WebpushNotification(
        title='$GOOG up 1.43% on the day',
        body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        icon='https://my-server/icon.png',
      ),
    ),
    topic='industry-tech',
  )
  # [END webpush_message]
  return message


def all_platforms_message():
  # [START multi_platforms_message]
  message = messaging.Message(
    notification=messaging.Notification(
      title='$GOOG up 1.43% on the day',
      body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
    ),
    android=messaging.AndroidConfig(
      ttl=datetime.timedelta(seconds=3600),
      priority='normal',
      notification=messaging.AndroidNotification(
        icon='stock_ticker_update',
        color='#f45342'
      ),
    ),
    apns=messaging.APNSConfig(
      payload=messaging.APNSPayload(
        aps=messaging.Aps(badge=42),
      ),
    ),
    topic='industry-tech',
  )
  # [END multi_platforms_message]
  return message


def subscribe_to_topic():
  topic = 'highScores'
  # [START subscribe]
  # These registration tokens come from the client FCM SDKs.
  device_tokens = [
    'YOUR_REGISTRATION_TOKEN_1',
    # ...
    'YOUR_REGISTRATION_TOKEN_n',
  ]

  # Subscribe the devices corresponding to the registration tokens to the
  # topic.
  response = messaging.subscribe_to_topic(device_tokens, topic)
  # See the TopicManagementResponse reference documentation
  # for the contents of response.
  print(response.success_count, 'tokens were subscribed successfully')
  # [END subscribe]


def unsubscribe_from_topic():
  topic = 'highScores'
  # [START unsubscribe]
  # These registration tokens come from the client FCM SDKs.
  device_tokens = [
    'YOUR_REGISTRATION_TOKEN_1',
    # ...
    'YOUR_REGISTRATION_TOKEN_n',
  ]

  # Unubscribe the devices corresponding to the registration tokens from the
  # topic.
  response = messaging.unsubscribe_from_topic(device_tokens, topic)
  # See the TopicManagementResponse reference documentation
  # for the contents of response.
  print(response.success_count, 'tokens were unsubscribed successfully')
  # [END unsubscribe]


def send_all():
  device_token = 'YOUR_REGISTRATION_TOKEN'
  # [START send_all]
  # Create a list containing up to 500 messages.
  messages = [
    messaging.Message(
      notification=messaging.Notification('Price drop', '5% off all electronics'),
      token=device_token,
    ),
    # ...
    messaging.Message(
      notification=messaging.Notification('Price drop', '2% off all books'),
      topic='readers-club',
    ),
  ]

  response = messaging.send_all(messages)
  # See the BatchResponse reference documentation
  # for the contents of response.
  print('{0} messages were sent successfully'.format(response.success_count))
  # [END send_all]


def send_multicast():
  # [START send_multicast]
  # Create a list containing up to 500 registration tokens.
  # These registration tokens come from the client FCM SDKs.
  device_tokens = [
    'YOUR_REGISTRATION_TOKEN_1',
    # ...
    'YOUR_REGISTRATION_TOKEN_N',
  ]

  message = messaging.MulticastMessage(
    data={'score': '850', 'time': '2:45'},
    tokens=device_tokens,
  )
  response = messaging.send_multicast(message)
  # See the BatchResponse reference documentation
  # for the contents of response.
  print('{0} messages were sent successfully'.format(response.success_count))
  # [END send_multicast]

