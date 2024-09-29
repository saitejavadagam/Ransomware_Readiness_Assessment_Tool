from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from security_tests import security_tests_bp

app = Flask(__name__)
app.register_blueprint(security_tests_bp, url_prefix='/tests')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///progress.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

defender_params_comments = {
    "EnableControlledFolderAccess": "To enable, go to Settings > Privacy & Security > Windows Security > Virus & threat protection > Manage ransomware protection. Turn on Controlled folder access.",
    "AttackSurfaceReductionRules_Actions": "To enable, configure the rules in the Microsoft Defender Security Center under Attack Surface Reduction.",
    "AttackSurfaceReductionRules_Ids": "To enable, identify the specific rule IDs to be activated in the Defender settings.",
    "AttackSurfaceReductionRules_RuleSpecificExclusions": "To disable, remove specific rules that you do not want to enforce from the exclusions list.",
    "PUAProtection": "To enable, go to Settings > Privacy & Security > Windows Security > Virus & threat protection settings. Turn on Potentially unwanted app blocking.",
    "EnableNetworkProtection": "To enable, navigate to Windows Security > App & browser control > Exploit protection > Network protection and turn it on.",
    "DisableRemovableDriveScanning": "To disable, go to Settings > Privacy & Security > Windows Security > Virus & threat protection settings and turn off the scanning of removable drives.",
    "DisableRealtimeMonitoring": "To disable, open Windows Security, go to Virus & threat protection, and turn off Real-time protection.",
    "CloudBlockLevel": "To enable, configure cloud-delivered protection in Windows Security under Virus & threat protection settings.",
    "DisableTamperProtection": "To disable, go to Settings > Privacy & Security > Windows Security > Virus & threat protection settings and turn off Tamper protection.",
    "SignatureUpdateInterval": "To configure, adjust the frequency of signature updates in Windows Security settings under Virus & threat protection.",
    "BruteForceProtectionAggressiveness": "To configure, set the aggressiveness level for brute force protection in Defender settings.",
    "CloudExtendedTimeout": "To configure, set the extended timeout period for cloud protection in the Defender settings."
}


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


def generate_color_comment_system(progress):
    if progress >= 90:
        return 'green', 'Excellent understanding of ransomware defenses! Your system is well-protected with advanced measures in place.'
    elif progress >= 75:
        return 'greenyellow', 'Good understanding of ransomware defenses. Your system has solid protections, but consider enhancing your backup strategies.'
    elif progress >= 50:
        return 'yellow', 'Fair knowledge of ransomware defenses. Your system is partially protected, but you need to strengthen your detection and response protocols.'
    elif progress >= 25:
        return 'orange', 'Basic understanding of ransomware defenses. Your system is at risk; focus on implementing essential security measures and awareness training.'
    else:
        return 'red', 'Very limited knowledge of ransomware defenses. Your system is highly vulnerable; immediate action is required to implement basic protections and educate staff.'



@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/user_test')
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

    return render_template('progress.html', progress=progress, color=color, comment=comment)


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
    color, comment = generate_color_comment_system(progress)
    global values
    values = {
        'progress': progress,
        'color': color,
        'comment': comment
    }
    return "success"


@app.route('/client_results')
def wait_for_data():

    error_list = [values['comment']]+[i+' : '+defender_params_comments[i] for i in data['error_list']]
    return render_template('progress.html', progress=values['progress'], color=values['color'], error_list=error_list)


if __name__ == '__main__':
    app.run()
