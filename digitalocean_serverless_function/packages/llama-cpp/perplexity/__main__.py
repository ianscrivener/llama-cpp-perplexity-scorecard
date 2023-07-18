# https://faas-sfo3-7872a1dd.doserverless.co/api/v1/web/fn-3666012a-4dbd-40a5-9229-c102125a8ccc/llama-cpp/perplexity_api

# curl -X GET "https://faas-sfo3-7872a1dd.doserverless.co/api/v1/web/fn-3666012a-4dbd-40a5-9229-c102125a8ccc/llama-cpp/perplexity_api" \
#   -H "Content-Type: application/json"

# curl -X POST "https://faas-sfo3-7872a1dd.doserverless.co/api/v1/namespaces/fn-3666012a-4dbd-40a5-9229-c102125a8ccc/actions/llama-cpp/perplexity_api?blocking=true&result=true" \
#   -H "Content-Type: application/json" \
#  -H "Authorization: Basic ZWVhNzA0M2ItMjIzOS00ZGQ5LTgyNjAtMjYwNTRjNjNhYTljOkxWZjZGbFpadzlJYzBmQ2lvWU9aN2tZZ2JObW1McWdURHVjZmpzUGY0a1pIbDljZXJNbWN5bG5DTU14eUpCSVI="


#
# datetime - my format time stamp
# uuid - type my UUID
# git_user - type string
# git_email - type string
# perplexity_command"
# std_out - type array > len > 10
# std_err - type array, len > 10


import json
import os
from jsonschema import validate, ValidationError
from http import HTTPStatus


json_schema = "json_schema.json"

########################################
# check json is valid
def check_json(j):
    with open(json_schema, 'r') as file:
        schema = json.load(file)

    try:
        validate(instance=j, schema=schema)
        return True
    except ValidationError:
        return False


########################################
# main function
def main(args):
    data = args.get("json", {})

    if check_json(data):
        print("JSON is OK")
        return {"body": greeting}

    else:
        print("JSON is bad")
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": "no receiver phone number provided"
        }

