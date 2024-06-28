from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password_confirm', 'email', 'age', 'can_be_contacted', 'can_data_be_shared']

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data
    
    def validate_age(self, value):
        if value < 15:
            raise serializers.ValidationError('Vous devez avoir au moins 15ans')
        return value
    
    def create(self, validated_data):
        # Remove password_confirm from the validated data
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            age=validated_data['age'],
            can_be_contacted=validated_data['can_be_contacted'],
            can_data_be_shared=validated_data['can_data_be_shared']
        )
        return user
    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        request = self.context.get('request', None)
        if not instance.can_data_be_shared:
            if request and instance != request.user:
                representation.pop('email', None)
                representation.pop('age', None)
                representation.pop('can_be_contacted', None)
        if not instance.can_be_contacted:
            if request and instance != request.user:
                representation.pop('email', None)
        return representation


class UserDetailSerializer(UserListSerializer):
    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields
        
    def update(self, instance, validated_data):
        # Remove password_confirm from the validated data
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
            
            

