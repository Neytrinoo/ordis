from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db
from moviepy.editor import *
import os, sys
from app.models import VideoLesson, SingleLesson, MetaTagsLesson, meta_tags_lesson_table
import subprocess

print(SingleLesson.query.filter_by(id=1).first().meta_tags)
