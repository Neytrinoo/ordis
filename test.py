from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table, AttachedFile
import subprocess
from datetime import datetime
from zipfile import ZipFile

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
# for i in range(1, 16):
#     file = AttachedFile.query.filter_by(id=i).first()
#     file.filename = 'att_file' + '.' + file.file_path.split('.')[-1]
#     db.session.commit()
# with ZipFile('app/static/data/attached_files_archives/archive.zip', 'w') as myzip:
#     myzip.write('app/static/data/attached_files/user1_1_2.psd', arcname='asdf.psd')
les = SingleLesson.query.filter_by(id=1).first()
les.rating_influence_comments= 0
db.session.commit()