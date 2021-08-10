from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance, LabAnalysis
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, TemplateView, View
from django.urls import reverse_lazy
from django.urls import reverse
from django.forms.models import inlineformset_factory
from .forms import ProcessInstanceFormSet, InstrumentInstanceFormSet, InstrumentFormSet
from django.shortcuts import redirect
from django.db import transaction
from django.contrib.auth.models import User
from django import forms
import pandas as pd
import plotly.express as px
import plotly
from plotly.offline import plot
import plotly.graph_objects as go
from labmodel.forms import EditInstrumentForm, OffsetSliderForm, AddProcessForm, Labname_form, LabAssumptionsDropdownForm, ProcessDropdownForm, FailureRateDateRangeForm, OffsetForm, LabAnalysisForm, LabForm
import datetime
import snowflake.connector as sf
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from .utils import process_dataframe
from graphviz import Graph

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_labs = Lab.objects.all().count()
    num_instrument_types = Instrument.objects.all().count()

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def snowflake(request):
    if request.method == 'POST':
        form = FailureRateDateRangeForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            date = str(date)
            year = date[:4]
            month = date[5:7]
            day = date[8:]
            creds = {
                "account": "myriad", 
                "user": "mmehta", 
                "database": "PRENATAL_NON_PHI_DB", 
                "warehouse": "LOOKER_WH", 
                "authenticator": "externalbrowser", 
                "role": "PRENATAL_NON_PHI_LOOKER", 
                "password": "dret45onth"
            }
            con = sf.connect(**creds)
            
            snowflake_url = make_url(f'snowflake://{creds["user"]}:xx@{creds["account"]}/{creds["database"]}/RAW?warehouse={creds["warehouse"]}&role={creds["role"]}')
            snowflake_engine = create_engine(snowflake_url, creator=lambda: con)  # will error here without snowflake package 
            connector = con
            cursor = con.cursor()
            engine = snowflake_engine
            sql = f"""SELECT 
                        COUNT(result.id),
                        result.review_state_code
                        FROM GOLD.result as result
                        WHERE (result.created_at < date_from_parts({year}, {month}, {day}) AND result.created_at >= (add_months(date_from_parts({year}, {month}, {day}),-3))) AND review_state_code != -1 AND substring(result.external_id,0,3)='IPS'
                        GROUP BY 2""".format(year=year, month=month, day=day)
            cursor.execute(sql)
            data = []
            data = cursor.fetchall()
            df = pd.DataFrame(data)

            df.columns = ['Count', "Review State Code"]
            if int(month) >= 4:
                low_month = str(int(month) - 3)
                low_year = year
            else:
                low_month = str(12+(int(month)-3))
                low_year = str(int(year)-1)
            failure = sum(list((df.loc[df['Review State Code'] == 0])['Count']))/sum(df['Count'])
            context = {
            "low_date": low_month+"/"+day+"/"+low_year,
            "high_date": month+"/"+day+"/"+year,
            "form": form,
            "rate": failure,
            'failure_rates_df': df.to_html(classes=["table", "table-hover"])
            }
            return render(request, 'labmodel/snowflake.html', context=context)
        else:
            context = {"form": form}
    else:
        form = FailureRateDateRangeForm()
        context = {"form": form}
    
    return render(request, 'labmodel/snowflake.html', context=context)

df_an = pd.read_csv('~/django_projects/myriadwetlab/labmodel/data/instruments.csv')
df_an = df_an.set_index('Instrument type')
df_an = df_an['Asset numbers'].to_dict()

