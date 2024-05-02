# constants.py
"""

This for senting constant error messages


"""

# Types
SUCCESS_MESSAGE = "Success"
ERROR_MESSAGE = "Error"
MESSAGE = 'message'


# Messge For email purpuse




# Success messages
EMAIL_SIGNIN_SUCCESSGULLY = 'Email sign-in successful'
GENERATE_OTP_MESSAGE = 'OTP generated and sent successfully'
PASSWORD_SUCCESS = 'Password changed successfully'
PHONE_SUCCESS = 'Phone number changed successfully'
UNBLOCK_SUCCESS="User has been unblocked successfully."
BLOCK_SUCCESS = "User has been blocked successfully."
BOOKING_CANCEL = 'Booking Cancel Successfully'
DELETE_SUCCESS = 'Successfully deleted'
UPDATE_SUCCESS = 'successfully updated'
ADD_SUCCESS = 'successfully added'










# Fail Message
FAILED_TO_SENTOTP = 'Failed to send OTP'
AUTHENTICATION_FAILED='Authentication failed'





# Invalid 
INVALID_OTP = 'Invalid OTP or OTP expired'
ENTERY_NOT_FOUND = 'OTP entry not found'
INVALID_ROOM =  'Invalid room_id'
INVALID_CREDENTIAL = 'Invalid credentials'




# Already excists 
WHISHLIST_ALREADY_EXCIST = 'Room already in wishlist'




# Missing Field
MISSING_ROOM_ID = 'Missing room_id field'

# Notfound
WHISHLIST_NOT_FOUND='Wishlist not found'
ROOM_NOT_FOUND = 'Room not found'



# Response Messages

PHONE_NUMBER_ALREADY_EXISTS_ERROR = "This phone number is already associated with an existing account."
INVALID_GOOGLE_ACCESS_TOKEN_ERROR = "Invalid Google access token"
TOKEN_EXPIRED_ERROR = "This token is expired"
USER_VERIFICATION_FAILED_ERROR = "Could not verify user"
OTP_STILL_VALID = 'OTP resend is not allowed until the previous OTP expires.'
SIGNUP_SUCCESS =   "User signed up successfully as a vendor"
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

PERMISSION_DENIED = "You do not have permission to perform this action."
EMAIL_NOT_EXIST = 'User with this email does not exist'



# For room purpurse
ROOM_ALREADY_BOOKED = "The room is already booked within the specified time range."
CHECK_IN_MUST_FUTURE= "Check-in date must be in the future."
CHECKING_MUST_GREATER="Check-in date must be before check-out date."



# For Booking 
BOOKING_NOT_CANCEL='Booking cannot be canceled as the 2-minute cancellation window has passed.'






# $$$$$$$$$$$$$$$$$$$$$$$
FAIL_GENERATE = 'Failed to generate/send OTP. Exception'






# For Razopay
CURRENCY = 'INR'
METHOD_NOT_ALLOWED = 'Method not allowed'



# TODO  Cache Keys

TOP_RATED_ROOMS_CACHE_KEY = 'top_rated_rooms_list'
ALL_ROOMS = 'allrooms'
VENDOR_QUERY_SET = 'vendor_queryset'
USER_QUERY_SET = 'user_queryset'
ROOM_DETAIL='room_detail'
USER_WHISHLIST = "user_wishlists"
ROOM_LIST = 'room_list'

# Suggestion 
SUGGESTION = [
                    "Make sure all words are spelled correctly.",
                    "Try different keywords.",
                    "Try more general keywords.",
                    "Try fewer keywords."
                ]