import argparse
import subprocess
import json
import uuid
import platform
import os
from datetime import datetime
from time import time
from yaspin import yaspin
import requests
import re
from dotenv import load_dotenv
from libs import download_test_corpus


############################
# hard coded config
output_file_suffix = "px"
version = "1.0.0"
test_corpus_sizes=[406,103,60,19]

############################
# user config - loaded from .env file
load_dotenv()
# LLAMA_CPP_PATH = os.getenv('LLAMA_CPP_PATH')
# MODEL = os.getenv('MODEL')
# MODEL_PATH = os.getenv('MODEL_PATH')
# CORPUS = os.getenv('CORPUS')
# CORPUS_LINES = os.getenv('CORPUS_LINES')
# CORPUS_PATH = os.getenv('CORPUS_PATH', f'{os.getcwd()}/test_corpus')
# OUTPUT_FILE_PATH = os.getenv('OUTPUT_FILE_PATH', f'{os.getcwd()}/results')
# CONTEXT = int(os.getenv('CONTEXT', 512))  # Default set to 512
# BATCH = int(os.getenv('BATCH', 512))  # Default set to 512
# THREADS = int(os.getenv('THREADS', 4))  # Default set to 4
# GPU = int(os.getenv('GPU', 1))  # Default set to 1
# # API = os.getenv('API', 'https://faas-sfo3-7872a1dd.doserverless.co/api/v1/web/fn-0e980f16-1f90-45b6-95f9-3a85255c6239/llama_perplexity_api/v1')  # Default set to empty string
# API = os.getenv('API', 'https://vx4spcsyj5c47txsx6dhvidnxy0nyzru.lambda-url.us-east-1.on.aws/')
# API_WEB_URL = os.getenv('API', 'https://llama-cpp-perplexity-logs.s3.amazonaws.com')

############################
# Set up argument parser
parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('--llama_cpp_path', default=os.getenv('LLAMA_CPP_PATH'), help='Path to llama cpp')
parser.add_argument('--model', default=os.getenv('MODEL'), help='Model name')
parser.add_argument('--model_path', default=os.getenv('MODEL_PATH'), help='Path to the model')
parser.add_argument('--corpus', default=os.getenv('CORPUS'), help='Corpus name')
parser.add_argument('--corpus_lines', default=os.getenv('CORPUS_LINES'), help='Number of corpus lines')
parser.add_argument('--corpus_path', default=os.getenv('CORPUS_PATH',f'{os.getcwd()}/test_corpus'), help='Path to the corpus')
parser.add_argument('--output_file_path', default=os.getenv('OUTPUT_FILE_PATH',f'{os.getcwd()}/results'), help='Path to JSON output directory')
parser.add_argument('--context', default=int(os.getenv('CONTEXT', 512)), type=int, help='Context size')
parser.add_argument('--batch', default=int(os.getenv('BATCH', 512)), type=int, help='Batch size')
parser.add_argument('--threads', default=int(os.getenv('THREADS', 4)), type=int, help='Number of threads')
parser.add_argument('--gpu', default=int(os.getenv('GPU', 100000)), type=int, help='GPU indicator')
parser.add_argument('--api', default='https://vx4spcsyj5c47txsx6dhvidnxy0nyzru.lambda-url.us-east-1.on.aws', help='API endpoint')
parser.add_argument('--api_web_url', default=os.getenv('API_WEB_URL','https://llama-cpp-perplexity-logs.s3.amazonaws.com'), help='API web URL')
parser.add_argument('--hardware_desc', default=os.getenv('HARDWARE_DESC', "unknown"), help='Describe your hardware very briefly')
parser.add_argument('--verbose', help='Print debugging output',  action='store_true')
parser.add_argument('--ignore', help='Set ignore flag in JSON saved to AWS S3', action='store_true')

# Parse arguments
args = parser.parse_args()

