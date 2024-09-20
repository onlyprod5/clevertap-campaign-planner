#!/bin/sh

# Change directory to the location of the script
cd "$(dirname "$0")"

CURRENT_DIR=$(pwd)

INFO_LOG=$CURRENT_DIR/output.log
ERROR_LOG=2>&1 # Redirects standard error to the same file as info.

python3 -m venv myenv

source myenv/bin/activate

pip install pyotp selenium==4.24.0 requests slack_sdk python-dotenv

echo "\n----\n"

python3 $CURRENT_DIR/main.py >> $INFO_LOG $ERROR_LOG

