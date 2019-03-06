from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table
import subprocess

clip = VideoFileClip('G:/SecondYearYandexLyceum/проект Pygame/videogame.mp4')
duration = int(clip.duration)
res = ''
m = duration // 60
if m > 0:
    duration -= m * 60
h = duration // 3600
if h > 0:
    duration -= h * 3600
res = str(m) + ':' + str(duration)
if h > 0:
    res = str(h) + ':' + res
les = SingleLesson.query.filter_by(id=4).first()
les.duration = res
db.session.commit()