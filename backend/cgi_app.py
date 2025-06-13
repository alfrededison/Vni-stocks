#!/usr/bin/python3.12

import os
import json

from handlers import (
    get_env,
    get_signals_data,
    get_stocks,
    build_signals,
    trigger_signals,
    filter_stocks,
    test_notify,
)


def main():
    # CORS headers
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()  # End of headers

    # Handle preflight OPTIONS request
    if os.environ.get('REQUEST_METHOD', '') == 'OPTIONS':
        print(json.dumps({"message": "CORS preflight"}))
        return

    query_string = os.environ.get('QUERY_STRING', '')
    params = dict(param.split('=', 1) for param in query_string.split('&') if '=' in param)

    action = params.get('action', '')

    if action == 'env':
        print(json.dumps(get_env()))
    elif action == 'signals':
        print(json.dumps(get_signals_data()))
    elif action == 'stocks':
        print(json.dumps(get_stocks()))
    elif action == 'build':
        print(json.dumps(build_signals()))
    elif action == 'trigger':
        print(json.dumps(trigger_signals()))
    elif action == 'filter':
        print(json.dumps(filter_stocks()))
    elif action == 'test-notify':
        print(json.dumps(test_notify()))
    else:
        print(json.dumps({"error": "Unknown or missing action parameter"}))

if __name__ == "__main__":
    main()
