from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
        Serializer for user registration.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_confirmed_password(self, value):
        """
            Ensure confirmed password matches the original password.
        """
        password = self.initial_data.get('password')
        if password != value:
            raise serializers.ValidationError('Passwords do not match.')
        return value
    
    def validate_email(self, value):
        """
            Check if the email is already in use.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email exists already.')
        return value
    
    def create(self, validated_data):
        """
            Create a new user with the provided data, set is_active to False.
        """
        validated_data.pop('confirmed_password')
        username = validated_data.get('email')
        return User.objects.create_user(username=username, **validated_data, is_active=False)


class ActivateSerializer(serializers.ModelSerializer):
    """
        Serializer to activate a user's account.
    """

    class Meta:
        model = User 
        fields = ['is_active']

    def update(self, instance, validated_data):
        """
            Set the user's is_active status to True.
        """
        instance.is_active = True 
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    """
        Serializer for user login using email and password.
        Overrides default TokenObtainPairSerializer.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """
            Remove username field from TokenObtainPairSerializer.
        """
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields.pop('username')

    def validate(self, attrs):
        """
            Validate email and password, check user is active
        """
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email or Password is not valid')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Email or Password is not valid')
        
        if not user.is_active:
            raise serializers.ValidationError('Email or Password is not valid')
        
        data = super().validate({'username': user.username, 'password': password})
        data['user'] = user
        return data


class PasswordConfirmSerializer(serializers.ModelSerializer):
    """
        Serializer for setting a new password, with confirmation.
    """
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ['new_password', 'confirm_password']

    def validate_confirm_password(self, value):
        """
             Ensure the confirmed password matches the new password.
        """
        password = self.initial_data.get('new_password')
        if password != value:
            raise serializers.ValidationError('Passwords do not match.')
        return value

    def update(self, instance, validated_data):
        """
            Set a new password for the user.
        """
        validated_data.pop('confirm_password')
        new_password = validated_data.pop('new_password')
        instance.set_password(new_password) 
        instance.save()
        return instance