def snowflake2(request):
    if request.method == 'POST':
        form = OffsetForm(request.POST)
        if form.is_valid():
            instruments_string = form.cleaned_data['Instrument']
            key = None
            for k in df_an:
                if df_an[k] == instruments_string:
                    key = k
                    instruments_string = instruments_string[1:-1]
                    break
            creds = {
                "account": "myriad", 
                "user": "mmehta", 
                "database": "PRENATAL_NON_PHI_DB", 
                "warehouse": "LOOKER_WH", 
                "authenticator": "externalbrowser", 
                "role": "PRENATAL_NON_PHI_LOOKER", 
                "password": "dret45onth"
            }
            con = sf.connect(**creds)
            con.close()
            con = sf.connect(**creds)
            
            snowflake_url = make_url(f'snowflake://{creds["user"]}:xx@{creds["account"]}/{creds["database"]}/RAW?warehouse={creds["warehouse"]}&role={creds["role"]}')
            snowflake_engine = create_engine(snowflake_url, creator=lambda: con)  # will error here without snowflake package
            cursor = con.cursor()
            engine = snowflake_engine
            sql = f"""SELECT
                        DISTINCT
                        eq.asset_number,
                        eqt.status,
                        eqt.method_name,
                        eqt.timestamp,
                        js.state_changed_at,
                        js.state
                    FROM GOLD.equipment AS eq
                    INNER JOIN GOLD.labware_op_equipment as loe ON loe.equipment_id=eq.id
                    INNER JOIN GOLD.labware_op AS lo ON lo.id=loe.labwareop_id
                    INNER JOIN GOLD.equipment_timings AS eqt ON eqt.pipeline_job_id=lo.job_id
                    INNER JOIN GOLD.job_state AS js ON js.job_id=lo.job_id
                    WHERE eq.asset_number IN ({instruments_string}) AND eq.active AND eqt.status='DONE'
                    AND eqt.timestamp > date_from_parts(2021, 08, 01) AND eqt.timestamp < date_from_parts(2021, 08, 03)""".format(instruments_string=instruments_string)

            cursor.execute(sql)
            # rows = 0
            # while rows == 0:
            #     dat = cursor.fetchmany(100)
            #     if not dat:
            #         break
            #     df = pd.DataFrame(dat, columns=cursor.description)
            #     rows += df.shape[0]
            data = []
            df = cursor.fetch_pandas_all()
            #data = cursor.fetchall()
           # df = pd.DataFrame(data)


            df.columns = ['ASSET_NUMBER',  'STATUS',  'METHOD_NAME', 'TIMESTAMP',   'STATE_CHANGED_AT',    'STATE']
            res = process_dataframe(df)
            dfs = res['dfs']
            traces = {"x":[], "y1":[], "y2":[]}
            for df in dfs:
                traces['x'].append(df)
                traces["y1"].append(dfs[df]['Offset'])
                traces["y2"].append(dfs[df]['Idle'])
            
            fig = go.Figure(
            data=[go.Box(name=traces['x'][i], y=traces['y1'][i]) for i in range(len(traces['x']))],
            )
            fig['layout'].update(width=900, height=900, autosize=False)
            plot_div1 = plot(fig, output_type='div')


            
            fig2 = go.Figure(
            data=[go.Box(name=traces['x'][i], y=traces['y2'][i]) for i in range(len(traces['x']))],
            layout_title_text="Idle times"
            )
            fig['layout'].update(width=900, height=900, autosize=False)
            plot_div2 = plot(fig2, output_type='div')
            
            context = {
                    "offset_boxplot": plot_div1,
                    "idle_boxplot": plot_div2,
                    "instrument_name": key,
                    "instruments": instruments_string
                }
            return render(request, 'labmodel/snowflake2.html', context=context)
        else:
            context = {"form": form}
    else:
        form = OffsetForm()
        context = {"form": form}
    
    return render(request, 'labmodel/snowflake2.html', context=context)

