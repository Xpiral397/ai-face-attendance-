import json
import logging
import base64
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from services.face_service import identify_user_by_face, verify_face, register_face

logger = logging.getLogger(__name__)
User = get_user_model()

class FaceAuthConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time face authentication
    This allows for continuous feedback during the authentication process
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        logger.info("WebSocket connection established for face authentication")
        await self.accept()
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to face authentication service'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"WebSocket connection closed with code: {close_code}")
    
    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages
        Messages can be:
        1. face_image - A base64 encoded face image
        2. email - Optional email hint
        3. password - Optional password for 2FA
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'face_frame':
                # Process face image frame
                await self.process_face_frame(data)
            elif message_type == 'auth_request':
                # Process complete authentication request
                await self.process_auth_request(data)
            elif message_type == 'verify_password':
                # Process password verification 
                await self.process_password_verification(data)
            elif message_type == 'registration_request':
                # Process user registration
                await self.process_registration(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unsupported message type: {message_type}'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))
    
    async def process_face_frame(self, data):
        """
        Process a single face frame and provide real-time feedback
        - Detects face quality
        - Identifies user if possible
        - Provides real-time feedback
        """
        face_image = data.get('face_image')
        if not face_image:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No face image provided'
            }))
            return
        
        # First, perform basic validation of the image
        try:
            # Simple validation that it's a valid base64 string
            base64.b64decode(face_image)
            
            # Identify user if possible (in a real app, you'd add face quality checks here)
            # Since database operations block, we use database_sync_to_async
            email = await self.identify_user(face_image)
            
            if email:
                # User identified
                await self.send(text_data=json.dumps({
                    'type': 'face_detected',
                    'status': 'success',
                    'message': 'Face detected and matched',
                    'user_email': email,
                    'next_step': 'password_verification'
                }))
            else:
                # Face not recognized/matched
                await self.send(text_data=json.dumps({
                    'type': 'face_detected',
                    'status': 'unrecognized',
                    'message': 'Face detected but not recognized',
                }))
                
        except Exception as e:
            # Invalid image data or processing error
            logger.error(f"Error processing face frame: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'face_detection_error',
                'message': f'Error processing image: {str(e)}'
            }))
    
    async def process_auth_request(self, data):
        """Process a complete authentication request with face and optional password"""
        face_image = data.get('face_image')
        email_hint = data.get('email')
        password = data.get('password')
        
        if not face_image:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Face image is required'
            }))
            return
        
        try:
            # Step 1: Identify user by face
            if email_hint:
                # If email provided, verify the face matches
                user = await self.get_user_by_email(email_hint)
                if not user:
                    await self.send(text_data=json.dumps({
                        'type': 'auth_error',
                        'message': 'User not found'
                    }))
                    return
                
                # Verify face matches the user
                face_verified = await self.verify_user_face(face_image, str(user.id))
                if not face_verified:
                    await self.send(text_data=json.dumps({
                        'type': 'auth_error',
                        'message': 'Face verification failed'
                    }))
                    return
            else:
                # Identify user by face
                identified_email = await self.identify_user(face_image)
                if not identified_email:
                    await self.send(text_data=json.dumps({
                        'type': 'auth_error',
                        'message': 'Could not identify user from face'
                    }))
                    return
                
                user = await self.get_user_by_email(identified_email)
                if not user:
                    await self.send(text_data=json.dumps({
                        'type': 'auth_error',
                        'message': 'Identified user not found in database'
                    }))
                    return
            
            # Step 2: Verify password if provided
            if password:
                authenticated_user = await self.authenticate_user(user.username, password)
                if not authenticated_user:
                    await self.send(text_data=json.dumps({
                        'type': 'auth_error',
                        'message': 'Password verification failed',
                        'step': 'password'
                    }))
                    return
                user = authenticated_user
            else:
                # For development only - in production, always require password
                logger.warning(f"WebSocket face login without password for user: {user.email}")
            
            # If we get here, face and password (if provided) are verified
            # Generate tokens
            tokens = await self.generate_tokens(user)
            user_data = await self.get_user_data(user)
            
            # Return success response
            await self.send(text_data=json.dumps({
                'type': 'auth_success',
                'message': 'Authentication successful',
                'tokens': tokens,
                'user': user_data
            }))
            
        except Exception as e:
            logger.error(f"Error in WebSocket authentication: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'auth_error',
                'message': f'Authentication error: {str(e)}'
            }))
    
    async def process_password_verification(self, data):
        """Process password verification for a user identified by face"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Email and password are required'
            }))
            return
        
        try:
            # Get user by email
            user = await self.get_user_by_email(email)
            if not user:
                await self.send(text_data=json.dumps({
                    'type': 'auth_error',
                    'message': 'User not found'
                }))
                return
            
            # Verify password
            authenticated_user = await self.authenticate_user(user.username, password)
            if not authenticated_user:
                await self.send(text_data=json.dumps({
                    'type': 'auth_error',
                    'message': 'Password verification failed',
                    'step': 'password'
                }))
                return
            
            # Generate tokens
            tokens = await self.generate_tokens(authenticated_user)
            user_data = await self.get_user_data(authenticated_user)
            
            # Return success response
            await self.send(text_data=json.dumps({
                'type': 'auth_success',
                'message': 'Authentication successful',
                'tokens': tokens,
                'user': user_data
            }))
            
        except Exception as e:
            logger.error(f"Error in password verification: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'auth_error',
                'message': f'Authentication error: {str(e)}'
            }))
    
    async def process_registration(self, data):
        """Process user registration with face image"""
        username = data.get('username')
        email = data.get('email')
        full_name = data.get('full_name', '')
        password = data.get('password')
        face_image = data.get('face_image')
        
        # Validate required fields
        if not all([username, email, password, face_image]):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Username, email, password, and face image are required'
            }))
            return
        
        try:
            # Check if user with email already exists
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'User with this email already exists'
                }))
                return
            
            # Check if username is taken
            existing_username = await self.get_user_by_username(username)
            if existing_username:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Username is already taken'
                }))
                return
            
            # Create new user
            user = await self.create_user(username, email, password, full_name)
            
            # Register face for the user
            face_registered = await self.register_face(face_image, str(user.id))
            if not face_registered:
                # If face registration fails, delete the user and return error
                await self.delete_user(user.id)
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Failed to register face. Please try again.'
                }))
                return
            
            # Generate tokens
            tokens = await self.generate_tokens(user)
            user_data = await self.get_user_data(user)
            
            # Return success response
            await self.send(text_data=json.dumps({
                'type': 'registration_success',
                'message': 'Registration successful',
                'tokens': tokens,
                'user': user_data
            }))
            
        except Exception as e:
            logger.error(f"Error in user registration: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Registration error: {str(e)}'
            }))
    
    # Database/business logic methods - must be wrapped with database_sync_to_async
    
    @database_sync_to_async
    def identify_user(self, face_image):
        """Identify a user by their face image"""
        return identify_user_by_face(face_image)
    
    @database_sync_to_async
    def verify_user_face(self, face_image, user_id):
        """Verify a user's face against their stored face data"""
        return verify_face(face_image, user_id)
    
    @database_sync_to_async
    def register_face(self, face_image, user_id):
        """Register a face for a user"""
        return register_face(face_image, user_id)
    
    @database_sync_to_async
    def get_user_by_email(self, email):
        """Get a user by email"""
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_by_username(self, username):
        """Get a user by username"""
        try:
            return User.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
    
    @database_sync_to_async
    def create_user(self, username, email, password, full_name):
        """Create a new user"""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role='student'  # Default role
        )
        return user
    
    @database_sync_to_async
    def delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    @database_sync_to_async
    def authenticate_user(self, username, password):
        """Authenticate a user with username and password"""
        return authenticate(username=username, password=password)
    
    @database_sync_to_async
    def generate_tokens(self, user):
        """Generate JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
    @database_sync_to_async
    def get_user_data(self, user):
        """Get user data for the response"""
        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        } 