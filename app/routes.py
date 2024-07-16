from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, mail
from app.forms import (RegistrationForm, LoginForm, UpdateProfileForm, PostForm, 
                       CommentForm, ArticleForm, ForumForm, BlogForm, RequestResetForm, 
                       ResetPasswordForm, SearchForm, MessageForm)
from app.models import User, Post, Comment, Article, Forum, Blog, Notification, Message, Reply
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import os
import secrets
from werkzeug.utils import secure_filename

def save_file(form_file):
    try:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_file.filename)
        file_fn = random_hex + f_ext
        file_path = os.path.join(app.root_path, 'static/uploads', file_fn)
        form_file.save(file_path)
        return file_fn
    except Exception as e:
        flash(f'An error occurred while saving the file: {e}', 'danger')
        return None


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    articles = Article.query.order_by(Article.date_posted.desc()).all()
    forums = Forum.query.order_by(Forum.date_created.desc()).all()
    blogs = Blog.query.order_by(Blog.date_posted.desc()).all()
    return render_template('home.html', posts=posts, articles=articles, forums=forums, blogs=blogs)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('home'))


def save_picture(form_file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(app.root_path, 'static/Profiles', file_fn)
    form_file.save(file_path)
    return file_fn

@app.route("/update_profile", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        if form.profile_image.data:
            profile_img = save_picture(form.profile_image.data)
            current_user.profile_image = profile_img
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    return render_template('update_profile.html', title='Update Profile', form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        if form.file.data:
            file_name = save_file(form.file.data)
            post.file = file_name
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, file=post.file)

@app.route("/post/<int:post_id>/comment", methods=['GET', 'POST'])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('comment.html', title='New Comment', form=form, legend='New Comment')

@app.route("/articles")
def articles():
    articles = Article.query.all()
    return render_template('articles.html', articles=articles)

@app.route("/article/new", methods=['GET', 'POST'])
@login_required
def new_article():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, content=form.content.data, author=current_user)
        if form.file.data:
            file_name = save_file(form.file.data)
            article.file = file_name
        db.session.add(article)
        db.session.commit()
        flash('Your article has been published!', 'success')
        return redirect(url_for('home'))
    return render_template('create_article.html', title='New Article', form=form)

@app.route("/article/<int:article_id>", methods=['GET', 'POST'])
def article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', title=article.title, article=article, file=article.file)

@app.route("/forums")
def forums():
    forums = Forum.query.all()
    return render_template('forums.html', forums=forums)

@app.route("/forum/new", methods=['GET', 'POST'])
@login_required
def new_forum():
    form = ForumForm()
    if form.validate_on_submit():
        forum = Forum(name=form.name.data, description=form.description.data, author=current_user)
        if form.file.data:
            file_name = save_file(form.file.data)
            forum.file = file_name
        db.session.add(forum)
        db.session.commit()
        flash('Your forum has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_forum.html', title='New Forum', form=form, legend='New Forum')

@app.route("/forum/<int:forum_id>", methods=['GET', 'POST'])
def forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    return render_template('forum.html', title=forum.name, forum=article, file=forum.file)

@app.route("/blogs")
def blogs():
    blogs = Blog.query.all()
    return render_template('blogs.html', blogs=blogs)

@app.route("/blog/new", methods=['GET', 'POST'])
@login_required
def new_blog():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, content=form.content.data, creator=current_user)
        if form.file.data:
            file_name = save_file(form.file.data)
            blog.file = file_name
            db.session.add(blog)
            db.session.commit()
            flash('Your blog has been posted!', 'success')
            return redirect(url_for('home'))
    return render_template('create_blog.html', title='New Blog', form=form)

@app.route("/blog/<int:blog_id>", methods=['GET', 'POST'])
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog.html', title=blog.title, blog=blog, file=blog.file)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.search.data
        posts = Post.query.filter(Post.content.contains(query) | Post.title.contains(query)).all()
        articles = Article.query.filter(Article.content.contains(query) | Article.title.contains(query)).all()
        forums = Forum.query.filter(Forum.title.contains(query) | Forum.description.contains(query)).all()
        blogs = Blog.query.filter(Blog.content.contains(query) | Blog.title.contains(query)).all()
        return render_template('search_results.html', query=query, posts=posts, articles=articles, forums=forums, blogs=blogs)
    return render_template('search.html', form=form)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/user/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
    article = Article.query.filter_by(author=user).all()
    return render_template('user_posts.html', posts=posts, user=user)



@app.route("/user/<username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    articles = Article.query.filter_by(author=user)
    blogs = Blog.query.filter_by(author=user)
    forums = Forum.query.filter_by(creator=user)
    return render_template('user_profile.html', user=user, articles=articles, blogs=blogs, forums=forums)


@app.route("/notifications")
@login_required
def notifications():
    notifications = current_user.notifications.order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route("/message/new", methods=['GET', 'POST'])
@login_required
def new_message():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if recipient:
            message = Message(current_user, recipient, form.content.data)
            db.session.add(message)
            db.session.commit()
            flash('Your message has been sent!', 'success')
            return redirect(url_for('messages'))
        else:
            flash('Recipient not found!', 'danger')
    return render_template('create_message.html', title='New Message', form=form)

@app.route("/messages")
@login_required
def messages():
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
    received_messages = current_user.received_messages.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', sent_messages=sent_messages, received_messages=received_messages)

@app.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot follow yourself!', 'danger')
        return redirect(url_for('user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!', 'success')
    return redirect(url_for('user_profile', username=username))

@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot unfollow yourself!', 'danger')
        return redirect(url_for('user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {username}.', 'success')
    return redirect(url_for('user_profile', username=username))

@app.route("/chat")
@login_required
def chat():
    return render_template('chat.html', title='Chat Room')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.likes is None:
        post.likes = 0
    post.likes += 1
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route('/unlike_post/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.likes is None:
        post.likes = 0
    if post.likes > 0:
        post.likes -= 1
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route('/repost/<int:post_id>', methods=['POST'])
@login_required
def repost(post_id):
    # Logic to repost
    post = Post.query.get_or_404(post_id)
    new_post = Post(title=post.title, content=post.content, author=current_user)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('post', post_id=new_post.id))

@app.route('/share/<int:post_id>', methods=['POST'])
@login_required
def share(post_id):
    post = Post.query.get_or_404(post_id)
    new_post = Post(title=post.title, content=post.content, author=current_user)
    db.session.add(new_post)
    db.session.commit()
    flash('Post shared successfully!', 'success')
    return redirect(url_for('post', post_id=new_post.id))

@app.route('/post_comment/<int:post_id>', methods=['POST'])
@login_required
def post_comment(post_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, author=current_user, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    # Logic to like a comment
    comment = Comment.query.get_or_404(comment_id)
    comment.likes += 1
    db.session.commit()
    return redirect(request.referrer)

@app.route('/unlike_comment/<int:comment_id>', methods=['POST'])
@login_required
def unlike_comment(comment_id):
    # Logic to unlike a comment
    comment = Comment.query.get_or_404(comment_id)
    comment.likes -= 1
    db.session.commit()
    return redirect(request.referrer)

@app.route('/reply_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def reply_comment(comment_id):
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            reply = Reply(content=content, author=current_user, comment_id=comment_id)
            db.session.add(reply)
            db.session.commit()
        return redirect(request.referrer)
    return render_template('reply.html', comment_id=comment_id)
