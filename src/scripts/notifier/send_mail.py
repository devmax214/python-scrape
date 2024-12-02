import smtplib
from email.message import EmailMessage
from email.header import Header
from email.utils import formataddr
from jinja2 import Template
import logging
import os
from scripts.common.constants import *

def send_base_email(message):
	str_log_txt = ''
	try:
		with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.ehlo()

			smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
			smtp.send_message(message)

	except smtplib.SMTPRecipientsRefused as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except smtplib.SMTPHeloError as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except smtplib.SMTPSenderRefused as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except smtplib.SMTPDataError as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except smtplib.SMTPNotSupportedError as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except smtplib.SMTPException as err:
		str_log_txt = f'Send Error: Unsuccessful: Email {str(err)}'
	except OSError as err:
		str_log_txt = f'SMTP Error:Unsuccessful: Email {str(err)}'
	except Exception as err:
		str_log_txt = f'Email Error:Unsuccessful: Email {str(err)}'
	else:
		str_log_txt = f'Successful: Email Sent '
	finally:
		logging.info(str_log_txt)
		return str_log_txt

def send_error_email(recipient, msg):
	message = EmailMessage()
	message['Subject'] = 'Oh something crashed'
	message['From'] = formataddr((str(Header('Alert from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient
	message.set_content(msg)
	return send_base_email(message)

def send_out_of_stock(recipient, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Oh snap something is missing…'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))  
	message['To'] = recipient

	strPath = "{}/templates/out_of_stock.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = 0,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_404(recipient, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Product not found - 404'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/404_not_found.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			ProductURL=product_url,
			PictureURL=picture_url,
			ProductName=product_name,
			CurrentPrice=current_price,
			TargetPrice=target_price,
			LatestPrice=latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_back_in_stock(recipient, price_difference, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Knock, knock, who’s there?'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/back_in_stock.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = price_difference,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)


def send_back_price_met(recipient, price_difference, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Knock, knock,Savyor got you savings!'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/back_price_met.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = price_difference,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_price_met(recipient, price_difference, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Savyor got you savings!'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/index_price_met.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = price_difference,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_price_increase(recipient, price_difference, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Something is definitely up....'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/price_increase.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = price_difference,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_price_drop(recipient, price_difference, product_url, picture_url, product_name, current_price, target_price, latest_price):
	# price_drop
	# I need to send a price drop notice for when the price drops (>$0.1)
	# but not yet drop to the target. In this case, a notice is sent but the
	# TrackActive will continue to be active.

	message = EmailMessage()
	message['Subject'] = 'Savyor got you savings!'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/index_price_drop.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			PriceDifference = price_difference,
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice = target_price,
			LatestPrice = latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)

def send_period_met(recipient, product_url, picture_url, product_name, current_price, target_price, latest_price):
	message = EmailMessage()
	message['Subject'] = 'Price track period is up'
	message['From'] = formataddr((str(Header('News from Savyor', 'utf-8')), EMAIL_ADDRESS))
	message['To'] = recipient

	strPath = "{}/templates/index_period_met.html".format(os.path.dirname(os.path.abspath(__file__)))
	with open(strPath) as f:
		template = Template(f.read()).render(
			ProductURL = product_url,
			PictureURL = picture_url,
			ProductName = product_name,
			CurrentPrice = current_price,
			TargetPrice= target_price,
			LatestPrice= latest_price
		)
	message.add_alternative(template, subtype='html')
	return send_base_email(message)