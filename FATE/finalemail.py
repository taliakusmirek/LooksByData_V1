#import smtplib
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
#from email.mime.base import MIMEBase
#from email import encoders
#import os

def main(voguecrawler_output, articlecrawler_output, image_recognition_output, trend_prediction_output):
    return "Email sent!"
    # email all predictions to user for review -> this should be done every week, with a monthly recap email every 30 days and a future prediction email every two weeks.

#have it put into an email that i get three times each week
        #first is last weeks and initial thoughts
        #second is mid-week trend results
        #third is full week trend results

        #the begining of each month gives a review of last month's trends, and will see at mid of current month if those trends changed or not

        #every two weeks, a future prediction email will be sent out



        # Pre-Step: Establish a counter for each week to figure out what type of email to send


        # Step 1: Set up the SMTP server