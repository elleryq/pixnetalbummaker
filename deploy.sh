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

# replace consumer key/secret
source ~/Dropbox/Projects/pixnetalbummaker/pixnetapi_app_detail.txt
TMPFILE="/tmp/user.py"
cp application/controller/user.py.in $TMPFILE
sed -i s/{consumer_key}/$consumer_key/ $TMPFILE
sed -i s/{consumer_secret}/$consumer_secret/ $TMPFILE
cp $TMPFILE application/controller/user.py
rm -f $TMPFILE
unset TMPFILE

# call appcfg.py to deploy
if [ -e /opt/google_appengine/appcfg.py ]; then
    python /opt/google_appengine/appcfg.py --noisy update .
else
    echo "Need Google AppEngine SDK."
fi

rm -f application/controller/user.py

exit 0
