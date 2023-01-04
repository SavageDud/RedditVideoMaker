import requests
import pandas as pd
import pyttsx3
import gtts
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx.all as vfx
import random
from moviepy.config import change_settings
from better_profanity import profanity
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"})



# Settings for your api key
publickey = ''
privatekey = ''


#which subreddit to go to
Subredit = ["AskReddit"]





#settings of tts 

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

#settings of video
screensize = (1080,1920)

#importante setting of video file paths
Stock_video_file_path = ['minecraftvideoclip/minecraft1.mp4','minecraftvideoclip/minecraft2.mp4','minecraftvideoclip/minecraft3.mp4']


textgenerator = lambda txt: TextClip(txt, font='Visage Outline', fontsize=60, color='white' , kerning=-2, interline=-1,size = screensize, method='caption')

#password file
with open('password.txt', 'r') as f:
        pw = f.read()
    
data = {
        'grant_type': "password",
        "username" :"Username",
        "password" : pw }
    

auth = requests.auth.HTTPBasicAuth(publickey , privatekey)
headers = {"User-Agent" : "MyApi/0.0.1"}
    
res = requests.post("https://www.reddit.com/api/v1/access_token",auth = auth ,data = data , headers = headers)
TOKEN = res.json()['access_token']

headers = {**headers , ** {'Authorization' : f'bearer {TOKEN}'}}







def GetDataframe(subreditname):

    
    res = requests.get('https://oauth.reddit.com/r/'+subreditname+'/hot' , headers = headers)
    
    
    
    df = pd.DataFrame()
    for post in res.json()['data']["children"] :
        df = df.append({
                'subreddit' : post['data']['subreddit'],
                'title': post['data']['title'],
                'selftext': post['data']['selftext'],
                'url' :  post['data']['url'][11:]},ignore_index=True)
    
    return df
  


    

    
    
    
#get comments of video
def GetComments(link):
    commentlist = []
    request = requests.get("https://oauth"+link , headers = headers)
    for x in range(0,10):
        comment = request.json()[1]['data']['children'][x]['data']['body']
        if(len(comment) < 300 and comment == profanity.censor(comment)):
             commentlist.append(comment)
    return commentlist




# testing vuncion
def TestAllVoice():
    tts = gtts.gTTS("hello world")
    tts.save('voices/hello.mp3')



def CreateAudioFile(speach , filename , sceneindex):
    tts = gtts.gTTS(speach)
    filepath = str('voices/'+filename+str(sceneindex)+".mp3")
    tts.save(filepath)
    return filepath
    
def CreateVideo(videoname, datasetindex):
    
    name = videoframe['title'][datasetindex]
    commentlist = GetComments(videoframe['url'][datasetindex])
    audiofilepath = []
    audiofilepath.append(CreateAudioFile(name,videoname,0))
    index = 1
    for audio in commentlist:
        audiofilepath.append(CreateAudioFile(audio,videoname,index))
        index+= 1
    commentlist.insert(0 , name)
    
    CreateVideoClip(audiofilepath, commentlist,videoname)


def CreateVideoClip(audiofilepath , subtitle_text,videoname):
    
    
    audiofilelist = []
    durationcliptime = [] # important variable for adding subtitle we need to keep track of all duration of clips
    
    firstaudiofile = AudioFileClip(audiofilepath[0])
    firstSilenceClip = AudioFileClip("silence.mp3")
    
    durationcliptime.append(firstaudiofile.duration + firstSilenceClip.duration)
    
    audiofilelist.append(firstaudiofile)
    audiofilelist.append(firstSilenceClip)
    for path in range(1,len(audiofilepath)):
        if(durationcliptime[-1] > 50):
            break
        Audiofile = AudioFileClip(audiofilepath[path] )
        SilenceClip = AudioFileClip("silence.mp3")
        
        nexdurationtime = (Audiofile.duration + SilenceClip.duration + durationcliptime[-1])
        if(nexdurationtime > 50):
            break
        durationcliptime.append(nexdurationtime)
        audiofilelist.append(Audiofile)
        audiofilelist.append(SilenceClip)
        
        
    
    final_audio_clip = concatenate_audioclips(audiofilelist)
            
    chosenclipindex = random.randrange(0,len(Stock_video_file_path))
    
    
    #compute subtitles
    subtitles = []
    subtitles.append(((0,durationcliptime[0]),subtitle_text[0]))
    
    
    for subtitleindex in range(1,len(durationcliptime)):
        subtitles.append(((durationcliptime[subtitleindex - 1], durationcliptime[subtitleindex]),subtitle_text[subtitleindex]))
    
    subtitle_overlay = SubtitlesClip(subtitles, textgenerator)
    mainclip = VideoFileClip(Stock_video_file_path[chosenclipindex])
    
    clipend = random.uniform(final_audio_clip.duration , mainclip.duration)
    clipstart = clipend - final_audio_clip.duration
    CutedClip = mainclip.subclip(clipstart , clipend)
    
    finalclip = CutedClip.without_audio()
    finalclip.audio = final_audio_clip
    
    finalresult = CompositeVideoClip([finalclip , subtitle_overlay.set_pos(('center','center'))])
    finalresult.write_videofile("finalresults/"+videoname+".mp4")
    
videoframe = None
for subreditname in Subredit:
    videoframe = GetDataframe(str(subreditname))
    for videoindex in range(0,len(videoframe['title'])):
        video_name = 'video_v6_' +str(subreditname)+ str(videoindex)
        CreateVideo(video_name,videoindex)  
    
    
