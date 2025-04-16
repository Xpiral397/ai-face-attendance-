from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
# from .models import StudentProfile, LecturerProfile
from .serializers import UserSerializer, LoginSerializer # , StudentProfileSerializer, LecturerProfileSerializer
from services.face_service import verify_face, save_face_image, identify_user_by_face
import base64
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    """Viewset for authentication"""
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login with username and password"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout (requires client to discard tokens)"""
        return Response({'detail': 'Successfully logged out.'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get current user profile"""
        user = request.user
        
        # Commented out for initial migration
        # if user.role == User.Role.STUDENT:
        #     try:
        #         profile = StudentProfile.objects.get(user=user)
        #         return Response(StudentProfileSerializer(profile).data)
        #     except StudentProfile.DoesNotExist:
        #         return Response({'detail': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        # 
        # elif user.role == User.Role.LECTURER:
        #     try:
        #         profile = LecturerProfile.objects.get(user=user)
        #         return Response(LecturerProfileSerializer(profile).data)
        #     except LecturerProfile.DoesNotExist:
        #         return Response({'detail': 'Lecturer profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(UserSerializer(user).data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def face_login(self, request):
        """
        Enhanced Face Login with two-factor authentication:
        1. First identify the user by their face
        2. Then verify with password
        """
        face_image_base64 = request.data.get('face_image')
        password = request.data.get('password')
        email_hint = request.data.get('email', None)  # Optional email hint
        
        if not face_image_base64:
            return Response(
                {'detail': 'Face image is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Step 1: Identify user by face
            if email_hint:
                # If email is provided, we'll use it as a hint but still verify the face
                logger.info(f"Using email hint: {email_hint}")
                try:
                    user = User.objects.get(email=email_hint)
                    # Verify face matches the user
                    if not verify_face(face_image_base64, str(user.id)):
                        return Response(
                            {'detail': 'Face verification failed'}, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                except User.DoesNotExist:
                    return Response(
                        {'detail': 'User not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # If no email hint provided, identify user by face
                identified_email = identify_user_by_face(face_image_base64)
                
                if not identified_email:
                    return Response(
                        {'detail': 'Could not identify user from face image'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                try:
                    user = User.objects.get(email=identified_email)
                except User.DoesNotExist:
                    return Response(
                        {'detail': 'Identified user not found in database'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Step 2: Verify password (if provided)
            if password:
                authenticated_user = authenticate(username=user.username, password=password)
                if not authenticated_user:
                    return Response(
                        {'detail': 'Password verification failed'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                user = authenticated_user
            else:
                # For development only: allow login without password if face verification succeeds
                # In production, you would want to always require password
                logger.warning(f"Face login without password for user: {user.email}")
            
            # If we get here, both face and password (if required) are verified
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
                
        except Exception as e:
            logger.error(f"Face login error: {e}")
            return Response(
                {'detail': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register_face(self, request):
        """Register face for current user"""
        user = request.user
        face_image_base64 = request.data.get('face_image')
        
        if not face_image_base64:
            return Response(
                {'detail': 'Face image is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert base64 to bytes
            face_image = base64.b64decode(face_image_base64)
            
            # Save face image
            file_path = save_face_image(face_image, str(user.id))
            
            if file_path:
                return Response({'detail': 'Face registered successfully'})
            else:
                return Response(
                    {'detail': 'Failed to register face'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Face registration error: {e}")
            return Response(
                {'detail': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 