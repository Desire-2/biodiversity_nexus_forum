from app import db
from models import Post

posts = Post.query.filter(Post.likes == None).all()
for post in posts:
    post.likes = 0
    db.session.add(post)
db.session.commit()
