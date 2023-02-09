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

def mashup():
    input_args = sys.argv
    name = input_args[1]
    num_videos = input_args[2]
    cut_duration = input_args[3]
    output_file = input_args[4]
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
    final_wav_path = SAVE_PATH + "/" + output_file + ".wav"
    wavs = [
        SAVE_PATH + "/" + wav for wav in os.listdir(SAVE_PATH) if wav.endswith(".wav")
    ]
    final_clip = concatenate_audioclips([AudioFileClip(wav) for wav in wavs])
    final_clip.write_audiofile(final_wav_path)
    final_clip.close()
    print("Done merging wavs to " + final_wav_path)
    
    return 

mashup()

