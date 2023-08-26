import os
import requests
import zipfile

########################
def main(corpus_path, sizes):
    """Download and prepare data."""

    url = "https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-2-raw-v1.zip"
    do_download = False

    # Test 1 - test_corpus directory exists
    if not os.path.exists(corpus_path):
        os.makedirs(corpus_path, exist_ok=True)

    # change directory to {corpus_path}
    os.chdir(corpus_path)

    # Test 2 - required files exist
    for number in sizes:
        fname = f'wiki.test.raw.{number}'
        if not os.path.isfile(fname):
            do_download = True

    ###################
    # Download and process if required
    if do_download:

        local_filename = url.split('/')[-1]

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(local_filename, 'r') as zip_ref:
            zip_ref.extractall('.')

        os.remove(local_filename)

        # Create 'wiki.test.raw.xxx' pruned test data
        with open('wikitext-2-raw/wiki.test.raw') as file:
            lines = file.readlines()

        # numbers = [406,103,60,19]
        for number in sizes:
            fname = f'wiki.test.raw.{number}'
            with open(fname, 'w') as file:
                file.writelines(lines[:number])

        return do_download
