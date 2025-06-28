from django.contrib import admin

from .models import User, MissingPersonReport, ModerationLog,ReportMessage

admin.site.register(User)
admin.site.register(MissingPersonReport)
admin.site.register(ModerationLog)
admin.site.register(ReportMessage)
