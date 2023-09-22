from recipes.models import Follow
from rest_framework import serializers

from .models import CustomUser as User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribe",
        )

    def get_is_subscribe(self, obj):
        request = self.context.get("request")
        if request.user.is_authenticated:
            if Follow.objects.filter(
                user=request.user.id, following=obj.id
            ).exists():
                return True
        return False
