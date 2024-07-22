# Biodiversity Nexus Forum

Welcome to the Biodiversity Nexus Forum, an online platform dedicated to connecting conservation enthusiasts, researchers, and students. This forum provides a space for sharing knowledge, discussing biodiversity topics, and collaborating on conservation projects.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture and Technologies](#architecture-and-technologies)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Development](#development)
7. [Contributing](#contributing)
8. [License](#license)
9. [Contact](#contact)

## Project Overview

The Biodiversity Nexus Forum aims to facilitate discussions on biodiversity and conservation, share research findings, and foster collaboration among members. The platform includes features such as user registration, discussion forums, article and blog posting, commenting and replying, and post interactions like liking, unliking, sharing, and reposting.

## Features

- **User Registration and Authentication**: Secure login and user management.
- **Discussion Forums**: Topic-based forums for discussions.
- **Article and Blog Posting**: Members can share articles and blogs.
- **Commenting and Replying**: Engage in conversations through comments and replies.
- **Post Interactions**: Like, unlike, share, and repost features.

## Architecture and Technologies

### Architecture

- **Frontend**: HTML, CSS, JavaScript (Bootstrap for responsiveness)
- **Backend**: Flask (Python)
- **Database**: SQLAlchemy (SQLite)

### Technologies

- **Flask**: For building the web application.
- **Flask-Login**: For user authentication and session management.
- **SQLAlchemy**: For database interactions.
- **Jinja2**: For templating.

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/Desire-2/biodiversity-nexus-forum.git
    cd biodiversity-nexus-forum
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
      ```sh
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```sh
      source venv/bin/activate
      ```

4. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

5. **Set up the database**:
    ```sh
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6. **Run the application**:
    ```sh
    flask run
    ```

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000`.
2. Register a new user account.
3. Log in with your credentials.
4. Start participating in discussions, posting articles, and interacting with posts.

## Development

### Adding New Features

To add new features or make improvements:

1. **Create a new branch**:
    ```sh
    git checkout -b feature-name
    ```

2. **Implement your changes** and **commit them**:
    ```sh
    git commit -m "Description of feature"
    ```

3. **Push to your branch**:
    ```sh
    git push origin feature-name
    ```

4. **Create a pull request** on GitHub.

### Handling Errors

To ensure error messages are displayed correctly for duplicate usernames or emails during registration:

```python
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
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)
```

### Error Handlers

Implement custom error handlers to provide user-friendly error messages:

```python
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/feature-name`)
3. Commit your Changes (`git commit -m 'Add some feature'`)
4. Push to the Branch (`git push origin feature/feature-name`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Desire Bikorimana - [Your Email](mailto:bikorimanadesire@yahoo.com)

Project Link: [https://github.com/your-username/biodiversity-nexus-forum](https://github.com/Desire-2/biodiversity-nexus-forum)
