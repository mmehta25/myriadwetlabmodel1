from django.contrib import admin
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance, LabAnalysis
# Register your models here.

# admin.site.register(Lab)
# admin.site.register(Assay)
# admin.site.register(Process)
# admin.site.register(Instrument)
# admin.site.register(InstrumentInstance)

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_year', 'creator', 'from_template', 'days_per_month', 'integrated_hours', 'walkup_hours')

@admin.register(Assay)
class AssayAdmin(admin.ModelAdmin):
    list_display = ('name', 'lab', 'display_processinstances', 'id', 'samples_per_batch')

class ProcessInstanceInline(admin.TabularInline):
	extra = 0
	model = ProcessInstance

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'labdisplay', 'display_processinstanceinst')
    inlines = [ProcessInstanceInline]

@admin.register(LabAnalysis)
class LabAnalysisAdmin(admin.ModelAdmin):
    list_display = ('lab', )

@admin.register(ProcessInstance)
class ProcessInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'assay', 'labdisplay', 'process', 'instrument', 'subname', 'duration', 'sample_count')

class InstrumentsInstanceInline(admin.TabularInline):
	extra = 0
	model = InstrumentInstance

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'labdisplay', 'display_processinstances')
    inlines = [InstrumentsInstanceInline]

@admin.register(InstrumentInstance)
class InstrumentInstanceAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'labdisplay', 'samples_per_day', 'integrated_or_walkup', 'identical_copies')
    fieldsets = (
        (None, {
            'fields': ('instrument', 'samples_per_day', 'id')
        }),
        ('Instance Specific Details', {
            'fields': ('integrated_or_walkup', 'identical_copies')
        }),
    )

