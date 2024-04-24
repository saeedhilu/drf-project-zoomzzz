# constants.py
"""

This for senting constant error messages


"""
from rest_framework import status

# Response Messages
SUCCESS_MESSAGE = "Success"
ERROR_MESSAGE = "Error"
PHONE_NUMBER_ALREADY_EXISTS_ERROR = "This phone number is already associated with an existing account."
INVALID_GOOGLE_ACCESS_TOKEN_ERROR = "Invalid Google access token"
TOKEN_EXPIRED_ERROR = "This token is expired"
USER_VERIFICATION_FAILED_ERROR = "Could not verify user"
OTP_STILL_VALID = 'OTP resend is not allowed until the previous OTP expires.'

# Status Codes

"""

For Vendor Page

"""
# error_messages.py

# Common error messages
PASSWORDS_DO_NOT_MATCH = "Passwords do not match"
NEW_PASSWORD_SIMILAR_TO_OLD = "New password is too similar to the old password"
NEW_PASSWORD_CONFIRMATION_REQUIRED = "New password and confirm password do not match"
INVALID_EMAIL_OR_PASSWORD = "Invalid email or password"
EMAIL_ALREADY_EXISTS = "A user with this email already exists"
OTP_ALREADY_EXISTS = 'A valid OTP already exists for this email address.'
GENERATE_OTP_MESSAGE = 'OTP generated and sent successfully'
EMAIL_NOT_EXIST = 'User with this email does not exist'
PASSWORD_SUCCESS = 'Password changed successfully'
PHONE_SUCCESS = 'Phone number changed successfully'
PERMISSION_DENIED = "You do not have permission to perform this action."









