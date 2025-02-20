from rest_framework import serializers

from .models import Event, EventCategory, EventRegisteredUser, EventReview, Interests


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = "__all__"


class InterestsSerializer(serializers.ModelSerializer):
    event_categories = EventCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Interests
        fields = ["id", "user", "event_categories"]


class InterestsWriteSerializer(serializers.ModelSerializer):
    event_categories = serializers.PrimaryKeyRelatedField(
        queryset=EventCategory.objects.all(), many=True
    )

    class Meta:
        model = Interests
        exclude = ["user"]


class EventSerializer(serializers.ModelSerializer):
    event_category = EventCategorySerializer(read_only=False)
    event_organizer = serializers.StringRelatedField()

    class Meta:
        model = Event
        fields = "__all__"


class EventWriteSerializer(serializers.ModelSerializer):
    event_category = serializers.PrimaryKeyRelatedField(queryset=EventCategory.objects.all())

    class Meta:
        model = Event
        exclude = ["event_organizer"]


class EventRegisteredUserSerializer(serializers.ModelSerializer):
    event = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = EventRegisteredUser
        fields = "__all__"


class EventRegisteredUserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegisteredUser
        exclude = ["user"]


class EventReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    event = serializers.StringRelatedField()

    class Meta:
        model = EventReview
        fields = "__all__"


class EventReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReview
        exclude = ["user"]
