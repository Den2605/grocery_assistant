from djoser.serializers import UserSerializer
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer):
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = {
            "email": data["email"],
            "id": data["id"],
            "username": data["username"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "password": data["password"],
        }
        return data
