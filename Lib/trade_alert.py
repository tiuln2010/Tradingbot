import requests

class Trade_alert:
    """Slack alert"""
    def __init__(self, msg):
        self.msg = msg
            
    def send_msg(msg='default'):
        encoded_msg = '{"text":"%s"}' % msg
        headers = {
            'Content-type': 'application/json',
        }
        url = 'https://hooks.slack.com/services/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'
        response = requests.post(url, headers=headers, data=encoded_msg)
        return response


