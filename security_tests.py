from flask import Flask, render_template, jsonify, Blueprint
import subprocess
import platform
import socket
import psutil
import os
import matplotlib.pyplot as plt

security_tests_bp = Blueprint('security_tests', __name__)


def run_security_tests():
    """Run 10 security tests on the system and return the results."""
    results = {'safe': 0, 'medium': 0, 'risk': 0}
    passed_tests = 0
    total_tests = 10

    # Test examples (simplified)
    try:
        # Antivirus test (Test 1)
        output = subprocess.check_output(
            'wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName', shell=True)
        if output.strip():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        results['risk'] += 1

    # Firewall test (Test 2)
    try:
        output = subprocess.check_output('netsh advfirewall show allprofiles state', shell=True)
        if b'ON' in output:
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        results['risk'] += 1

    try:
        output = subprocess.check_output('powershell Get-WUServiceManager', shell=True)
        if 'Windows Update' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking Windows Update: {e}")
        results['risk'] += 1

    # Test 4: Check for automatic backup settings
    try:
        output = subprocess.check_output('powershell Get-Service -Name Wbadmin', shell=True)
        if 'Running' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking Backup: {e}")
        results['risk'] += 1

    # Test 5: Check for disk encryption (BitLocker) status
    try:
        output = subprocess.check_output('manage-bde -status', shell=True)
        if 'Fully Decrypted' not in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking BitLocker: {e}")
        results['risk'] += 1

    # Test 6: Check for system account password policies
    try:
        output = subprocess.check_output('net accounts', shell=True)
        if 'Minimum password age' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking password policy: {e}")
        results['risk'] += 1

    # Test 7: Check for system integrity (system file checker)
    try:
        output = subprocess.check_output('sfc /scannow', shell=True)
        if 'Windows Resource Protection did not find any integrity violations' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking system integrity: {e}")
        results['risk'] += 1

    # Test 8: Check for malware scans in the last 30 days
    try:
        output = subprocess.check_output('powershell Get-MpThreatDetection -LastScan', shell=True)
        if output.strip():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking malware scans: {e}")
        results['risk'] += 1

    # Test 9: Check if UAC (User Account Control) is enabled
    try:
        output = subprocess.check_output(
            'reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v EnableLUA', shell=True)
        if '0x1' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking UAC: {e}")
        results['risk'] += 1

    # Test 10: Check for open network ports
    try:
        output = subprocess.check_output('netstat -an', shell=True)
        if 'LISTENING' in output.decode():
            passed_tests += 1
        else:
            results['medium'] += 1
    except Exception as e:
        print(f"Error checking open ports: {e}")
        results['risk'] += 1

    results['safe'] = passed_tests
    return results, passed_tests, total_tests


def system_info():
    """Get basic system information."""
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "Hostname": socket.gethostname(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
    }
    return info


def create_donut_chart(results):

    labels = ['Safe', 'Medium Risk', 'High Risk']
    sizes = [results['safe'], results['medium'], results['risk']]
    colors = ['#28a745', '#ffc107', '#dc3545']  # Green for safe, Yellow for medium, Red for risk

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.4})
    center_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(center_circle)

    ax.axis('equal')

    chart_path = os.path.join('static', 'donut_chart.png')
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    return chart_path


@security_tests_bp.route('/')
def test_choices():
    return render_template('choice.html')


@security_tests_bp.route('/run_security_test', methods=['POST'])
def run_security_test():
    # Run the security tests
    results, passed_tests, total_tests = run_security_tests()

    # Get system information
    sys_info = system_info()

    # Determine risk level
    if passed_tests <= 4:
        risk_level = "High Risk"
    elif 5 <= passed_tests <= 6:
        risk_level = "Medium"
    else:
        risk_level = "Safe"

    # Create donut chart for visualization
    chart_path = create_donut_chart(results)

    # Render the results page and pass all variables to the template
    return render_template('results.html',
                           results=results,
                           passed_tests=passed_tests,
                           total_tests=total_tests,
                           sys_info=sys_info,
                           risk_level=risk_level,
                           chart_path=chart_path)



