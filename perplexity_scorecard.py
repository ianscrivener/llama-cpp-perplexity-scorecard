import subprocess
import json
import uuid
import platform
import os
from datetime import datetime
from time import time
from yaspin import yaspin
import re
# import cli.app
from dotenv import load_dotenv


current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)

############################
# config
output_file_suffix = "px"


############################
# Load the .env file
load_dotenv()
LLAMA_CPP_PATH = os.getenv('LLAMA_CPP_PATH')
MODEL = os.getenv('MODEL')
MODEL_PATH = os.getenv('MODEL_PATH')
CORPUS = os.getenv('CORPUS')
CORPUS_PATH = os.getenv('CORPUS_PATH', f'{parent_directory}/test_corpus')
OUTPUT_FILE_PATH = os.getenv('OUTPUT_FILE_PATH', f'{parent_directory}/results')
CONTEXT = int(os.getenv('CONTEXT', 512))  # Default set to 512
BATCH = int(os.getenv('BATCH', 512))  # Default set to 512
THREADS = int(os.getenv('THREADS', 4))  # Default set to 4
GPU = int(os.getenv('GPU', 1))  # Default set to 1
API = os.getenv('API', '')  # Default set to empty string


############################
# get llama.cpp build details
def get_build_details():
    with open(f'{LLAMA_CPP_PATH}/build-info.h', 'r') as file:
        contents = file.read()

    build_number_match = re.search(r'#define BUILD_NUMBER (\d+)', contents)
    build_commit_match = re.search(r'#define BUILD_COMMIT "(.+?)"', contents)

    if build_number_match and build_commit_match:
        BUILD_NUMBER = int(build_number_match.group(1))
        BUILD_COMMIT = build_commit_match.group(1)
        return BUILD_NUMBER, BUILD_COMMIT
    else:
        print('ERROR Couldn\'t find BUILD_NUMBER and/or BUILD_COMMIT.')


############################
# show a spinner
@yaspin(text= 'Running llama.cpp ./perplexity...')

############################
# main function
def main():
    build_number, build_commit = get_build_details()
    perplexity_command = f"cd {LLAMA_CPP_PATH} && ./perplexity -m {MODEL_PATH}/{MODEL} -f {CORPUS_PATH}/{CORPUS} -c {CONTEXT} -b {BATCH} -t {THREADS} -ngl {GPU}"
    perplexity_command_json = f"./perplexity -m {MODEL} -f {CORPUS} -c {CONTEXT} -b {BATCH} -t {THREADS} -ngl {GPU}"
    start_time = time()
    process = subprocess.Popen(
        perplexity_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        bufsize=1,
        universal_newlines=True,
    )

    result = {
        "uuid": str(uuid.uuid4()),
        "datetime": "",
        "os": platform.version(),
        "perplexity_command": perplexity_command_json,
        "build_number": build_number,
        "build_commit": build_commit,
        "model": MODEL,
        "corpus": CORPUS,
        "context": CONTEXT,
        "batch": BATCH,
        "perplexity": 0,
        "step_count": 0,
        "seconds": 0,
        "std_out": [],
        "std_err": []
    }

    step = 1
    prev_time = 0
    score = ""

    while True:
        output = process.stdout.read(1)
        if output == "" and process.poll() is not None:
            break
        if output:
            current_time = time()
            if output == ",":
                score = score.split("]")[-1]

                ms_total = round((current_time - start_time) * 1000)

                if prev_time == 0:
                    ms_delta = ms_total
                else:
                    ms_delta = ms_total - prev_time

                # set perplexity score in json
                result["step_count"] = step
                result["perplexity"] = float(score)
                result["seconds"] = ms_total/1000

                result["std_out"].append(
                    {
                        "step": step,
                        "seconds_total": float(ms_total/1000),
                        "seconds_delta": float(ms_delta/1000),
                        "perplexity": float(score),
                    }
                )
                prev_time = ms_total
                step += 1
                score = ""
            else:
                score += output

    stderr = process.stderr.readlines()
    for line in stderr:
        current_time = time()
        response = line.strip()
        if response:
            result["std_err"].append(response)

    # ISO date time - 20230717T114948Z
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uuid_short = result["uuid"][:8]
    result["datetime"] = str(timestamp)
    output_file_name = f"{OUTPUT_FILE_PATH}/{output_file_suffix}_{timestamp}_{uuid_short}.json"
    with open(output_file_name, "w") as f:
        json.dump(result, f, indent=4)

#     print(json.dumps(result, indent=4))
#     print()
    print(f'   DONE: see results - {output_file_name} ')

# if __name__ == "__main__":
main()
