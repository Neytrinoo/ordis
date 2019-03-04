from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table
import subprocess

meta_tags_lesson_table.drop(db.engine)
db.session.commit()
