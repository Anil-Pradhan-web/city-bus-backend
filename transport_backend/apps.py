from django.apps import AppConfig
from django.contrib import admin

class AdminConfig(AppConfig):
    name = 'transport_backend'

    def ready(self):
        admin.site.site_header = 'City Bus Admin Panel'
        admin.site.site_title = 'Transport Control'
        admin.site.index_title = 'System Administration'
