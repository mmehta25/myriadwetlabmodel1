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
    def display_processinstances(self):
        return ', '.join(str(processinstances.subname) for processinstances in self.processinstance_set.all())
    def labdisplay(self):
        if len(self.processinstance_set.all()) != 0:
            for e in self.processinstance_set.all():
                processinstance = e
                break
            return processinstance.assay.lab
        else:
            return Lab.objects.get(from_template=True)
    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('instrument-detail', args=[str(self.id)])

class InstrumentInstance(models.Model):
    """Model representing a specific copy of an instrument (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular instrument')

    #Foreign key used because an instrument instance can only have one instrument, but an instrument can have multiple instances of itself.
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, null=True)
    samples_per_day = models.IntegerField()
    identical_copies = models.IntegerField()

    def labdisplay(self):
        if len(self.instrument.processinstance_set.all()) != 0:
            for e in self.instrument.processinstance_set.all():
                processinstance = e
            return processinstance.assay.lab
        else:
            return None

    integrated_or_walkup_choices = (
        ('Integrated', 'Integrated'),
        ('Walkup', 'Walkup')
    )

    integrated_or_walkup = models.CharField(
        max_length=10,
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
    #lab = models.ForeignKey("Lab", on_delete=models.CASCADE, blank=True, null=True)

    def display_processinstanceinst(self):
    	"""Create a string for the Assay. This is required to display assays in Admin."""
    	return ', '.join(str(processinstances.subname) for processinstances in self.processinstance_set.all())

    display_processinstanceinst.short_description = 'Process Instances'

    def labdisplay(self):
        if len(self.processinstance_set.all()) != 0:
            for e in self.processinstance_set.all():
                processinstance = e
                break
            return processinstance.assay.lab
        else:
            return None

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class ProcessInstance(models.Model):
    subname = models.CharField(max_length=25)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, blank=True, null=True, default=1)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=True, default=1)
    assay = models.ForeignKey('Assay', on_delete=models.CASCADE, null=True, default=1)
    duration = models.DecimalField(max_digits=4, decimal_places=2, help_text='Duration in hours')
    sample_count = models.IntegerField(help_text='# of samples to process')
    step_number = models.IntegerField(default=0, help_text="Enter the Step Number of this process.")
    only_walkup = models.BooleanField(default = False, help_text='True if the process cannot be automated')
    def labdisplay(self):
        return self.assay.lab

    def get_absolute_url(self):
        return reverse('Process-detail', args=[str(self.id)])
    def __str__(self):
        return f'{self.subname}'
    class Meta:
        verbose_name = "ProcessInstance"
        verbose_name_plural = "ProcessInstances"

class Assay(models.Model):
    """Model representing an Assay."""
    name = models.CharField(max_length=25)
    lab = models.ForeignKey('Lab', on_delete=models.CASCADE, default=1)
    samples_per_batch = models.IntegerField('Samples per batch', unique=False)
    projection_for_year_1 = models.IntegerField('Projection for next year', unique=False)
    projection_for_year_2 = models.IntegerField('Projection for 2 years from now', unique=False)
    projection_for_year_3 = models.IntegerField('Projection for 3 years from now', unique=False)
    projection_for_year_4 = models.IntegerField('Projection for 4 years from now', unique=False)
    projection_for_year_5 = models.IntegerField('Projection for 5 years from now', unique=False)
    projection_for_year_6 = models.IntegerField('Projection for 6 years from now', unique=False)

    def display_processinstances(self):
        return ', '.join(str(processinstances.subname) for processinstances in self.processinstance_set.all())
    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('Assay-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class Lab(models.Model):
    """Model representing a lab."""
    name = models.CharField(max_length=20)
    current_year = models.IntegerField('Starting Year', unique=False, default=2021)
    days_per_month = models.IntegerField('Days per month', unique=False,
                             help_text='Enter assumption for working days per month')

    integrated_hours = models.DecimalField('Integrated Hours', max_digits=4, decimal_places=2, unique=False,
                             help_text='Enter assumption for integrated hours per day')

    walkup_hours = models.DecimalField('Walkup Hours', max_digits=4, decimal_places=2,unique=False,
                             help_text='Enter assumption for walkup hours per day')

    max_utilization = models.DecimalField('Max utilization', max_digits=4, decimal_places=2, 
                            help_text='Enter the instrument maximum utilization in %')
    offset = models.DecimalField('Offset', max_digits=4, decimal_places=2, 
                            help_text='Offset is the factor multiplied to duration estimates')

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    from_template = models.BooleanField(default=False)
    def get_absolute_url(self):
        """Returns the url to access a particular lab instance."""
        return reverse('my-created')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'


class LabAnalysis(models.Model):
    """Model performing calculations on a lab."""
    lab = models.OneToOneField(Lab, on_delete=models.CASCADE, primary_key=True)
    failure_rate = models.DecimalField('Failure Rate', max_digits=4, decimal_places=2, unique=False,
        default=0)

    def instrument_utilization_samples(self, instrument, year):
        projections = {}
        y = self.lab.current_year
        for assay in self.lab.assay_set.all():
            projections[assay.name] = {
                (y + 1): int(assay.projection_for_year_1),
                (y + 2): int(assay.projection_for_year_2),
                (y + 3): int(assay.projection_for_year_3),
                (y + 4): int(assay.projection_for_year_4),
                (y + 5): int(assay.projection_for_year_5),
                (y + 6): int(assay.projection_for_year_6)
            }

        daysperyear = int(self.lab.days_per_month) * 12
        instruments = []
        assay_sample_volume = []

        for assay in self.lab.assay_set.all():
            instrument_in_assay = False
            for process in assay.processinstance_set.all():
                for instrumentinstance in process.instrument.instrumentinstance_set.all():
                    if instrumentinstance.instrument.name == instrument.name:
                        instrument_in_assay = True
                        if instrumentinstance.integrated_or_walkup == 'Integrated':
                            instruments.append(instrumentinstance)

                        if instrumentinstance.integrated_or_walkup == 'Walkup':
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
        y = self.lab.current_year
        for assay in self.lab.assay_set.all():
            projections[assay.name] = {
                (y + 1): int(assay.projection_for_year_1),
                (y + 2): int(assay.projection_for_year_2),
                (y + 3): int(assay.projection_for_year_3),
                (y + 4): int(assay.projection_for_year_4),
                (y + 5): int(assay.projection_for_year_5),
                (y + 6): int(assay.projection_for_year_6)
            }
        offset = float(self.lab.offset)
        num_integrated = 0
        num_walkup = 0
        processes_using_instrument = []
        sample_counts = []
        volume_projections = []
        seen_instrument = False
        for assay in self.lab.assay_set.all():
            instrument_in_assay = False
            for processinst in assay.processinstance_set.all():
                if processinst.instrument.name == instrument.name:
                    instrument_in_assay = True
                    sample_counts.append(processinst.sample_count)
                    processes_using_instrument.append(processinst)
                    if not seen_instrument:
                        for instrumentinstance in processinst.instrument.instrumentinstance_set.all():
                            if instrumentinstance.integrated_or_walkup == 'Integrated':
                                num_integrated += int(instrumentinstance.identical_copies)
                            if instrumentinstance.integrated_or_walkup == 'Walkup':
                                num_walkup += int(instrumentinstance.identical_copies)
                        seen_instrument = True
                    if instrument_in_assay:
                        volume = projections[assay.name][year]
                        volume_projections.append(volume)

        if len(volume_projections) != len(sample_counts):
            print("Error: length of volume projections (", str(len(volume_projections)), ") does not match length of sample counts (", str(len(sample_counts)), ")")

        durations = [offset*float(process.duration) for process in processes_using_instrument]
        total_run_hours_by_process = [(volume_projections[i]/(int(self.lab.days_per_month)*12*int(sample_counts[i])))*float(durations[i]) for i in range(len(volume_projections))]
        total_run_hours = sum(total_run_hours_by_process)

        utilization = total_run_hours/(num_integrated*int(self.lab.integrated_hours) + num_walkup*int(self.lab.walkup_hours))
        return utilization
    