LLAMA_CPP_PATH = args.llama_cpp_path
MODEL = args.model
MODEL_PATH = args.model_path
CORPUS = args.corpus
CORPUS_LINES = args.corpus_lines
CORPUS_PATH = args.corpus_path
OUTPUT_FILE_PATH = args.output_file_path
CONTEXT = args.context
BATCH = args.batch
THREADS = args.threads
GPU = args.gpu
API = args.api
API_WEB_URL = args.api_web_url
HARDWARE_DESC = args.hardware_desc
VERBOSE = False if args.verbose is None else True
IGNORE = 0 if args.ignore is None else 1

if VERBOSE:
    print("########################")
    for arg in vars(args):
        print(f'{arg}: {getattr(args, arg)}')

############################
# test corpus
download_test_corpus.main(CORPUS_PATH,test_corpus_sizes)

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
# remove full filepaths from std_err
def lint_stderr(stderr_array):
    new_array = []
    for item in stderr_array:
        new_array.append(item.replace(LLAMA_CPP_PATH,""))
    return new_array

############################
# main function
def main():
    build_number, build_commit = get_build_details()
    perplexity_command = f"cd {LLAMA_CPP_PATH} && ./perplexity -m {MODEL_PATH}/{MODEL} -f {CORPUS_PATH}/{CORPUS} -c {CONTEXT} -b {BATCH} -t {THREADS} -ngl {GPU}"
    perplexity_command_json = f"./perplexity -m {MODEL} -f {CORPUS} -c {CONTEXT} -b {BATCH} -t {THREADS} -ngl {GPU}"
    start_time = time()

    if VERBOSE:
        print("\n########################")
        print("./perplexity command")
        print(perplexity_command)
        print("########################")

    #  run llama.cpp in a sub process
    process = subprocess.Popen(
        perplexity_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        bufsize=1,
        universal_newlines=True,
    )

    # build json result set
    result = {
        "uuid": str(uuid.uuid4()),
        "ignore": IGNORE,
        "datetime": "",
        "file_name": "",
        "version": version,
        "os": platform.version(),
        "hardware":HARDWARE_DESC,
        "perplexity_command": perplexity_command_json,
        "build_number": build_number,
        "build_commit": build_commit,
        "model": MODEL,
        "corpus": CORPUS,
        "corpus_lines": int(CORPUS_LINES),
        "context": CONTEXT,
        "batch": BATCH,
        "perplexity": 0,
        "step_count": 0,
        "seconds": 0,
        "std_out": [],
        "std_err": []
    }

    # loop through stdout form llama.cpp, extracting chunk data & making JSON
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

    # clean up llama.cpp stderr output
    stderr = process.stderr.readlines()
    for line in stderr:
        current_time = time()
        response = line.strip()
        if response:
            result["std_err"].append(response)
            if VERBOSE:
                print(response)


    # build some more JSON
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") # ISO date time - 20230717T114948Z
    uuid_short = result["uuid"][:8]
    result["datetime"] = str(timestamp)
    output_file_name = f"{OUTPUT_FILE_PATH}/{output_file_suffix}_{timestamp}_{uuid_short}.json"
    result["file_name"] = output_file_name.split("/")[-1]
    result["std_err"] = lint_stderr(result["std_err"])

    # make a JSON file
    with open(output_file_name, "w") as f:
        json.dump(result, f, indent=4)

    # POST JSON results to API
    try:
        print(f'\n   API Response: {requests.post(API, json=result)}')
    except:
        print('There was an error submitting results to the AWS API.')

#   print(json.dumps(result, indent=4))
#   print()

    if VERBOSE:
        print("\n########################")
        print(f'Results: {output_file_name} ')
        print(json.dumps(result, indent=4))

    else:
        print(f'   DONE: see results - {output_file_name} ')
        print(f'      also on AWS S3 - {API_WEB_URL}/{result["file_name"]} ')
        print(f'      Thanks for submitting your llama.cpp perplexity results!!')


# show a spinner and start main function

if not VERBOSE:
    spinner = yaspin(text='Running llama.cpp ./perplexity...')
    spinner.start()
    main()
    spinner.stop()
else:
    main()
