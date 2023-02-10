import streamlit as st
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
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
        
        final_wav_path = SAVE_PATH + output_file + ".wav"
        final.write_audiofile(final_wav_path)
        
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "njain_be20@thapar.edu"  # Enter your address
        receiver_email = email_id  # Enter receiver address

        # Add body to email

        print("Email sent!")
        
        # assert type(receiver_email)==list
        zip_file = final_wav_path + ".zip"
        with zipfile.ZipFile(zip_file, 'w') as myzip:
            myzip.write(final_wav_path)

        msg = MIMEMultipart()
        msg.attach(MIMEText("Mashup of " + singer_name + " - Nitansh Jain - 102017025", "plain"))
        
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = "Mashup of " + singer_name + " - Nitansh Jain - 102017025"


        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(zip_file,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(zip_file)))
        msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('youremail@example.com', 'yourpassword')
        smtp.sendmail(from_addr = "youremail@example.com", to_addrs = receiver_email, msg = msg.as_string())
        smtp.close()

        os.remove(zip_file)

        
    else:
        st.warning("Please fill all the fields")
