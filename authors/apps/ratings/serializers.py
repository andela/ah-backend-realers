from rest_framework import serializers
from .models import Rating


class RatingSerializers(serializers.ModelSerializer):
    "create serilizers for Rating article"
    class Meta:
        model = Rating
        fields = ('ratings', 'username')

    def validate_ratings(self, ratings):
        if ratings < 1 or ratings > 5:
            raise serializers.ValidationError("Number ratings should be 1 to 5")
        return ratings
