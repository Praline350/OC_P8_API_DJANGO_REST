from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # Appel de la méthode get_user de la classe parente pour obtenir l'utilisateur à partir du jeton validé
        user = super().get_user(validated_token)
        
        # Vérifie si l'utilisateur est actif
        if not user.is_active:
            # Si l'utilisateur est inactif, une exception AuthenticationFailed est levée
            raise AuthenticationFailed('User is inactive')
        
        # Si l'utilisateur est actif, il est retourné
        return user

