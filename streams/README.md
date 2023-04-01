# Server setup

## Set up virtualenv
in src directory
`virtualenv -p python3 env`
`source env/bin/activate`
`pip install -r requirements.txt`
## Start server
in src directory
`flask --app webserver run &`
`python websocketserver.py &`
`ngrok start --all --config ngrok.yml`
note server url
edit templates/streams for server url

# Twilio setup

- Assume we have a test SIP domain and extension/pw creds with Twilio
- Assume we have a test PSTN number with Twilio

## Set up environment secrets

## Register SIP client to test SIP domain and creds

sip:test@experimenter-futel-stage.sip.twilio.com

## Call the SIP client using our server's TWIML

SERVER_TWIML_URL: https://<server_url>/twiml
FROM_PSTN_NUMBER: <Twilio test PSTN number>
TO_SIP_URL: sip:<extension>@<Twilio SIP domain>

`twilio api:core:calls:create --from="<FROM_PSTN_NUMBER>" --to="<TO_SIP_URI>" --url="<SERVER_TWIML_URL>"`
