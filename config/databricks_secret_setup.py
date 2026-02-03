import urllib.parse

# Use a dictionary to keep everything organized
AWS_CREDS = {
    "ACCESS_KEY": "**#**",
    "SECRET_KEY": "###**@###",
    "BUCKET": "sindrela-sales-pipeline"
}

def get_s3_base_path():
    encoded_secret = urllib.parse.quote(AWS_CREDS["SECRET_KEY"], safe="")
    return f"s3a://{AWS_CREDS['ACCESS_KEY']}:{encoded_secret}@{AWS_CREDS['BUCKET']}/landing-zone/"

