from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from .serializers import(
    ChangeEmailSerializer,
    GenerateEmailSerializer, 
    VendorLoginSerializer,
    ForgotPasswordSerializer
) 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from accounts.utils import(
    send_otp_email,
    generate_otp_code,
    forgot_password_link
) 
from accounts.models import OTP
from django.contrib.auth.tokens import default_token_generator

from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_str




class GenerateEmailView(APIView):
    """
    API endpoint to generate and send OTP via email for user registration.
    """
    serializer_class = GenerateEmailSerializer

    def create_otp(self, email, password):
        """
        Create or update OTP for the given email and password.
        """
        otp = generate_otp_code()
        otp_expiry = timezone.now() + timedelta(seconds=40)
        
        otp_instance, created = OTP.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'otp_expiry': otp_expiry, 'password': password}
        )
        return otp, otp_instance, created

    def post(self, request):
        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data['email']
            phone_number = validated_data.get('phone_number')
            password = validated_data.get('password')
            first_name = validated_data.get('first_name')
            last_name = validated_data.get('last_name')
            username = email.split('@')[0]

            try:
                # Check if there's an existing valid OTP for the email
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    # If the OTP is still valid, notify the user and return
                    return Response({'message': 'A valid OTP already exists for this email address.'}, status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                pass

            try:
                # Create or update OTP
                otp, otp_instance, _ = self.create_otp(email, password)

                # Send OTP email with the generated OTP
                send_otp_email(email,otp, validated_data['first_name'] )

                # Store email in session
                request.session['username']=username
                request.session['email'] = email
                request.session['phone_number'] = phone_number
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name

                # Return success response
                return Response({'message': 'OTP generated and sent successfully'}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyEmailView(APIView):
    """
    API endpoint to verify email OTP and authenticate user as a vendor.
    """
    def post(self, request):
        # Retrieve email, OTP, and other user data entered by the user
        email = request.session.get('email')
        otp_entered = request.data.get('otp')

        # Retrieve first name, last name, and phone number from session
        first_name = request.session.get('first_name')
        last_name = request.session.get('last_name')
        phone_number = request.session.get('phone_number')
        username = request.session.get('username')

        try:
            # Retrieve OTP instance from the database
            otp_instance = OTP.objects.get(email=email)
            password = otp_instance.password

            # Check if OTP is valid and not expired
            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                # Delete the OTP instance as it's no longer needed
                otp_instance.delete()

                # Create the user
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    is_vendor=True
                )

                # Generate tokens for authentication
                access_token = RefreshToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                refresh_token_exp = timezone.now() + timedelta(days=7)

                # Return success response with tokens and user information
                return Response({
                    "access_token": str(access_token.access_token),
                    "refresh_token": str(refresh_token),
                    "refresh_token_expiry": refresh_token_exp.isoformat(),
                    "user": {
                        'username':user.username,
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number
                    },
                    "message": "User signed up successfully as a vendor",
                }, status=status.HTTP_200_OK)
            else:
                # If OTP is invalid or expired, return error response
                return Response({'error': 'Invalid OTP or OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            # If OTP entry is not found, return error response
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # If any other exception occurs, return generic error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ResendEmailOTPView(APIView):
    """ 
    API endpoint to resend OTP via email.
    """
    def post(self, request):
        email = request.data.get('email')
        try:
            otp_instance = OTP.objects.get(email=email)

            if otp_instance.otp_expiry < timezone.now():
                # If OTP is expired, generate a new OTP and update the expiry time
                otp = generate_otp_code()
                otp_expiry = timezone.now() + timedelta(seconds=40)
                otp_instance.otp_code = otp
                otp_instance.otp_expiry = otp_expiry
                otp_instance.save()

                # Resend OTP email
                send_otp_email(email, otp_instance.otp_code)  # Assuming send_otp_email is defined elsewhere

                return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)
            else:
                # If OTP is not expired, return error indicating OTP resend is not allowed
                return Response({'error': 'OTP resend is not allowed until the previous OTP expires.'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            # If OTP entry does not exist, return error
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)

class VendorLoginView(APIView):
    """
    This end point for login for vendor
    """
    def post(self, request):
        serializer = VendorLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # Get the user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the provided password matches the actual password
            if   user.check_password(password) == False:  # Check password here
                print(password,user.check_password(password))
                return Response({'error': 'Incorrect password'}, status=status.HTTP_401_UNAUTHORIZED)

            # Proceed with successful login
            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Additional vendor data
            vendor_data = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                "phone_number":user.phone_number
            }

            # Return tokens and vendor data to the client
            return Response({
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'vendor': vendor_data,
            }, status=status.HTTP_200_OK)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ForgotPasswordEmailView(APIView):
    """
    This for  senting email  for forgot password option  
    """
    EXPIRY_TIMEDELTA = timedelta(minutes=15)  # Adjust expiry duration as needed

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            
            forgot_password_link(user,email)
            return Response({'success': 'Password reset email sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from .serializers import ForgottPasswordChangeSerializer,ChangePasswordSerializer
from datetime import timedelta,datetime

class ForgottPasswordResetView(APIView):
    """
    This end point for forgott password
    """
    TOKEN_EXPIRATION_DURATION = timedelta(minutes=15)  # Adjust expiry duration as needed

    def patch(self, request, uidb64=None, token=None):
        uidb64 = request.data.get('uidb64', uidb64)
        token = request.data.get('token', token)

        print(token)
        print(uidb64)

        if uidb64 and token:
            return self.handle_password_reset(request, uidb64, token)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_password_reset(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token
        if default_token_generator.check_token(user, token):
            token_expiry_time = datetime.now() +  self.TOKEN_EXPIRATION_DURATION

            # Check if the token has expired
            if token_expiry_time < datetime.now():
                return Response({'error': 'Reset token has expired'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ForgottPasswordChangeSerializer(data=request.data, context={'user': user})
            if serializer.is_valid():
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)




class ChangePasswordView(APIView):
    """
    This end point for changing password
    """

    def post(self, request):
        email = request.session.get('email')  # Assuming you have a function to get email from session
        if email:
            user = User.objects.filter(email=email).first()
            if user:
                serializer = ChangePasswordSerializer(data=request.data)
                if serializer.is_valid():
                    old_password = serializer.validated_data.get('old_password')
                    new_password = serializer.validated_data.get('new_password')
                    confirm_password = serializer.validated_data.get('confirm_password')

                    if new_password != confirm_password:
                        return Response("New password and confirm password do not match")

                    if not user.check_password(old_password):
                        return Response("Incorrect old password")

                    user.set_password(new_password)
                    user.save()
                    return Response({'success': 'Password changed successfully'}, status=200)
                else:
                    return Response(serializer.errors, status=400)
            else:
                return Response({'error': 'User not found'}, status=404)
        else:
            return Response({'error': 'Email not found in session'}, status=400)

from rest_framework.permissions import IsAuthenticated
from .serializers import VendorProfileSerializer



#




class VendorProfileAPIView(APIView):
    """
    View for retrieving and updating user profile information.
    """
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        """
        Retrieve the profile information of the authenticated user.
        """
    
        serializer = VendorProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
        
            # return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        """
        Update the profile information of the authenticated user.
        """
        if request.user.is_authenticated:
            serializer = VendorProfileSerializer(request.user, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        




class ChangeEmailView(APIView):
    """
    this for making option for changing email for vendors
    """
    serializer_class = ChangeEmailSerializer
    def create_otp(self, email):
        """
        Create or update OTP for the given email and password.
        """
        otp = generate_otp_code()
        otp_expiry = timezone.now() + timedelta(seconds=40)
        
        otp_instance, created = OTP.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'otp_expiry': otp_expiry}
        )
        return otp, otp_instance, created

    def post(self, request):
        """
        Generate OTP and send it to the provided email address.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            email = validated_data['email']
            

            try:
                # Check if there's an existing valid OTP for the email
                otp_instance = OTP.objects.get(email=email)
                if otp_instance.otp_expiry >= timezone.now():
                    
                    return Response({'message': 'A valid OTP already exists for this email address.'}, status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                pass

            try:
                # Create or update OTP
                otp, otp_instance, _ = self.create_otp(email)

                # Send OTP email with the generated OTP
                send_otp_email(email, otp)

                # Store email in session
                request.session['email'] = email

                return Response({'message': 'OTP generated and sent successfully'}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyEmailChangeView(APIView):
    def post(self, request):
        # Retrieve email, OTP, and user from request data
        email = request.session.get('email')
        otp_entered = request.data.get('otp')
        user = request.user
        print(user)

        try:
            # Retrieve OTP instance from the database
            otp_instance = OTP.objects.get(email=email)

            # Check if OTP is valid and not expired
            if otp_instance.otp_code == otp_entered and otp_instance.otp_expiry >= timezone.now():
                # Delete the OTP instance as it's no longer needed
                otp_instance.delete()

                # Update user's email address with the new email
                user.email = email
                user.save()

                return Response({'message': 'Email updated successfully'}, status=status.HTTP_200_OK)
            else:
                # If OTP is invalid or expired, return error response
                return Response({'error': 'Invalid OTP or OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            # If OTP entry is not found, return error response
            return Response({'error': 'OTP entry not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # If any other exception occurs, return generic error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
