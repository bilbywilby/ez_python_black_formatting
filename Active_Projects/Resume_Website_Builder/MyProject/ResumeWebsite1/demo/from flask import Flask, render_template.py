from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_babel import Babel, gettext
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email
import markdown
import os
import fitz
import pdfkit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated_resumes'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Bootstrap instance
bootstrap = Bootstrap(app)

# Flask-Babel instance
babel = Babel(app)


# Define allowed file function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Define the form class to represent user input
class ResumeForm(FlaskForm):
    name = StringField(gettext('Name'), validators=[InputRequired()])
    email = StringField(gettext('Email'), validators=[
                        InputRequired(), Email()])
    phone = StringField(gettext('Phone'), validators=[InputRequired()])
    bio = TextAreaField(gettext('Bio'), validators=[InputRequired()])
    education = TextAreaField(
        gettext('Education'), validators=[InputRequired()])
    work = TextAreaField(gettext('Work Experience'),
                         validators=[InputRequired()])
    skills = TextAreaField(gettext('Skills'), validators=[InputRequired()])
    certification = TextAreaField(
        gettext('Certification'), validators=[InputRequired()])
    submit = SubmitField('Submit')


# Define the index page route
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ResumeForm()
    if request.method == 'POST':
        resume_html = parse_resume(request)
    else:
        resume_html = render_template('resume_template.html')
    return render_template('index.html', form=form, resume_html=resume_html)


# Parse the resume and generate the HTML output
def parse_resume(request):
    text_fields = ['name', 'email', 'phone', 'bio',
                   'education', 'work', 'skills', 'certification']
    user_input = {}
    for field in text_fields:
        user_input[field] = request.form[field]

    # Save input to file
    filename = save_to_file(user_input)

    # Parse Resume
    parser = ResumeParser(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    content = parser.parse()

    # Generate HTML
    generator = ResumeGenerator(content)
    generated_html = generator.generate_html()

    # Save HTML to file
    generated_filename = f'{filename.rsplit(".", 1)[0]}.html'
    generated_filepath = os.path.join(
        app.config['GENERATED_FOLDER'], generated_filename)
    with open(generated_filepath, 'w', encoding="utf-8") as generated_file:
        generated_file.write(generated_html)

    return generated_html


# Saves submitted input to file
def save_to_file(input_data):
    filename = f'{secure_filename(input_data["name"])}.txt'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'w') as file:
        for field, value in input_data.items():
            file.write(f'{field.capitalize()}\n{value}\n\n')
    return filename


# Parse the text from the uploaded file
class ResumeParser:
    def __init__(self, filepath):
        self._filepath = filepath

    def _extract_text(self):
        with fitz.open(self._filepath) as doc:
            text = ""
            for page in doc:
                text += '\n' + page.get_text(' ') + '\n'
            return text

    def parse(self):
        text = self._extract_text()
        return self._split_sections(text)

    def _split_sections(self, text):
        sections = {}
        text = text.split('\n')
        current_section = None
        for line in text:
            line = line.strip()
            if not line:
                continue
            if line.lower() in ['skills', 'certifications', 'education', 'experience']:
                sections[line.lower()] = []
                current_section = line.lower()
            else:
                if current_section is not None:
                    sections[current_section].append(line)
        return sections


# Generate HTML
class ResumeGenerator:
    def __init__(self, content):
        self._content = content

    def generate_html(self):
        output = ""
        for section, text in self._content.items():
            output += markdown.markdown(f'### {section.capitalize()}')
            output += markdown.markdown("\n".join(text))
        return output


# Generates PDF from HTML
class PDFGenerator:
    def __init__(self, input_html, output_pdf_name):
        self._input_html = input_html
        self._output_pdf_name = output_pdf_name
        self._options = {
            'page-size': 'Letter',
            'margin-top': '0.25in',
            'margin-right': '0.25in',
            'margin-bottom': '0.25in',
            'margin-left': '0.25in',
            'encoding': "UTF-8",
            'no-outline': '',
            'dpi': 300,
            'quiet': ''
        }

    def generate_pdf(self):
        pdfkit.from_string(
            self._input_html, self._output_pdf_name, options=self._options)


# Route to handle file uploads
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash(gettext('Please select a file!'), 'danger')
            return redirect(request.url)

        file = request.files['file']
        # Check that a file was selected and is allowed
        if file.filename == '':
            flash(gettext('Please select a file!'), 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(gettext('File uploaded successfully'), 'success')
            return redirect(url_for('index'))
        else:
            flash(gettext('Invalid file format. Please upload a PDF file.'), 'danger')
            return redirect(request.url)
    else:
        return render_template('upload.html')


# Route to download the generated resume
@app.route('/download', methods=['POST'])
def download():
    generated_html = request.form.get('generated_html')
    generated_pdf_name = 'resume.pdf'
    pdf_generator = PDFGenerator(
        generated_html, output_pdf_name=generated_pdf_name)
    pdf_generator.generate_pdf()
    return send_from_directory(directory=app.config['GENERATED_FOLDER'], filename=generated_pdf_name, as_attachment=True)


# Flask-Babel function to get the user's language preference
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'es'])


if __name__ == '__main__':
    app.run(debug=True)
