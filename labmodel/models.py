from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Instrument(models.Model):
    """Model representing a generic instrument."""
    name = models.CharField(max_length=10)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('instrument-detail', args=[str(self.id)])

class InstrumentInstance(models.Model):
    """Model representing a specific copy of an instrument (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular instrument')

    #Foreign key used because an instrument instance can only have one instrument, but an instrument can have multiple instances of itself.
    instrument = models.ForeignKey('Instrument', on_delete=models.RESTRICT, null=True)
    processinstance = models.ForeignKey('ProcessInstance', on_delete=models.RESTRICT, null=True, default=1)
    samples_per_day = models.CharField(max_length=10)
    identical_copies = models.CharField(max_length=10)

    integrated_or_walkup_choices = (
        ('i', 'Integrated'),
        ('w', 'Walkup')
    )  
    integrated_or_walkup = models.CharField(
        max_length=1,
        choices=integrated_or_walkup_choices,
        blank=True,
        default='i',
        help_text='Integrated or walkup?',
    )

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.instrument.name})' #self.id will return 1 for first record, etc.

class Process(models.Model):
    """Model representing a Process."""
    name = models.CharField(max_length=25)

    def display_processinstanceinst(self):
    	"""Create a string for the Assay. This is required to display assays in Admin."""
    	return ', '.join(str(processinstances.subname) for processinstances in self.processinstance_set.all())

    display_processinstanceinst.short_description = 'Process Instances'

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class ProcessInstance(models.Model):
	#id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular process instance')
	subname = models.CharField(max_length=25)

	process = models.ForeignKey(Process, on_delete=models.RESTRICT, null=True, default=1)
	assay = models.ForeignKey('Assay', on_delete=models.RESTRICT, null=True, default=1)
	duration = models.CharField(max_length=10, help_text='Duration in hours')
	sample_count = models.CharField(max_length=10, help_text='# of samples to process')

	def get_absolute_url(self):
		return reverse('Process-detail', args=[str(self.id)])
	def __str__(self):
		return f'{self.subname}'
		class Meta:
			verbose_name = "ProcessInstance"
			verbose_name_plural = "ProcessInstances"
    # instruments = models.ManyToManyField(InstrumentInstance, help_text='Select instrument instances for this process')

    # def display_instrumentinst(self):
    # 	"""Create a string for the Assay. This is required to display assays in Admin."""
    # 	return ', '.join(str(instruments.id) + "(" + instruments.instrument.name + ")" for instruments in self.instruments.all()[:5])

    #display_instrumentinst.short_description = 'Instrument Instances'


class Assay(models.Model):
    """Model representing an Assay."""
    name = models.CharField(max_length=25)
    lab = models.ForeignKey('Lab', on_delete=models.CASCADE, default=1)
    projection_for_2021 = models.CharField('Projection for 2021', max_length=10, unique=False)

    projection_for_2022 = models.CharField('Projection for 2022', max_length=10, unique=False)

    projection_for_2023 = models.CharField('Projection for 2023', max_length=10, unique=False)

    projection_for_2024 = models.CharField('Projection for 2024', max_length=10, unique=False)

    projection_for_2025 = models.CharField('Projection for 2025', max_length=10, unique=False)

    projection_for_2026 = models.CharField('Projection for 2026', max_length=10, unique=False)


    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('Assay-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class Lab(models.Model):
    """Model representing a lab."""
    name = models.CharField(max_length=25)

    days_per_month = models.CharField('Days per month', max_length=2, unique=False,
                             help_text='Enter assumption for working days per month')

    integrated_hours = models.CharField('Integrated Hours', max_length=2, unique=False,
                             help_text='Enter assumption for integrated hours per day')

    walkup_hours = models.CharField('Walkup Hours', max_length=2, unique=False,
                             help_text='Enter assumption for walkup hours per day')

    max_utilization = models.DecimalField('Max utilization', max_digits=4, decimal_places=2, 
                            help_text='Enter the instrument maximum utilization in %')
    offset = models.DecimalField('Offset', max_digits=4, decimal_places=2, 
                            help_text='Offset is the factor multiplied to duration estimates')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def get_absolute_url(self):
        """Returns the url to access a particular lab instance."""
        return reverse('my-created')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'


class LabAnalysis(models.Model):
    """Model performing calculations on a lab."""
    lab = models.OneToOneField(Lab, on_delete=models.CASCADE, primary_key=True)

    def instrument_utilization_samples(self, instrument, year):
        projections = {}

        for assay in self.lab.assay_set.all():
            projections[assay.name] = {
                2021: int(assay.projection_for_2021),
                2022: int(assay.projection_for_2022),
                2023: int(assay.projection_for_2023),
                2024: int(assay.projection_for_2024),
                2025: int(assay.projection_for_2025),
                2026: int(assay.projection_for_2026)
            }

        daysperyear = int(self.lab.days_per_month) * 12
        instruments = []
        assay_sample_volume = []

        for assay in self.lab.assay_set.all():
            instrument_in_assay = False
            for process in assay.processinstance_set.all():
                for instrumentinstance in process.instrumentinstance_set.all():
                    if instrumentinstance.instrument.name == instrument.name:
                        instrument_in_assay = True
                        if instrumentinstance.integrated_or_walkup == 'i':
                            instruments.append(instrumentinstance)

                        if instrumentinstance.integrated_or_walkup == 'w':
                            instruments.append(instrumentinstance)

            if instrument_in_assay:
                volume = projections[assay.name][year]
                assay_sample_volume.append(volume)

        max_samplesperday = [int(instrumentinst.identical_copies)*int(instrumentinst.samples_per_day) for instrumentinst in instruments]
        max_samplesperyear = sum(max_samplesperday)*daysperyear
        total_sample_volume = sum(assay_sample_volume)
        utilization = total_sample_volume/max_samplesperyear

        return utilization

    def instrument_utilization_hours(self, instrument, year):
        projections = {}

        for assay in self.lab.assay_set.all():
            projections[assay.name] = {
                2021: int(assay.projection_for_2021),
                2022: int(assay.projection_for_2022),
                2023: int(assay.projection_for_2023),
                2024: int(assay.projection_for_2024),
                2025: int(assay.projection_for_2025),
                2026: int(assay.projection_for_2026)
            }
        offset = float(self.lab.offset)
        num_integrated = 0
        num_walkup = 0
        processes_using_instrument = []
        sample_counts = []
        volume_projections = []

        for assay in self.lab.assay_set.all():
            instrument_in_assay = False
            for processinst in assay.processinstance_set.all():
                for instrumentinstance in processinst.instrumentinstance_set.all():
                    if instrumentinstance.instrument.name == instrument.name:
                        instrument_in_assay = True
                        sample_counts.append(processinst.sample_count)
                        processes_using_instrument.append(processinst)

                        if instrumentinstance.integrated_or_walkup == 'i':
                            num_integrated += int(instrumentinstance.identical_copies)

                        if instrumentinstance.integrated_or_walkup == 'w':
                            num_walkup += int(instrumentinstance.identical_copies)
            if instrument_in_assay:
                volume = projections[assay.name][year]
                volume_projections.append(volume)

        if len(volume_projections) != len(sample_counts):
            print("Error: length of volume projections does not match length of sample counts")

        durations = [offset*float(process.duration) for process in processes_using_instrument]
        total_run_hours_by_process = [(volume_projections[i]/(int(self.lab.days_per_month)*12*int(sample_counts[i])))*float(durations[i]) for i in range(len(volume_projections))]
        total_run_hours = sum(total_run_hours_by_process)

        utilization = total_run_hours/(num_integrated*int(self.lab.integrated_hours) + num_walkup*int(self.lab.walkup_hours))
        return utilization
    
