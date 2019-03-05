from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table
import subprocess

clip = VideoFileClip('app/static/data/videos/user1_1.mp4')
print(clip.duration)