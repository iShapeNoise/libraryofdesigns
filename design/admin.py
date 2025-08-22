from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Design


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'get_full_path', 'level')
    list_filter = ('level',)
    search_fields = ('name',)

    def get_full_path(self, obj):
        return obj.get_full_path()
    get_full_path.short_description = 'Full Path'


# @admin.register(Design)
# class DesignAdmin(admin.ModelAdmin):
#     list_display = ['title', 'created_by', 'created_at', 'tag_list']
#     list_filter = ['tags', 'category', 'created_at']
# 
#     def tag_list(self, obj):
#         return ", ".join(o.name for o in obj.tags.all())
#     tag_list.short_description = 'Tags'


admin.site.register(Design)
