# work in progress
pip3 install -t dep -r requirements.txt
(cd dep; zip ../lambda_artifact.zip -r .)
zip lambda_artifact.zip -u main.py