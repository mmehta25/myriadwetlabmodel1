from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Instrument(models.Model):
    """Model representing a generic instrument."""
    name = models.CharField(max_length=10)
    samples_per_day = models.CharField(max_length=10)

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
    process = models.ForeignKey('Process', on_delete=models.RESTRICT, null=True, default=1)

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
    duration = models.CharField(max_length=10, help_text='Duration in hours')
    sample_count = models.CharField(max_length=10, help_text='# of samples to process')

    def display_instrumentinst(self):
    	"""Create a string for the Assay. This is required to display assays in Admin."""
    	return ', '.join(str(instruments.id) + "(" + instruments.instrument.name + ")" for instruments in self.instruments.all()[:5])

    display_instrumentinst.short_description = 'Instrument Instances'

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class ProcessInstance(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular process instance')
	subname = models.CharField(max_length=25)
	process = models.ForeignKey(Process, on_delete=models.RESTRICT, null=True, default=1)
	assay = models.ForeignKey('Assay', on_delete=models.RESTRICT, null=True, default=1)
	def get_absolute_url(self):
		return reverse('Process-detail', args=[str(self.id)])
	def __str__(self):
		return f'{self.subname}'
    # instruments = models.ManyToManyField(InstrumentInstance, help_text='Select instrument instances for this process')

    # def display_instrumentinst(self):
    # 	"""Create a string for the Assay. This is required to display assays in Admin."""
    # 	return ', '.join(str(instruments.id) + "(" + instruments.instrument.name + ")" for instruments in self.instruments.all()[:5])

    #display_instrumentinst.short_description = 'Instrument Instances'


class Assay(models.Model):
    """Model representing an Assay."""
    name = models.CharField(max_length=25)

    # ManyToManyField used because an assay can consist of many processes. A process can be a part of multiple assays.
    #processes = models.ManyToManyField(Process, help_text='Select processes for this assay')
    lab = models.ForeignKey('Lab', on_delete=models.CASCADE, default=1)
    # def display_process(self):
    # 	"""Create a string for the Process. This is required to display processes in Admin."""
    # 	return ', '.join(process.name for process in self.processes.all()[:5])

    # display_process.short_description = 'Processes'
    class Meta:
        verbose_name = "Assay"
        verbose_name_plural = "Assays"

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('Assay-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'

class Lab(models.Model):
    """Model representing a lab."""
    name = models.CharField(max_length=25)
    days_per_month = models.CharField('days_per_month', max_length=2, unique=False,
                             help_text='Enter assumption for working days per month')
    integrated_hours = models.CharField('integrated_hours', max_length=2, unique=False,
                             help_text='Enter assumption for integrated hours per day')
    walkup_hours = models.CharField('walkup_hours', max_length=2, unique=False,
                             help_text='Enter assumption for walkup hours per day')
    #assay = models.ManyToManyField(Assay, help_text='Select an assay for this lab')

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # def display_assay(self):
    # 	"""Create a string for the Assay. This is required to display assays in Admin."""
    # 	return ', '.join(assay.name for assay in self.assay.all()[:5])

    # display_assay.short_description = 'Assays'

    def get_absolute_url(self):
        """Returns the url to access a particular lab instance."""
        return reverse('my-created')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'