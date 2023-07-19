import subprocess
import json
import uuid
import platform
import os
from datetime import datetime
from time import time
from yaspin import yaspin
import re
import cli.app

############################
# config
OUTPUT_FILE_SUFFIX = "px"
output_filepath = "results"
LLAMA_CPP_PATH="/Users/ianscrivener/_AI/___LLMs/_LLM_monorepo/llama.cpp"
MODEL="open-llama-7b-q4_0.bin"
MODEL_PATH="/Users/ianscrivener/_AI/___LLMs/_LLM_monorepo/llama.cpp/models/7B"
CORPUS="wiki.test.raw.19"
# CORPUS_PATH="/Users/ianscrivener/_AI/scriv-ml-monorepo/llama-cpp-ci-bench/wikitext-2-raw"
CORPUS_PATH="/Users/ianscrivener/_AI/scriv-ml-monorepo/_node.js_spikes/llama-cpp-ci-bench/wikitext-2-raw"
CONTEXT=512
BATCH=512
THREADS=4
GPU=1
API=""

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
    output_file_name = f"{output_filepath}/{OUTPUT_FILE_SUFFIX}_{timestamp}_{uuid_short}.json"
    with open(output_file_name, "w") as f:
        json.dump(result, f, indent=4)

#     print(json.dumps(result, indent=4))
    print()
    print(f'   DONE: see results - {output_file_name} ')




if __name__ == "__main__":
    main()
