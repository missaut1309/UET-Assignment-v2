from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(WorkPlace)
admin.site.register(Degree)
admin.site.register(Topic)
admin.site.register(Lecturer)
admin.site.register(Keyword)
admin.site.register(TopicToKeyword)
admin.site.register(LecturerToKeyword)
admin.site.register(MyCommittee)
admin.site.register(MyGroup)
admin.site.register(Position)
admin.site.register(Department)