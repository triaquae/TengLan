from django.contrib import admin

# Register your models here.


from analyse import models


class SiteAdmin(admin.ModelAdmin):
    list_display = ('id','url','name','enabled')

class RegionAdmin(admin.ModelAdmin):
    list_display = ('id','region_id','region_type','name','child_of')
    list_filter = ('region_type','child_of')
admin.site.register(models.UserProfile)
admin.site.register(models.Site,SiteAdmin)
admin.site.register(models.Region,RegionAdmin)