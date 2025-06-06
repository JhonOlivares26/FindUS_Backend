from django.contrib import admin

from . import models


# TabularInlines
class EventInLine(admin.TabularInline):
    model = models.Event
    extra = 0


class EventRegisteredUserInLine(admin.TabularInline):
    model = models.EventRegisteredUser
    extra = 0


class EventReviewInLine(admin.TabularInline):
    model = models.EventReview
    extra = 0


# Admin
@admin.register(models.EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)
    inlines = [EventInLine]


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "event_organizer", "event_category", "event_date", "paid")
    search_fields = ("event_name", "event_category__name", "event_organizer__email")
    list_filter = ("event_category", "paid", "has_limit")
    ordering = ("-event_date",)
    readonly_fields = ("event_organizer",)
    inlines = [EventRegisteredUserInLine, EventReviewInLine]


@admin.register(models.EventRegisteredUser)
class EventRegisteredUserAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "user",
        "registration_status",
    )
    search_fields = (
        "event__event_name",
        "user__email",
    )
    list_filter = ("event",)
    ordering = ("event",)


@admin.register(models.EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "event",
        "rating",
    )
    search_fields = (
        "user__email",
        "event__event_name",
    )
    list_filter = ("event",)
    ordering = ("event",)


@admin.register(models.Interests)
class InterestsAdmin(admin.ModelAdmin):
    list_display = ("user", "display_interests")
    search_fields = ("user__email",)
    list_filter = ("event_categories",)
    ordering = ("user__email",)

    def display_interests(self, obj):
        return ", ".join([category.name for category in obj.event_categories.all()])

    display_interests.short_description = "Intereses"
