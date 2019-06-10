from rest_framework import serializers
from .models import Profile
import re

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'bio',
                  'image', 'gender', 'location', 'birth_date','created_at','updated_at')
        read_only_fields = ('username','created_at')

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return 'https://static.productionready.io/images/smiley-cyrus.jpg'

    def check_for_digits(self,field):

        if re.search(r'^[A-Za-z]+$', field) is None:
            raise serializers.ValidationError(
                'This field can only contain letters atleast 1 in length'
            )

    def validate_first_name(self, first_name):

        if first_name:
            self.check_for_digits(first_name)
        return first_name
            

    def validate_last_name(self, last_name):

        if last_name:
            self.check_for_digits(last_name)
        return last_name