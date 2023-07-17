from azure.cognitiveservices.vision.computervision import ComputerVisionClient
import urllib.parse
from msrest.authentication import CognitiveServicesCredentials
from rest_framework import serializers
from azure.storage.blob import BlobServiceClient

from backend.models import Image, User, Tag

STORAGE_ACCOUNT_KEY = "arA7TUUYt4C48PbZ/SRTp/dwWmGrJJ7pmm6z6x+7Hfc96c7zHawZITYbP+PD0vrSA/nw3A8JSxZC+AStyknoGg=="
STORAGE_ACCOUNT_NAME = "s3stockage"
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=s3stockage;AccountKey=arA7TUUYt4C48PbZ/SRTp/dwWmGrJJ7pmm6z6x+7Hfc96c7zHawZITYbP+PD0vrSA/nw3A8JSxZC+AStyknoGg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "bucket"

COMPUTER_VISION_SUBSCRIPTION_KEY = "b06743608e3640b68884a8e1a67f4a9c"
COMPUTER_VISION_ENDPOINT = "https://imgrecognizer.cognitiveservices.azure.com/"

def upload_to_to_blob_storage(file_path, file_name):
    """
    Upload file to blob storage
    :param file_path:
    :param file_name:
    :return:
    """
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_name)
    blob_client.upload_blob(file_path)
    return  urllib.parse.unquote(blob_client.url)


def get_tags_from_image(image_url):
    """
    Get tags from image url using azure computer vision
    :param image_url:
    :return:
    """
    computer_vision_client = ComputerVisionClient(COMPUTER_VISION_ENDPOINT, CognitiveServicesCredentials(COMPUTER_VISION_SUBSCRIPTION_KEY))
    tags_result_remote = computer_vision_client.tag_image(image_url)
    tags = []
    for tag in tags_result_remote.tags:
        if tag.confidence > 0.9:
            tags.append(tag.name)
    return tags


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    class Meta:
        """
        Metaclass for user serializer
        """
        model = User
        fields = ('id', 'username', 'email', 'password')
        id = serializers.IntegerField(read_only=True)
        username = serializers.CharField(required=True, allow_blank=False, max_length=255)
        email = serializers.EmailField(required=True, allow_blank=False, max_length=255)
        password = serializers.CharField(required=True, allow_blank=False, max_length=1000)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create user
        :param validated_data:
        :return:
        """
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance



class ImageSerializer(serializers.ModelSerializer):
    """
    Image serializer
    """
    class Meta:
        """
        Meta class for image serializer
        """
        model = Image
        fields = "__all__"

    def create(self, validated_data):
        """
        Create image
        :param validated_data:
        :return:
        """
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")
        validated_data["image"]  = upload_to_to_blob_storage(image, image.name)
        detected_tags = get_tags_from_image(validated_data["image"])

        image = Image.objects.create(**validated_data)
        for tag in detected_tags:
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            image.tags.add(tag_obj)
        return image