def scheduleview(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    offset = lab.offset
    walkup_time = lab.walkup_hours
    integrated_hours = datetime.timedelta(hours=int(lab.integrated_hours))
    assays = lab.assay_set.all()
    timings_by_day = {}

    for assay in assays:
        processes = assay.processinstance_set.all()
        a = assay.name
        print(str(a) +"has " + str(len(processes)) + "processes")
        start_total = datetime.datetime(2021, 8, 16, 0, 0, 0)
        total = start_total
        n = 1
        timings_by_day[a] = {}
        timings_by_day[a]["day_"+ str(n)] = []
        process_count = 0
        total_processes = len(processes)
        for process in processes:
            p = process.subname
            dur = process.duration * offset
            hrs = int(round(dur))
            mins = int(round((dur-hrs)*60))
            duration = datetime.timedelta(hours=hrs, minutes=mins)
            if duration > integrated_hours:
                print("Start: " + str(total), "Finish: " + str(total + integrated_hours), "Process: "+ str(p) + "Assay: " + str(a))
                timings_by_day[a]['day_' + str(n)].append({"Start": total, "Finish": total + integrated_hours, "Process": p, "Assay": a})
                integrated_hours_left = integrated_hours - datetime.timedelta(hours=total.hour)
                duration = duration - integrated_hours_left #left over hours for next day
                start_total = start_total + datetime.timedelta(days=1) #switch start to next day
                total = start_total
                n += 1
                timings_by_day[a]['day_' + str(n)] = []
            elif total + duration > start_total + integrated_hours:
                n += 1
                start_total = start_total + datetime.timedelta(days=1) #switch start to next day
                total = start_total
                timings_by_day[a]['day_' + str(n)] = []
            else:
                if total + duration > start_total + datetime.timedelta(hours=int(walkup_time)) and process.only_walkup:
                    n += 1
                    start_total = start_total + datetime.timedelta(days=1) #switch start to next day
                    total = start_total
                    timings_by_day[a]['day_' + str(n)] = []
            timings_by_day[a]['day_' + str(n)].append({"Start": total, "Finish": total + duration, "Process": p, "Assay": a})
            total += duration
            process_count += 1
            if process_count == total_processes:
                if 'IPS' in a:
                    ips_turnaround_time = total - datetime.datetime(2021, 8, 16, 0, 0, 0)
                if 'DTS' in a:
                    dts_turnaround_time = total - datetime.datetime(2021, 8, 16, 0, 0, 0)
    dfs = {}
    for a in timings_by_day:
        for t in timings_by_day[a]:
            df = pd.DataFrame(timings_by_day[a][t])
            if t in dfs:
                dfs[t] = pd.concat([dfs[t], df])
            else:
                dfs[t] = df
    plots = []
    day = 0
    for t in dfs:
        day += 1
        #plots.append(dfs[t].to_html(classes=["table", "table-hover"]))
        fig = px.timeline(dfs[t], x_start="Start", x_end="Finish", y="Process", color="Assay", title="Day " + str(day) + ": ")
        plots.append(plot(fig, output_type='div'))
    context = {
        "plots":plots,
        "dts_time": dts_turnaround_time,
        "ips_time": ips_turnaround_time,
        "lab": lab,
    }
    return render(request, 'schedule.html', context=context)


class UserLabsListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing labs created by current user."""
    model = Lab
    template_name ='labmodel/user_labs.html'

    def get_queryset(self):
        return Lab.objects.filter(creator=self.request.user)

def make_clone(request, pk):
    if request.method == 'POST':
        cloned_instruments = {}
        cloned_processes = {}
        if 'make_clone' in request.POST:
            lab = get_object_or_404(Lab, pk=pk)
            lab.pk = None
            lab.creator = request.user
            lab.name = str(lab.name) + "_" + str(request.user.username)
            lab.from_template = False
            lab.save()
            old_lab = Lab.objects.get(pk=pk)
            for assay in old_lab.assay_set.all():
                old_assay_pk = assay.pk
                assay.pk = None
                assay.lab = lab
                assay.save()
                old_assay = Assay.objects.get(pk=old_assay_pk)
                for processinstance in old_assay.processinstance_set.all():
                    if processinstance.process.name not in cloned_processes:
                        process = processinstance.process
                        process.pk = None
                        process.save()
                        cloned_processes[process.name] = process.pk
                    else:
                        process = Process.objects.get(pk=cloned_processes[processinstance.process.name])
                    old_processinstance_pk = processinstance.pk
                    processinstance.pk = None
                    processinstance.assay = assay
                    processinstance.process = process
                    old_processinstance = ProcessInstance.objects.get(pk=old_processinstance_pk)

                    old_instrument_pk = old_processinstance.instrument.pk
                    old_instrument = Instrument.objects.get(pk=old_instrument_pk)

                    if old_processinstance.instrument.name not in cloned_instruments:
                        instrument = old_processinstance.instrument
                        instrument.pk = None
                        instrument.save()
                        cloned_instruments[instrument.name] = instrument.pk
                        for instrumentinstance in old_instrument.instrumentinstance_set.all():
                            instrumentinstance.pk = None
                            instrumentinstance.instrument = instrument
                            instrumentinstance.save()

                    processinstance.instrument = Instrument.objects.get(pk=cloned_instruments[old_instrument.name])
                    processinstance.save()

    return HttpResponseRedirect(reverse('my-created'))

def templatelist(request):
    context = {
    'lab_template_list': Lab.objects.filter(from_template=True),
    }
    return render(request, 'template_list.html', context=context)

class LabDetailView(LoginRequiredMixin, View):
    template_name = "labmodel/lab_detail.html"

    def get_object(self):
        return get_object_or_404(Lab, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['lab'] = self.get_object()
        kwargs['years'] = range(kwargs['lab'].current_year + 1, kwargs['lab'].current_year + 7)

        if 'labname_form' not in kwargs:
            kwargs['labname_form'] = Labname_form(initial={'name': self.get_object().name})
        if 'LabAssumptionsDropdownForm' not in kwargs:
            kwargs['LabAssumptionsDropdownForm'] = LabAssumptionsDropdownForm(
                initial= {'offset': self.get_object().offset, 
                'integrated_hours': self.get_object().integrated_hours, 
                'walkup_hours': self.get_object().walkup_hours, 
                'current_year': self.get_object().current_year, 
                'max_utilization': self.get_object().max_utilization, 
                'days_per_month': self.get_object().days_per_month})

        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ctxt = {}

        if 'labname_form' in request.POST:
            labnameform = Labname_form(request.POST)

            if labnameform.is_valid():
                lab = self.get_object()
                lab.name = labnameform.cleaned_data['name']
                lab.save()
            else:
                ctxt['labname_form'] = labnameform

        elif 'LabAssumptionsDropdownForm' in request.POST:
            labassumptionsdropdown_form = LabAssumptionsDropdownForm(request.POST)

            if labassumptionsdropdown_form.is_valid():
                lab = self.get_object()
                lab.offset = labassumptionsdropdown_form.cleaned_data['offset']
                lab.integrated_hours = labassumptionsdropdown_form.cleaned_data['integrated_hours']
                lab.walkup_hours = labassumptionsdropdown_form.cleaned_data['walkup_hours']
                lab.current_year = labassumptionsdropdown_form.cleaned_data['current_year']
                lab.max_utilization = labassumptionsdropdown_form.cleaned_data['max_utilization']
                lab.days_per_month = labassumptionsdropdown_form.cleaned_data['days_per_month']
                lab.save()
            else:
                ctxt['labassumptionsdropdown_form'] = labassumptionsdropdown_form

        return render(request, self.template_name, self.get_context_data(**ctxt))

class ProcessInstanceDetailView(FormMixin, generic.DetailView):
    model = ProcessInstance
    form_class = ProcessDropdownForm

    def get_success_url(self):
        return reverse('processinstance-detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        data = super(ProcessInstanceDetailView, self).get_context_data(**kwargs)
        data['ProcessDropdownForm'] = ProcessDropdownForm(initial={'duration': self.object.duration, 'sample_count': self.object.sample_count})
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            processinstance = self.object
            processinstance.duration = form.cleaned_data['duration']
            processinstance.sample_count = form.cleaned_data['sample_count']
            processinstance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class LabAnalysisLabView(FormMixin, generic.DetailView):
    template_name = "labmodel/lab_analysis.html"

    def get_object(self):
        lab=get_object_or_404(Lab, pk=self.kwargs['pk'])
        obj = LabAnalysis.objects.filter(lab=lab).all()
        if len(obj) == 0:
            obj = LabAnalysis(lab=get_object_or_404(Lab, pk=self.kwargs['pk']))
            obj.save()
            return obj
        return obj[0]

    def get_context_data(self, **kwargs):
        kwargs['lab_analysis'] = self.get_object()
        kwargs['years'] = range(kwargs['lab_analysis'].lab.current_year + 1, kwargs['lab_analysis'].lab.current_year + 7)

        if 'failurerate_form' not in kwargs:
            kwargs['LabAnalysisForm'] = LabAnalysisForm()
        
        if 'offset_form' not in kwargs:
            kwargs['OffsetForm'] = LabForm()

        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ctxt = {}

        if 'failurerate_form' in request.POST:
            failurerateform = LabAnalysisForm(request.POST)

            if failurerateform.is_valid():
                lab_analysis = self.get_object()
                lab_anaupperlysis.failure_rate = failurerateform.cleaned_data['failure_rate']
                lab_analysis.save()
            else:
                ctxt['failurerate_form'] = failurerateform
        if 'offset_form' in request.POST:
            offsetform = LabForm(request.POST)

            if offsetform.is_valid():
                lab = self.get_object().lab
                lab.offset = offsetform.cleaned_data['offset']
                lab.save()
            else:
                ctxt['offset_form'] = offsetform

        return render(request, self.template_name, self.get_context_data(**ctxt))
def instrumentutilhours(request, pk):
    obj = LabAnalysis(lab=get_object_or_404(Lab, pk=pk))
    obj.save()

    util_dict_samples = {}
    util_dict_hours = {}
    y = obj.lab.current_year
    years = [y+1, y+2, y+3, y+4, y+5, y+6]
    instrument_set = set()
    for assay in obj.lab.assay_set.all():
        for processinstance in assay.processinstance_set.all():
            for instrumentinstance in processinstance.instrument.instrumentinstance_set.all():
                instrument_set.add(instrumentinstance.instrument)

    for yr in years:
        for instrument in instrument_set:
            byhours = obj.instrument_utilization_hours(instrument, yr)
            if instrument in util_dict_hours:
                util_dict_hours[instrument].append(byhours)
            else:
                util_dict_hours[instrument] = [byhours]
    names = []
    for instrument in instrument_set:
        names.append(instrument.name)

    max_util = obj.lab.max_utilization / 100

    df_hours = pd.DataFrame.from_dict(util_dict_hours, orient='index', columns=years)
    
    
    data_hours = df_hours.values
    
    fig2 = go.Figure(
        data=[go.Heatmap(x=years, xgap=2, y=names, ygap=2, z=data_hours )],
        layout_title_text="Heatmap of Instrument Utilization by Hours (Hover for details)"
    )
    fig2.update_xaxes(side="top")
    fig2['layout'].update(width=900, height=900, autosize=False)
    plot_div_hours = plot(fig2, output_type='div')

    for y in years:
        df_hours[y] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_hours[y]], index = df_hours.index)

    df_htmldiv_hours = df_hours.to_html(classes=["table", "table-hover"])

    context = {
    'years': years,
    'lab_analysis': obj,
    'lab': obj.lab,
    'lab_id': obj.lab.pk,
    'plot_div_hours': plot_div_hours,
    'df_hours': df_htmldiv_hours
    }
    return render(request, 'labmodel/instrumentutilhours.html', context=context)

def instrumentutilsamples(request, pk):
    obj = LabAnalysis(lab=get_object_or_404(Lab, pk=pk))
    obj.save()

    util_dict_samples = {}
    util_dict_hours = {}
    y = obj.lab.current_year
    years = [y+1, y+2, y+3, y+4, y+5, y+6]
    instrument_set = set()
    for assay in obj.lab.assay_set.all():
        for processinstance in assay.processinstance_set.all():
            for instrumentinstance in processinstance.instrument.instrumentinstance_set.all():
                instrument_set.add(instrumentinstance.instrument)

    for yr in years:
        for instrument in instrument_set:
            bysamples = obj.instrument_utilization_samples(instrument, yr)
            byhours = obj.instrument_utilization_hours(instrument, yr)

            if instrument in util_dict_samples:
                util_dict_samples[instrument].append(bysamples)
            else:
                util_dict_samples[instrument] = [bysamples]

            if instrument in util_dict_hours:
                util_dict_hours[instrument].append(byhours)
            else:
                util_dict_hours[instrument] = [byhours]
    names = []
    for instrument in instrument_set:
        names.append(instrument.name)

    max_util = obj.lab.max_utilization / 100

    df_samples = pd.DataFrame.from_dict(util_dict_samples, orient='index', columns=years)
    df_hours = pd.DataFrame.from_dict(util_dict_hours, orient='index', columns=years)
    
    data_samples = df_samples.values
    data_hours = df_hours.values
    
    fig1 = go.Figure(
        data=[go.Heatmap(x=years, xgap=2, y=names, ygap=2, z=data_samples )],
        layout_title_text="Heatmap of Instrument Utilization by Samples (Hover for details)"
    )
    fig1.update_xaxes(side="top")
    fig1['layout'].update(width=900, height=900, autosize=False)
    plot_div_samples = plot(fig1, output_type='div')

    fig2 = go.Figure(
        data=[go.Heatmap(x=years, xgap=2, y=names, ygap=2, z=data_hours )],
        layout_title_text="Heatmap of Instrument Utilization by Hours (Hover for details)"
    )
    fig2.update_xaxes(side="top")
    fig2['layout'].update(width=900, height=900, autosize=False)
    plot_div_hours = plot(fig2, output_type='div')

    for y in years:
        df_samples[y] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_samples[y]], index = df_samples.index)
        df_hours[y] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_hours[y]], index = df_hours.index)

    df_htmldiv_hours = df_hours.to_html(classes=["table", "table-hover"])
    df_htmldiv_samples = df_samples.to_html(classes=["table", "table-hover"])

    context = {
    'years': years,
    'lab_analysis': obj,
    'lab': obj.lab,
    'lab_id': obj.lab.pk,
    'plot_div_samples': plot_div_samples,
    'df_samples': df_htmldiv_samples,
    'plot_div_hours': plot_div_hours,
    'df_hours': df_htmldiv_hours
    }
    return render(request, 'labmodel/instrumentutilsamples.html', context=context)
# Forms ##########################################################
class AssayList(LoginRequiredMixin, ListView):
    model = Assay
    template_name ='labmodel/assay_list.html'
    def get_context_data(self, **kwargs):
        data = super(AssayList, self).get_context_data(**kwargs)
        data['lab_id'] = self.kwargs['pk']
        lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
        data['lab_name'] = lab.name
        return data

    def get_queryset(self):
        return Assay.objects.filter(lab_id=self.kwargs['pk'])


class AssayProcessInstanceCreate(CreateView):
    model = Assay
    fields = ['name', 'lab', 'samples_per_batch', 'projection_for_year_1', 'projection_for_year_2', 'projection_for_year_3', 'projection_for_year_4', 
    'projection_for_year_5', 'projection_for_year_6']

    def get_initial(self):
        lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
        return {
            'lab': lab
        }

    def get_success_url(self):
        return reverse("lab-assay-list", args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        data = super(AssayProcessInstanceCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['processinstances'] = ProcessInstanceFormSet(self.request.POST)
        else:
            data['processinstances'] = ProcessInstanceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        processinstances = context['processinstances']
        with transaction.atomic():
            self.object = form.save()
            if processinstances.is_valid():
                processinstances.instance = self.object
                processinstances.save()
        return super(AssayProcessInstanceCreate, self).form_valid(form)

class LabCreate(CreateView):
    model = Lab
    fields = ['name', 'creator', 'current_year', 'days_per_month', 'offset', 'integrated_hours', 'walkup_hours', 'max_utilization']

    def get_initial(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return {
            'creator': user
        }
    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            return HttpResponseRedirect(self.get_success_url(self.object.pk))

    def get_success_url(self, lab_id):
        return reverse("class-add", args=(lab_id,))

def processinstrumentclassadd(request, pk):
    context = {
    'pk': pk,
    'process_list': Process.objects.all(),
    'instrument_list': Instrument.objects.all()
    }
    return render(request, 'processinstrumentclassadd.html', context=context)

def createnew(request):
    """Has from scratch and from template links"""
    return render(request, 'create_new.html', context={})

class InstrumentAddView(TemplateView):
    template_name = "labmodel/instrument_form.html"

    # Define method to handle GET request
    def get(self, *args, **kwargs):
        # Create an instance of the formset
        formset = InstrumentFormSet(queryset=Instrument.objects.none())
        return self.render_to_response({'instrument_formset': formset})

    def post(self, *args, **kwargs):
        formset = InstrumentFormSet(data=self.request.POST)
        # Check if submitted forms are valid
        if formset.is_valid():
            formset.save()
            return redirect(reverse("class-add", args=(self.kwargs['pk'], )))

        return self.render_to_response({'instrument_formset': formset})

class ProcessCreate(CreateView):
    model = Process
    fields = ['name', ]

    def get_success_url(self):
        return reverse_lazy("class-add", args=(self.kwargs['pk'], ))

class InstrumentInstanceAddView(TemplateView):
    template_name = "labmodel/instrumentinstance_form.html"

    # Define method to handle GET request
    def get(self, *args, **kwargs):
        # Create an instance of the formset
        instrument = get_object_or_404(Instrument, pk=self.kwargs['pk_inst'])
        formset = InstrumentInstanceFormSet(queryset=InstrumentInstance.objects.none(), initial = [{'instrument': instrument}])
        return self.render_to_response({'instrumentinstance_formset': formset})

    def post(self, *args, **kwargs):
        formset = InstrumentInstanceFormSet(data=self.request.POST)
        # Check if submitted forms are valid
        if formset.is_valid():
            formset.save()
            return redirect(reverse("lab-assay-list", args=(self.kwargs['pk_lab'], )))

        return self.render_to_response({'instrumentinstance_formset': formset})

class LabUpdate(UpdateView):
    model = Lab
    fields = '__all__' # Not recommended (potential security issue if more fields added)

def edit_instrument(request, p_id, pk):
    instrument_instance = get_object_or_404(InstrumentInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = EditInstrumentForm(request.POST, initial={'samples_per_day': instrument_instance.samples_per_day})

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            instrument_instance.identical_copies= form.cleaned_data['identical_copies']
            instrument_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('processinstance-detail', args=(p_id, )) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = EditInstrumentForm(initial={'samples_per_day': instrument_instance.samples_per_day})

    context = {
        'form': form,
        'instrument_instance': instrument_instance,
    }

    return render(request, 'labmodel/edit_instrument.html', context)

def add_process(request, lab_id, assay_id):
    assay = get_object_or_404(Assay, pk=assay_id)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        form = AddProcessForm(request.POST, initial={"assay": assay})
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('lab-analysis', args=(lab_id, )) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = AddProcessForm(initial={"assay": assay})

    context = {
        'form': form,
        'assay': assay,
    }

    return render(request, 'labmodel/add_process.html', context)

class LabDelete(DeleteView):
    model = Lab
    success_url = reverse_lazy('my-created')
