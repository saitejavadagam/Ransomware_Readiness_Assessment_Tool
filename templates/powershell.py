import subprocess
import webbrowser

import requests
import json

command_text = '(Get-MpPreference).'

final_result = {}

defender_params = [
    "EnableControlledFolderAccess",
    "AttackSurfaceReductionRules_Actions",
    "AttackSurfaceReductionRules_Ids",
    "AttackSurfaceReductionRules_RuleSpecificExclusions",
    "PUAProtection",
    "EnableNetworkProtection",
    "DisableRemovableDriveScanning",
    "DisableRealtimeMonitoring",
    "CloudBlockLevel",
    "DisableTamperProtection",
    "SignatureUpdateInterval",
    "BruteForceProtectionAggressiveness",
    "CloudExtendedTimeout"
]


def get_status(command):
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)

    if result.returncode == 0:

        return result.stdout.strip()

    else:
        return f"error:{result.stderr}"


for i in defender_params:
    final_result[i] = get_status(command_text + i)


# for i in final_result:
#     print(i, ':', final_result[i])

def assess_defender_score(defender_params_status):
    score = 0

    # Define desired values for parameters
    desired_values = {
        "EnableControlledFolderAccess": '1',
        "PUAProtection": '1',
        "EnableNetworkProtection": '1',
        "DisableRemovableDriveScanning": 'False',
        "DisableRealtimeMonitoring": 'False',
        "CloudBlockLevel": '2',
        "DisableTamperProtection": 'False',
        "AttackSurfaceReductionRules_Actions": "",
        "AttackSurfaceReductionRules_Ids": "",
        "AttackSurfaceReductionRules_RuleSpecificExclusions": "N/A: Must be an administrator to view exclusions",
        "SignatureUpdateInterval": '0',
        "CloudExtendedTimeout": '0'
    }

    max_score = len(desired_values)

    error_params = []

    for param in defender_params_status.keys():
        current_value = defender_params_status[param]
        if param in desired_values:
            desired_value = desired_values[param]
            if desired_value == current_value:
                score += 1
            else:
                error_params.append(param)

    return score, max_score, error_params


final_score, total_score, error_list = assess_defender_score(final_result)
print(f"Defender Score: {final_score}/{total_score}")
print(error_list)

server_url = 'http://127.0.0.1:5000/receive_data'

data_to_send = {
    'Defender_score': final_score,
    'total_score': total_score,
    'error_list': error_list
}

try:
    response = requests.post(server_url, json=data_to_send)
    if response.status_code == 200:
        print("Success")
        webbrowser.open("http://127.0.0.1:5000/client_results")
    else:
        print("Failed")
except Exception as e:
    print(f"Error: {e}")
