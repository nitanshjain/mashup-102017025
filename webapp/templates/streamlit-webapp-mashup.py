import streamlit as st
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import numpy as np
from detect_delimiter import detect
import scipy.stats as ss
import sys
import os

import urllib.request
import re
import sys
import os
from pytube import YouTube
from youtubesearchpython import VideosSearch
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import *
import os, sys, time, threading, multiprocessing, random as r
import zipfile

def mashup(name, num_videos, cut_duration):
    # input_args = sys.argv
    # name = input_args[1]
    # num_videos = input_args[2]
    # cut_duration = input_args[3]
    # output_file = input_args[4]
    search_query = name.replace(' ', '+')

    # getting links based on search query
    videosSearch = VideosSearch(search_query, limit=int(num_videos))
    x = videosSearch.result()
    links = list()
    for i in range(int(num_videos)+1):
        try:
            links.append(x['result'][i]['link'])
        except:
            videosSearch.next()
        if i==20:
            videosSearch.next()
        

    # downloading videos
    SAVE_PATH = os.getcwd() + '/'
    for link in links:
        try:
            yt = YouTube(link)
            if yt.length < 400:
                YouTube(link).streams.filter().first().download(SAVE_PATH)
        except:
            continue
        
        
    # converting videos to audio and cutting them to cut_duration time    
    i=0    
    for filename in os.listdir(SAVE_PATH):
        f = os.path.join(SAVE_PATH + filename)
        # checking if it is a file
        if os.path.isfile(f):
            if f==SAVE_PATH + '.DS_Store':
                os.remove(f)
                continue
            try:
                clip = VideoFileClip(f).subclip(0, int(cut_duration))
                os.remove(f)
                clip.audio.write_audiofile(SAVE_PATH + str(i) + ".wav")
                i = i+1
            except:
                continue
            
            
    # merging audio files into one file
    wavs = [
        SAVE_PATH + "/" + wav for wav in os.listdir(SAVE_PATH) if wav.endswith(".wav")
    ]
    final_clip = concatenate_audioclips([AudioFileClip(wav) for wav in wavs])
    
    return final_clip


PASSWORD = st.secrets["PASSWORD"]
st.set_page_config(page_title="Mashup - Nitansh Jain - 102017025", page_icon=":guardsman:", layout="wide")

singer_name = st.text_input("Singer Name")
num_of_videos = st.text_input("Number of videos")
dur = st.text_input("Duration of each video")
output_file = st.text_input("Output file name")
email_id = st.text_input("Email ID", key='email')

if st.button("Submit"):
    if singer_name and num_of_videos and dur and email:
        st.success("Form submitted successfully!")

        final = mashup(singer_name, num_of_videos, dur)
        SAVE_PATH = os.getcwd() + '/'
        
        final_wav_path = SAVE_PATH + "/" + output_file + ".wav"
        final.write_audiofile(final_wav_path)
        myzip = zipfile.ZipFile(SAVE_PATH + "/" + output_file + ".zip", 'w')
        myzip.write(final, myzip)
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "njain_be20@thapar.edu"  # Enter your address
        receiver_email = email_id  # Enter receiver address

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Mashup of " + singer_name + " - Nitansh Jain - 102017025"

        # Add body to email
        message.attach(MIMEText("Mashup of " + singer_name + " - Nitansh Jain - 102017025", "plain"))
        with open(myzip,'rb') as file:
        # Attach the file with filename to the email
            message.attach(MIMEApplication(file, Name=SAVE_PATH + "/" + output_file + ".zip"))
            
        # # Open PDF file in bynary
        # with open(myzip, "rb") as attachment:
        #     # Add file as application/octet-stream
        #     # Email client can usually download this automatically as attachment
        #     # print(attachment)
        #     part = MIMEBase("application", "zip")
        #     part.set_payload((attachment).read())

        

        # Add attachment to message and convert message to string
        # message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, PASSWORD)
            server.sendmail(sender_email, receiver_email, text)

        print("Email sent!")

        
    else:
        st.warning("Please fill all the fields")
