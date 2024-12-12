import json
from flask import Flask, render_template, request, redirect, url_for

JSON_PATH = 'data.json'

app = Flask(__name__)


def load_data():
    """
    Loads data from the JSON file specified by JSON_PATH.

    Returns:
        list: A list of posts if the file exists and contains valid JSON.
        dict: An empty list if the file is missing, empty, or corrupted.
    """
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as file:
            print(f"Data successfully read from {JSON_PATH}.")
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {JSON_PATH}. Creating a new empty database.")
        return []
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. The file might be empty or corrupted.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return []


def get_data():
    """
    Provides cached access to the data from the JSON file.
    Loads data from the file if it is not already cached.

    Returns:
        list: The cached data loaded from the JSON file.
    """
    if not hasattr(get_data, "_cache"):
        get_data._cache = load_data()
    return get_data._cache


def save_data(data):
    """
    Saves the provided data to the JSON file specified by JSON_PATH.

    Args:
        data (list): The list of posts to save.

    Returns:
        None
    """
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
            print(f"Data successfully saved to {JSON_PATH}.")
    except Exception as e:
        print(f"Error: An unexpected error occurred while saving data: {e}")


@app.route('/')
def index():
    """
    Renders the home page with a list of blog posts.

    Returns:
        str: Rendered HTML of the index page.
    """
    return render_template('index.html', posts=get_data())


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    """
    Deletes a blog post with the specified ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: A redirect to the index page.
    """
    data = get_data()
    for post in data:
        if post['id'] == post_id:
            data.remove(post)
    save_data(data)
    return redirect(url_for('index'))


@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    """
    Increments the like count of a blog post with the specified ID.

    Args:
        post_id (int): The ID of the post to like.

    Returns:
        Response: A redirect to the index page.
    """
    data = get_data()
    for post in data:
        if post['id'] == post_id:
            post['likes'] += 1
    save_data(data)
    return redirect(url_for('index'))


@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    """
    Updates a blog post with the specified ID.

    GET: Renders a form to update the blog post.
    POST: Updates the post with the submitted data and saves it.

    Args:
        post_id (int): The ID of the post to update.

    Returns:
        str: Rendered HTML of the update page (GET).
        Response: A redirect to the index page (POST).
    """
    updated_post = None
    data = get_data()
    for post in data:
        if post['id'] == post_id:
            updated_post = post
    if updated_post is None:
        return "Post not found", 404

    if request.method == 'POST':
        updated_post['author'] = request.form.get('author')
        updated_post['content'] = request.form.get('content')
        save_data(data)
        return redirect(url_for('index'))

    return render_template('update.html', post=updated_post)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Adds a new blog post.

    GET: Renders a form to create a new blog post.
    POST: Creates a new blog post with the submitted data and saves it.

    Returns:
        str: Rendered HTML of the add page (GET).
        Response: A redirect to the index page (POST).
    """
    data = get_data()
    highest_id = max([post['id'] for post in data], default=0)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        content = request.form.get('content')

        new_post = {
            'id': highest_id + 1,
            'author': author,
            'title': title,
            'content': content,
            'likes': 0,
        }
        data.append(new_post)
        save_data(data)
        return redirect(url_for('index'))

    return render_template('add.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
