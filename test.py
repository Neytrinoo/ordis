from app.models import User, MetaTags, Interests, interests_table, meta_tags_table
from app import db

User.query.delete()
MetaTags.query.delete()
Interests.query.delete()
interests_table.delete()
meta_tags_table.delete()
db.session.commit()