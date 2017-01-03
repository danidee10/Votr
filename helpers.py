import jwt
import os
import config
from flask import jsonify

# Load env file
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ


def handle_api_errors(error):
    resp = jsonify(error)
    resp.status_code = 401

    return resp


def decode_jwt(token):
    try:
        payload = jwt.decode(
                    token, env[config.AUTH0_CLIENT_SECRET],
                    audience=env[config.AUTH0_CLIENT_ID],
                    algorithms=['HS256'],
                    options={'verify_iat': False}
                )

    except jwt.ExpiredSignature:
        return handle_api_errors({'code': 'token_expired',
                            'message': 'token is expired'})
    except jwt.InvalidAudienceError:
        return handle_api_errors({'code': 'invalid_audience',
                            'message': 'incorrect audience'})
    except jwt.DecodeError:
        return handle_api_errors({'code': 'token_invalid_signature',
                            'message': 'token signature is invalid'})

    return payload
