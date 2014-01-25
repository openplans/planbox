from django.contrib import admin
from genericadmin.admin import GenericAdminModelAdmin
from planbox_data.models import Profile, Project, Event


class ProfileAdmin (admin.ModelAdmin):
    filter_horizontal = ('organizations',)
    raw_id_fields = ('auth',)


class EventInline (admin.TabularInline):
    model = Event
    extra = 2
    readonly_fields = ('index',)


class ProjectAdmin (GenericAdminModelAdmin):
    list_display = ('__unicode__', 'owner', 'slug', 'status', 'public')
    list_filter = ('status',)
    prepopulated_fields = {"slug": ("title",)}

    inlines = (
        EventInline,
    )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
