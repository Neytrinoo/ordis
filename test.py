from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table
import subprocess
from datetime import datetime

# clip = VideoFileClip('app/static/data/videos/user1_3.mp4')
# duration = int(clip.duration)
# res = ''
# m = duration // 60
# if m > 0:
#     duration -= m * 60
# h = duration // 3600
# if h > 0:
#     duration -= h * 3600
# res = '0' * (2 - len(str(m))) + str(m) + ':' + '0' * (2 - len(str(duration))) + str(duration)
# if h > 0:
#     res = '0' * (2 - len(str(h))) + str(h) + ':' + res
les = SingleLesson.query.filter_by(id=5).first()
les.date_added = datetime.utcnow()
db.session.commit()
