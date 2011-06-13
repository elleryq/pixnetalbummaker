#!/bin/sh

# Notice
echo "Do you had increased the version in app.yaml?"
echo "Please check it again."
echo "Are you sure? (yes/no)"
read answer
if [ "$answer" != "yes" ]; then
    echo "You don't agree to continue."
    exit -1
fi

# call appcfg.py to deploy
if [ -e /opt/google_appengine/appcfg.py ]; then
    python /opt/google_appengine/appcfg.py --noisy update .
    echo "Updated ok!"
else
    echo "Need Google AppEngine SDK."
fi

exit 0
