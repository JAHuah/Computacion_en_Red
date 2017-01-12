# -*-coding:utf8-*-

""" SendPulse REST API usage example

Documentation:
    https://login.sendpulse.com/manual/rest-api/
    https://sendpulse.com/api
"""

from pysendpulse import PySendPulse

if __name__ == "__main__":
    REST_API_ID = ''
    REST_API_SECRET = ''
    TOKEN_STORAGE = 'memcached'
    SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE)

	    # Activate/Deactivate subscriber, state=1 - activate, state=2 - deactivate
    SPApiProxy.push_set_subscription_state(SUBSCRIBER_ID, STATE)

    # Create new push task
    SPApiProxy.push_create('Hello!', WEBSITE_ID, 'This is my first push message', '10', {'filter_lang':'en', 'filter': '{"variable_name":"some","operator":"or","conditions":[{"condition":"likewith","value":"a"},{"condition":"notequal","value":"b"}]}'})
