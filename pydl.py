from pytube import YouTube,streams
import os
import subprocess
from progressbar import ProgressBar


def progress_Check(stream = None, chunk = None, bytes_remaining = None, file_handle = None):
    percent = (100*(file_size-bytes_remaining))/file_size
    pbar.update(percent)


def nonprogressive(stream,path,res,cnt=1):
    global file_size
    file_size = 0
    print("started downloading video and audio")
    file_size=stream.filter(type="video",res=res).first().filesize+stream.filter(type="audio",).order_by('abr').last().filesize
    if stream.filter(type="video",res=res).count():
        stream.filter(type="video",res=res).first().download(output_path=path,filename="vid.mp4")
    else:
        return False
    stream.filter(type="audio",).order_by('abr').last().download(output_path=path,filename="aud.mp3")
    return True


def progressive(stream,res,title,path):
    global file_size
    file_size = 0
    file_size=(stream.filter(progressive=True,res=res).first()).filesize
    stream.filter(progressive=True,res=res).first().download(output_path=path,filename=title+".mp4")


def merger(path,title):#todo make a progress bar for merging progress
    os.chdir(path)
    h264=f'ffmpeg -i vid.mp4 -i aud.mp3 -c:v copy -c:a aac merged.mp4'
    h265=f'ffmpeg -i vid.mp4 -i aud.mp3 -c:v libx265 -crf 26 -preset ultrafast -c:a aac merged.mp4'
    subprocess.run(h264,shell=True)
    os.rename("merged.mp4",f"{title}.mp4")
    os.remove("vid.mp4")
    os.remove("aud.mp3")
    print("downloaded")

def available_resolutions(stream):
    global reslist
    reslist={"2160p":0,"1440p":0,"1080p":0,"720p":0,"480p":0,"360p":0,"240p":0,"144p":0}

    for i in reslist:
        print(stream.filter(res=i))
        if len(stream.filter(res=i))>0:
            reslist[i]=1
    print(reslist)
    print("list of availabe resolutions")
    for j in reslist:
        if reslist[j]>=1:
            print(j)

#url of the video from youtube
url="https://www.youtube.com/watch?v=T0F_LpEjKbY"

#path to downloads or #to-do define path for user needed
path=os.environ['USERPROFILE']+"\\Downloads"

#youtube object is created with url to praise the infos of the url :progress_check is for progress tracking
vidobj=YouTube(url,on_progress_callback=progress_Check)

#stream variable holds the stream query of the url 
#stream query is used for the availabe video formats(Res,progressvive,codec) and audio formats(opus,av1,abs=bitrate) 

stream=vidobj.streams
#available_resolustions is used to find the avialabe res on that url for precautionary 
available_resolutions(stream)
# res holds the resolution we want

try:
    res=input("enter the resolution which are available:")
    if "p"not in res and "P" not in res:
        res+="p"
    elif res[-1]=="P":
        res=res[:-1]+"p"
    if res not in reslist or reslist[res]==0:
        raise ValueError
except ValueError:
    print("The resoultion entered is not available or mistyped resolution")
    res=input("enter the resolution which are available:")
    if res not in reslist:
        print("The resoultion entered is not available or mistyped resolution")
        print("restart the script :-(")
print(res)
breakpoint()
title="".join(vidobj.title.split("|"))

pbar = ProgressBar().start()

if not len(stream.filter(progressive=True,res=res)) or stream.filter(progressive=True,res=res).count()==0 :
    print("non progressive")
    merger(path,title) if nonprogressive(stream,path,res) else print("resolution Not found") #downloads non progress(vdieo and then audio seperately)files
    pbar.finish()

else:
    print("progressive")
    progressive(stream,res,title,path,)#downloads progress(vdieo+audio) file
    pbar.finish()
    print("downloaded")
