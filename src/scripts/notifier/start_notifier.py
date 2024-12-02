import logging
import firebase_admin
from firebase_admin import credentials
from scripts.common.model import *
from scripts.common.constants import *
from scripts.notifier.send_mail import *
from scripts.notifier.push_message import *
from datetime import datetime, timedelta

def tasks_notifier(cursor_hdl, tn_ID, p_url, p_name, tn_str_msg, tn_str_track_flag, tn_str_criteria, tn_str_recipient):
  tn_str_fdtm = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
  insert_notifier_log(cursor_hdl, tn_str_msg, tn_str_fdtm, tn_str_recipient, tn_str_track_flag, tn_str_criteria, tn_ID)
  logging.info(f'{tn_str_msg} {tn_str_track_flag} {tn_str_criteria}')

def push_notifier(product, str_track_flag, str_criteria):
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  message_data = generate_message(product, str_track_flag, str_criteria)
  send_to_multi_tokens(message_data, timestamp)

def initialize_firebase():
  certPath = "{}/../../../.keys/savyor-push-firebase-adminsdk-vd2k0.json".format(os.path.dirname(os.path.abspath(__file__)))
  try:
    cred = credentials.Certificate(certPath)
    firebase_admin.initialize_app(cred)
    print("Success to initialize firebase app")
    return True
  except:
    print("Failed to firebase")
    return False

