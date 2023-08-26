import os
import subprocess

########################
def main(corpus_path, sizes):
    """Download hellaswag - quick & dirty"""

    wget_command = '''
        wget -nc --compression=gzip \
        https://raw.githubusercontent.com/klosax/ppl_hellaswag/main/hellaswag_val_correct.txt.600 \
        https://raw.githubusercontent.com/klosax/ppl_hellaswag/main/hellaswag_val_wrong.txt.600 \
        https://raw.githubusercontent.com/klosax/ppl_hellaswag/main/hellaswag_val_correct.txt.200 \
        https://raw.githubusercontent.com/klosax/ppl_hellaswag/main/hellaswag_val_wrong.txt.200
    '''

    # Test 1 - test_corpus directory exists
    if not os.path.exists(corpus_path):
        os.makedirs(corpus_path, exist_ok=True)

    # change directory to {corpus_path}
    os.chdir(corpus_path)

    # Using subprocess to execute the command
    process = subprocess.Popen(wget_command, stdout=subprocess.PIPE, shell=True)

    # Get the output from the command
    output, error = process.communicate()

    # Print the output
    if output:
        return True
#         print(output.decode())
    if error:
        print(error.decode())
        return False

