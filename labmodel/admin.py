from django.contrib import admin
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance
# Register your models here.

# admin.site.register(Lab)
# admin.site.register(Assay)
# admin.site.register(Process)
# admin.site.register(Instrument)
# admin.site.register(InstrumentInstance)

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'days_per_month', 'integrated_hours', 'walkup_hours')

@admin.register(Assay)
class AssayAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'sample_count')

@admin.register(ProcessInstance)
class ProcessInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'subname')

class InstrumentsInstanceInline(admin.TabularInline):
	extra = 0
	model = InstrumentInstance

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'samples_per_day')
    inlines = [InstrumentsInstanceInline]

@admin.register(InstrumentInstance)
class InstrumentInstanceAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'integrated_or_walkup', 'identical_copies')
    fieldsets = (
        (None, {
            'fields': ('instrument', 'id')
        }),
        ('Instance Specific Details', {
            'fields': ('integrated_or_walkup', 'identical_copies')
        }),
    )