def start_notifier():
  str_track_flg = ''
  str_criteria = ''
  str_msg = ''
  current_timestamp = datetime.now()

  if initialize_firebase() == False:
    return
  
  cursor = get_db_conn(SCRAPE_DB_NAME).cursor()
  # for failed email attempts
  for failed_track in get_failed_active_tracks(cursor):
    str_status = failed_track['Status']
    if int(failed_track['LatestPrice']) == 0:
      str_email_rtn = send_period_met(
        recipient = failed_track['LogIn_username'],
        product_url = failed_track['ProductURL'],
        picture_url = failed_track['PictureURL'],
        product_name = failed_track['ProductName'],
        current_price=failed_track['CurrentPrice'],
        target_price=failed_track['TargetPrice'],
        latest_price = failed_track['Status']
      )
    elif int(failed_track['LatestPrice']) > 0:
      str_email_rtn = send_period_met(
        recipient = failed_track['LogIn_username'],
        product_url = failed_track['ProductURL'],
        picture_url = failed_track['PictureURL'],
        product_name = failed_track['ProductName'],
        current_price=failed_track['CurrentPrice'],
        target_price=failed_track['TargetPrice'],
        latest_price = '$'+str(failed_track['LatestPrice'])
      )
    if str_email_rtn == '':
      str_email_rtn = 'Error : Sending Email'
    if str_email_rtn.find('Error') == -1: # No Error
      update_userInput_notifier(cursor, 'Period Met', failed_track['ProductURL'])
      set_flag(cursor, failed_track['ID'], 'N')  # Change “TrackActive” to N;
      str_track_flg = 'Changed To N'
    else:
      str_track_flg = 'Not Changed To N'

    recipient = failed_track['LogIn_username']
    str_criteria = 'Period Met'
    str_msg = f'{str_email_rtn}'
    push_notifier(failed_track, str_track_flg, str_criteria)
    tasks_notifier(cursor, failed_track["ID"], failed_track["ProductURL"], failed_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
  
  for active_track in get_active_tracks(cursor):
    str_status = active_track['Status']
    timestamp = active_track['TimeStamp']
    expiration_time = timestamp + timedelta(active_track['TargetPeriod'])
    expired = current_timestamp > expiration_time
    # Price Met Check & # price_drop
    # price_drop
    # I need to send a price drop notice for when the price drops (>$0.1)
    # but not yet drop to the target. In this case, a notice is sent but the
    # TrackActive will continue to be active.
    price_drop = False
    price_met = False
    price_increase = False
    if int(active_track['LatestPrice']) == 0 and str_status in ('Out Of Stock') and if_previously_Outofstock(cursor, active_track['ID']):
      continue
    if int(active_track['LatestPrice']) > 0 and str_status not in ('Could Not Get Price (Other)','CAPTCHA Found','Price Range'):
      price_met = float(active_track['LatestPrice']) <= float(active_track['TargetPrice'])
      if float(active_track['LatestPrice']) > float(active_track['CurrentPrice']):
        int_increase = round((float(active_track['CurrentPrice']) - float(active_track['LatestPrice'])),2)
        if verify_price_increase(cursor, active_track['ID'], int_increase, active_track['LatestPrice']):
          update_price_increase(cursor, active_track['ID'], int_increase)
          price_increase = True
        else:
          continue
      elif not price_met : # if price Not Met, then Check for Price Drop
        int_drop = round((float(active_track['LastPrice']) - float(active_track['LatestPrice'])), 2)
        if int_drop < 0:
          int_drop = float(active_track['LatestPrice']) < float(active_track['CurrentPrice'])
        if float(active_track['LastPrice']) == float(active_track['LatestPrice']) and not if_previously_Outofstock(cursor, active_track['ID']):
          update_userInput_scrapper(cursor, float(active_track['LatestPrice']), str_status, str(active_track['ProductURL']))
          continue
        if int_drop > 0.00:
          update_price_drop(cursor, active_track['ID'], int_drop)
        if int_drop > 0.00 and float(active_track['LatestPrice']) < float(active_track['CurrentPrice']) and verify_price_drop(cursor, active_track['ID'], int_drop,active_track['LatestPrice']):
          price_drop = True

    # print(str_status, price_drop, if_previously_Instock(cursor, active_track['ID']), expired, price_increase, price_met)
    recipient = active_track['LogIn_username']
    if str_status == 'Product Not Found (404 ERROR)':
      str_email_rtn = send_404(
          recipient=active_track['LogIn_username'],
          product_url=active_track['ProductURL'],
          picture_url=active_track['PictureURL'],
          product_name=active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price=''
      )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, '404 ERROR', active_track['ProductURL'])

      str_track_flg = 'Changed To N'
      set_flag(cursor, active_track['ID'], 'N')
      str_criteria = 'Product Not Found (404 ERROR)'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
    elif str_status == 'Out Of Stock' and if_previously_Instock(cursor, active_track['ID']):   # ONLY if 'Out Of Stock' , This makes sure to send ONLY ONE email.
      if int(active_track['LatestPrice']) > 0:
        str_email_rtn = send_out_of_stock(
          recipient=active_track['LogIn_username'],
          product_url=active_track['ProductURL'],
          picture_url=active_track['PictureURL'],
          product_name=active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price='$'+str(active_track['LatestPrice'])
        )
      elif int(active_track['LatestPrice']) == 0:
        str_email_rtn = send_out_of_stock(
          recipient=active_track['LogIn_username'],
          product_url=active_track['ProductURL'],
          picture_url=active_track['PictureURL'],
          product_name=active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price=str_status
        )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'Out Of Stock', active_track['ProductURL'])

      str_track_flg = 'Not Changed To N'
      str_criteria = 'Out Of Stock'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), str_status, str(active_track['ProductURL']))
    elif str_status == "In Stock" and if_previously_Outofstock(cursor, active_track['ID']) and not price_drop:
      str_email_rtn = send_back_in_stock(
        recipient=active_track['LogIn_username'],
        price_difference= round( (active_track['CurrentPrice'] - active_track['LatestPrice']),2) ,
        product_url=active_track['ProductURL'],
        picture_url=active_track['PictureURL'],
        product_name=active_track['ProductName'],
        current_price=active_track['CurrentPrice'],
        target_price=active_track['TargetPrice'],
        latest_price=active_track['LatestPrice']
      )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor,'In Stock', active_track['ProductURL'])

      str_track_flg = 'Not Changed To N'
      str_criteria = 'Back Not Met'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), str_status, str(active_track['ProductURL']))
    elif str_status == "In Stock" and if_previously_Outofstock(cursor, active_track['ID']) and price_drop:
      str_email_rtn = send_back_price_met(
        recipient=active_track['LogIn_username'],
        price_difference=round( (active_track['CurrentPrice'] - active_track['LatestPrice']),2),
        product_url=active_track['ProductURL'],
        picture_url=active_track['PictureURL'],
        product_name=active_track['ProductName'],
        current_price=active_track['CurrentPrice'],
        target_price=active_track['TargetPrice'],
        latest_price=active_track['LatestPrice']
      )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'In Stock', active_track['ProductURL'])
        set_flag(cursor, active_track['ID'], 'N')
        str_track_flg = 'Changed To N'
      else:
        str_track_flg = 'Not Changed To N'

      str_criteria = 'Back Price Met'
      str_msg = f'{str_email_rtn}'
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), str_status, str(active_track['ProductURL']))
    elif expired:
      if int(active_track['LatestPrice']) == 0:
        str_email_rtn = send_period_met(
          recipient = active_track['LogIn_username'],
          product_url = active_track['ProductURL'],
          picture_url = active_track['PictureURL'],
          product_name = active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price = active_track['Status']
        )
      elif int(active_track['LatestPrice']) > 0:
        str_email_rtn = send_period_met(
          recipient = active_track['LogIn_username'],
          product_url = active_track['ProductURL'],
          picture_url = active_track['PictureURL'],
          product_name = active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price = '$'+str(active_track['LatestPrice'])
        )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'Period Met', active_track['ProductURL'])
        set_flag(cursor, active_track['ID'], 'N')  # Change “TrackActive” to N;
        str_track_flg = 'Changed To N'
      else:
        str_track_flg = 'Not Changed To N'

      str_criteria = 'Period Met'
      str_msg = f'{str_email_rtn}'
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), 'In Stock', str(active_track['ProductURL']))
    elif price_increase:
      str_email_rtn = send_price_increase(
        recipient=active_track['LogIn_username'],
        price_difference=abs(round((active_track['CurrentPrice'] - active_track['LatestPrice']), 2)),
        product_url=active_track['ProductURL'],
        picture_url=active_track['PictureURL'],
        product_name=active_track['ProductName'],
        current_price=active_track['CurrentPrice'],
        target_price=active_track['TargetPrice'],
        latest_price="$" + str(active_track['LatestPrice'])
      )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'In Stock', active_track['ProductURL'])
  
      str_track_flg = 'Not Changed To N'
      str_criteria = 'Price Increase'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), 'In Stock', str(active_track['ProductURL']))
    elif price_met:
      if int(active_track['LatestPrice']) == 0:
        str_email_rtn = send_price_met(
          recipient = active_track['LogIn_username'],
          price_difference = round( (active_track['CurrentPrice'] - active_track['LatestPrice']),2) ,
          product_url = active_track['ProductURL'],
          picture_url = active_track['PictureURL'],
          product_name = active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price = active_track['Status']
        )
      elif int(active_track['LatestPrice']) > 0:
        str_email_rtn = send_price_met(
          recipient=active_track['LogIn_username'],
          price_difference=round((active_track['CurrentPrice'] - active_track['LatestPrice']), 2),
          product_url=active_track['ProductURL'],
          picture_url=active_track['PictureURL'],
          product_name=active_track['ProductName'],
          current_price=active_track['CurrentPrice'],
          target_price=active_track['TargetPrice'],
          latest_price="$"+str(active_track['LatestPrice'])
        )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'Price Met', active_track['ProductURL'])
        set_flag(cursor, active_track['ID'], 'N')  # Change “TrackActive” to N;
        str_track_flg = 'Changed To N'
      else:
        str_track_flg = 'Not Changed To N'

      str_criteria = 'Price Met'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), 'In Stock', str(active_track['ProductURL']))
    elif price_drop:
      str_email_rtn = send_price_drop(
        recipient = active_track['LogIn_username'],
        price_difference = round( (active_track['CurrentPrice'] - active_track['LatestPrice']), 2),
        product_url = active_track['ProductURL'],
        picture_url = active_track['PictureURL'],
        product_name = active_track['ProductName'],
        current_price=active_track['CurrentPrice'],
        target_price=active_track['TargetPrice'],
        latest_price = "$"+str(active_track['LatestPrice'])
      )
      if str_email_rtn == '':
        str_email_rtn = 'Error : Sending Email'
      if str_email_rtn.find('Error') == -1:  # No Error
        update_userInput_notifier(cursor, 'In Stock', active_track['ProductURL'])

      str_track_flg = 'Not Changed To N'
      str_criteria = 'Price Drop'
      str_msg = f'{str_email_rtn} '
      push_notifier(active_track, str_track_flg, str_criteria)
      tasks_notifier(cursor, active_track["ID"], active_track["ProductURL"], active_track["ProductName"], str_msg, str_track_flg, str_criteria, recipient)
      update_userInput_scrapper(cursor, float(active_track['LatestPrice']), 'In Stock', str(active_track['ProductURL']))
  
  get_db_conn(SCRAPE_DB_NAME).commit()
  cursor.close()

  get_db_conn(TARGET_DB_NAME).cursor().close()