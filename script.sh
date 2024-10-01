#!/bin/sh

# Change directory to the location of the script
cd "$(dirname "$0")"

CURRENT_DIR=$(pwd)

INFO_LOG=$CURRENT_DIR/output.log
SLACK_INFO_LOG=$CURRENT_DIR/slack_output.log
ERROR_LOG=2>&1 # Redirects standard error to the same file as info.

python3 -m venv myenv

source myenv/bin/activate

pip install pyotp selenium==4.24.0 requests slack_sdk python-dotenv slack_bolt

echo "\n----\n"

if ! pgrep -f "slack_listener.py" > /dev/null; then
  python3 $CURRENT_DIR/slack_listener.py >> $SLACK_INFO_LOG $ERROR_LOG &
fi

python3 $CURRENT_DIR/main.py >> $INFO_LOG $ERROR_LOG
