# main.py
from flask import Flask, render_template, request, jsonify, session
import markdown2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Supported file extensions
ALLOWED_EXTENSIONS = {'md', 'jpg', 'png'}


@app.route('/')
def index():
    # Render the main page with form
    return render_template('index.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Save the settings in the session
        session['toc_depth'] = request.form.get('toc_depth', type=int)
        session['toc_numbered'] = 'toc_numbered' in request.form
        session['toc_style'] = request.form.get('toc_style')
        # Return a preview of the TOC based on the settings
        toc_html = generate_toc(
            session['content'], session['toc_depth'], session['toc_numbered'], session['toc_style'])
        return jsonify(toc_html=toc_html)
    # Render the settings page
    return render_template('settings.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and allowed_file(uploaded_file.filename):
            file_extension = os.path.splitext(
                uploaded_file.filename)[1].lower()
            content = ''
            if file_extension in ['.jpg', '.png']:
                content = image_to_text(uploaded_file)
            elif file_extension == '.md':
                content = uploaded_file.read().decode('utf-8')
            # Save content in session for TOC preview
            session['content'] = content
            html_content, toc_html = markdown_to_html_with_toc(content)
            return render_template('preview.html', html_content=html_content, toc_html=toc_html)
    # Render the upload page
    return render_template('upload.html')

# ... (rest of the functions)


def markdown_to_html_with_toc(markdown_content):
    # Retrieve settings from session
    toc_depth = session.get('toc_depth', 3)
    toc_numbered = session.get('toc_numbered', False)
    toc_style = session.get('toc_style', 'default')

    extras = ["toc", "fenced-code-blocks"]
    html_content = markdown2.markdown(markdown_content, extras=extras)
    toc_html = generate_toc(html_content, toc_depth, toc_numbered, toc_style)
    return html_content, toc_html

# ... (rest of the code)


if __name__ == '__main__':
    app.run(debug=True)
