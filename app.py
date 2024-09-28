from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/test')
def testing_page():
    return render_template('test.html')


@app.route('/results', methods=['POST'])
def generate_results():
    results = list(map(str, request.form.get('results').split(',')))
    print(type(results))
    print(results)

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

    progress = (100*score)//total
    print(progress)
    color = 'blue'
    return render_template('face.html', progress=progress, color=color)


@app.route('/test3')
def test3():
    return "this is the page where machine learning is done there"


if __name__ == '__main__':
    app.run()
