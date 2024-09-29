from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///progress.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ProgressData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    progress = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.String(200), nullable=False)

    def __init__(self, progress, color, comment):
        self.progress = progress
        self.color = color
        self.comment = comment


def generate_color_comment(progress):
    if progress >= 90:
        return 'green', 'Excellent understanding of ransomware knowledge!'
    elif progress >= 75:
        return 'greenyellow', 'Good understanding, but there is room for improvement.'
    elif progress >= 50:
        return 'yellow', 'Fair knowledge, but more study is needed to improve.'
    elif progress >= 25:
        return 'orange', 'Basic understanding, focus on learning more.'
    else:
        return 'red', 'Very limited knowledge, considerable improvement required.'


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/test')
def testing_page():
    return render_template('test.html')


@app.route('/results', methods=['POST'])
def generate_results():
    results = list(map(str, request.form.get('results').split(',')))

    answer_key = [
        'true',  # Q1: Do you have a data backup plan in place?
        'true',  # Q2: Have you conducted recent cybersecurity training for employees?
        'true',  # Q3: Are you using up-to-date antivirus software?
        'b',  # Q4: Your organization receives a suspicious email with a link. What do you do?
        'a',
        # Q5: Your team has been informed of a recent ransomware attack affecting similar organizations. What action should you take?
        'b',  # Q6: A ransomware alert pops up on your computer while working. How do you respond?
        'b',
        # Q7: You discover that a coworker has accidentally clicked on a malicious link in an email. What is your immediate action?
        'a',
        # Q8: During a routine check, your IT department discovers that several systems have not been backed up in a while. What should you do?
        'a',
        # Q9: Your organization is planning to implement new security software to combat ransomware. What should you do?
        'a'  # Q10: A colleague mentions they are using personal devices for work tasks. What is your response?
    ]

    score = 0
    total = len(results)

    for i in range(total):
        if results[i] == answer_key[i]:
            score += 1

    progress = (100 * score) // total
    print(progress)
    color, comment = generate_color_comment(progress)

    db.create_all()

    new_entry = ProgressData(progress=progress, color=color, comment=comment)

    # Add and commit to the database
    db.session.add(new_entry)
    db.session.commit()

    return render_template('face.html', progress=progress, color=color, comment=comment)


@app.route('/test3')
def test3():
    return "this is the page where machine learning is done there"


data = {}
values = {}


@app.route('/receive_data', methods=['POST'])
def receive_data():
    global data
    data = request.json
    print(data)

    progress = data['Defender_score'] * 100 // data['total_score']
    color, comment = generate_color_comment(progress)
    global values
    values = {
        'progress': progress,
        'color': color,
        'comment': comment
    }
    return "success"


@app.route('/client_results')
def wait_for_data():
    return render_template('face.html', progress=values['progress'], color=values['color'], comment=values['comment'])


if __name__ == '__main__':
    app.run()
