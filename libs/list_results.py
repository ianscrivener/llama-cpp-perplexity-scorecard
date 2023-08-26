import requests
from lxml import etree
import fnmatch

# Default URL of the S3 Bucket - publicly accessible
xml_index_url = "https://llama-cpp-perplexity-logs.s3.amazonaws.com/"

def main(bucket_url=xml_index_url):
    # Get the XML response
    response = requests.get(bucket_url)
    tree = etree.fromstring(response.content)

    # Create a python list of json_files that match "px_*.json"
    json_files = [
        element.text for element in tree.iter('{http://s3.amazonaws.com/doc/2006-03-01/}Key')
        if fnmatch.fnmatch(element.text, 'px_*.json')
    ]

    return json_files

if __name__ == "__main__":
    print(main())
