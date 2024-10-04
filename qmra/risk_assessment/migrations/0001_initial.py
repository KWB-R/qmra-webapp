# Generated by Django 5.0.6 on 2024-10-04 06:17

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskAssessment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('name', models.CharField(blank=True, default='', max_length=64)),
                ('description', models.TextField(blank=True, default='', max_length=500)),
                ('source_name', models.CharField(blank=True, choices=[('', '---------'), ('groundwater', [('groundwater', 'groundwater')]), ('rainwater', [('rainwater, rooftop harvesting', 'rainwater, rooftop harvesting'), ('rainwater, stormwater harvesting', 'rainwater, stormwater harvesting')]), ('sewage', [('sewage, raw', 'sewage, raw'), ('sewage, treated', 'sewage, treated')]), ('surface water', [('surface water, contaminated', 'surface water, contaminated'), ('surface water, general', 'surface water, general'), ('surface water, protected', 'surface water, protected')]), ('other', 'other')], max_length=256)),
                ('exposure_name', models.CharField(blank=True, choices=[('', '---------'), ('domestic use', [('domestic use, car washing', 'domestic use, car washing'), ('domestic use, toilet flushing', 'domestic use, toilet flushing'), ('domestic use, washing machine', 'domestic use, washing machine')]), ('drinking water', [('drinking water', 'drinking water')]), ('irrigation', [('irrigation, garden', 'irrigation, garden'), ('irrigation, public', 'irrigation, public'), ('irrigation, restricted', 'irrigation, restricted'), ('irrigation, unrestricted', 'irrigation, unrestricted')]), ('other', 'other')], max_length=256)),
                ('events_per_year', models.IntegerField()),
                ('volume_per_event', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_assessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inflow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pathogen', models.CharField(choices=[('', '---------'), ('Bacteria', [('Bacillus anthracis', 'Bacillus anthracis'), ('Burkholderia pseudomallei', 'Burkholderia pseudomallei'), ('Campylobacter jejuni', 'Campylobacter jejuni'), ('Coxiella burnetii', 'Coxiella burnetii'), ('Escherichia coli enterohemorrhagic (EHEC)', 'Escherichia coli enterohemorrhagic (EHEC)'), ('Escherichia coli', 'Escherichia coli'), ('Francisella tularensis', 'Francisella tularensis'), ('Legionella pneumophila', 'Legionella pneumophila'), ('Listeria monocytogenes (Death as response)', 'Listeria monocytogenes (Death as response)'), ('Listeria monocytogenes (Infection)', 'Listeria monocytogenes (Infection)'), ('Listeria monocytogenes (Stillbirths)', 'Listeria monocytogenes (Stillbirths)'), ('Mycobacterium avium', 'Mycobacterium avium'), ('Pseudomonas aeruginosa (Contact lens)', 'Pseudomonas aeruginosa (Contact lens)'), ('Pseudomonas aeruginosa (bacterimia)', 'Pseudomonas aeruginosa (bacterimia)'), ('Rickettsia rickettsi', 'Rickettsia rickettsi'), ('Salmonella Typhi', 'Salmonella Typhi'), ('Salmonella anatum', 'Salmonella anatum'), ('Salmonella meleagridis', 'Salmonella meleagridis'), ('Salmonella nontyphoid', 'Salmonella nontyphoid'), ('Salmonella serotype newport', 'Salmonella serotype newport'), ('Shigella', 'Shigella'), ('Staphylococcus aureus', 'Staphylococcus aureus'), ('Vibrio cholerae', 'Vibrio cholerae'), ('Yersinia pestis', 'Yersinia pestis')]), ('Viruses', [('Adenovirus', 'Adenovirus'), ('Echovirus', 'Echovirus'), ('Enteroviruses', 'Enteroviruses'), ('Influenza', 'Influenza'), ('Lassa virus', 'Lassa virus'), ('Poliovirus', 'Poliovirus'), ('Rhinovirus', 'Rhinovirus'), ('Rotavirus', 'Rotavirus'), ('SARS', 'SARS')]), ('Protozoa', [('Cryptosporidium parvum', 'Cryptosporidium parvum'), ('Endamoeba coli', 'Endamoeba coli'), ('Giardia duodenalis', 'Giardia duodenalis'), ('Naegleria fowleri', 'Naegleria fowleri')])], max_length=256)),
                ('min', models.FloatField()),
                ('max', models.FloatField()),
                ('risk_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inflows', to='risk_assessment.riskassessment')),
            ],
        ),
        migrations.CreateModel(
            name='RiskAssessmentResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pathogen', models.CharField(choices=[('', '---------'), ('Bacteria', [('Bacillus anthracis', 'Bacillus anthracis'), ('Burkholderia pseudomallei', 'Burkholderia pseudomallei'), ('Campylobacter jejuni', 'Campylobacter jejuni'), ('Coxiella burnetii', 'Coxiella burnetii'), ('Escherichia coli enterohemorrhagic (EHEC)', 'Escherichia coli enterohemorrhagic (EHEC)'), ('Escherichia coli', 'Escherichia coli'), ('Francisella tularensis', 'Francisella tularensis'), ('Legionella pneumophila', 'Legionella pneumophila'), ('Listeria monocytogenes (Death as response)', 'Listeria monocytogenes (Death as response)'), ('Listeria monocytogenes (Infection)', 'Listeria monocytogenes (Infection)'), ('Listeria monocytogenes (Stillbirths)', 'Listeria monocytogenes (Stillbirths)'), ('Mycobacterium avium', 'Mycobacterium avium'), ('Pseudomonas aeruginosa (Contact lens)', 'Pseudomonas aeruginosa (Contact lens)'), ('Pseudomonas aeruginosa (bacterimia)', 'Pseudomonas aeruginosa (bacterimia)'), ('Rickettsia rickettsi', 'Rickettsia rickettsi'), ('Salmonella Typhi', 'Salmonella Typhi'), ('Salmonella anatum', 'Salmonella anatum'), ('Salmonella meleagridis', 'Salmonella meleagridis'), ('Salmonella nontyphoid', 'Salmonella nontyphoid'), ('Salmonella serotype newport', 'Salmonella serotype newport'), ('Shigella', 'Shigella'), ('Staphylococcus aureus', 'Staphylococcus aureus'), ('Vibrio cholerae', 'Vibrio cholerae'), ('Yersinia pestis', 'Yersinia pestis')]), ('Viruses', [('Adenovirus', 'Adenovirus'), ('Echovirus', 'Echovirus'), ('Enteroviruses', 'Enteroviruses'), ('Influenza', 'Influenza'), ('Lassa virus', 'Lassa virus'), ('Poliovirus', 'Poliovirus'), ('Rhinovirus', 'Rhinovirus'), ('Rotavirus', 'Rotavirus'), ('SARS', 'SARS')]), ('Protozoa', [('Cryptosporidium parvum', 'Cryptosporidium parvum'), ('Endamoeba coli', 'Endamoeba coli'), ('Giardia duodenalis', 'Giardia duodenalis'), ('Naegleria fowleri', 'Naegleria fowleri')])], max_length=256)),
                ('infection_risk', models.BooleanField()),
                ('dalys_risk', models.BooleanField()),
                ('infection_minimum_lrv_min', models.FloatField()),
                ('infection_minimum_lrv_max', models.FloatField()),
                ('infection_minimum_lrv_q1', models.FloatField()),
                ('infection_minimum_lrv_q3', models.FloatField()),
                ('infection_minimum_lrv_median', models.FloatField()),
                ('infection_maximum_lrv_min', models.FloatField()),
                ('infection_maximum_lrv_max', models.FloatField()),
                ('infection_maximum_lrv_q1', models.FloatField()),
                ('infection_maximum_lrv_q3', models.FloatField()),
                ('infection_maximum_lrv_median', models.FloatField()),
                ('dalys_minimum_lrv_min', models.FloatField()),
                ('dalys_minimum_lrv_max', models.FloatField()),
                ('dalys_minimum_lrv_q1', models.FloatField()),
                ('dalys_minimum_lrv_q3', models.FloatField()),
                ('dalys_minimum_lrv_median', models.FloatField()),
                ('dalys_maximum_lrv_min', models.FloatField()),
                ('dalys_maximum_lrv_max', models.FloatField()),
                ('dalys_maximum_lrv_q1', models.FloatField()),
                ('dalys_maximum_lrv_q3', models.FloatField()),
                ('dalys_maximum_lrv_median', models.FloatField()),
                ('risk_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='risk_assessment.riskassessment')),
            ],
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('Bank filtration', 'Bank filtration'), ('Chlorination, drinking water', 'Chlorination, drinking water'), ('Chlorination, wastewater', 'Chlorination, wastewater'), ('Chlorine dioxide', 'Chlorine dioxide'), ('Conventional clarification', 'Conventional clarification'), ('Dissolved air flotation', 'Dissolved air flotation'), ('Dual media filtration', 'Dual media filtration'), ('Granular high-rate filtration', 'Granular high-rate filtration'), ('High-rate clarification', 'High-rate clarification'), ('Lime softening', 'Lime softening'), ('Membrane filtration', 'Membrane filtration'), ('Microfiltration', 'Microfiltration'), ('Nanofiltration', 'Nanofiltration'), ('Ozonation, drinking water', 'Ozonation, drinking water'), ('Ozonation, wastewater', 'Ozonation, wastewater'), ('Precoat filtration', 'Precoat filtration'), ('Primary treatment', 'Primary treatment'), ('Reverse osmosis', 'Reverse osmosis'), ('Roughing filters', 'Roughing filters'), ('Secondary treatment', 'Secondary treatment'), ('Slow sand filtration', 'Slow sand filtration'), ('Storage reservoirs', 'Storage reservoirs'), ('UV disinfection 20 mJ/cm2, drinking', 'UV disinfection 20 mJ/cm2, drinking'), ('UV disinfection 40 mJ/cm2, drinking', 'UV disinfection 40 mJ/cm2, drinking'), ('UV disinfection, wastewater', 'UV disinfection, wastewater'), ('Ultrafiltration', 'Ultrafiltration'), ('Wetlands, subsurface flow', 'Wetlands, subsurface flow'), ('Wetlands, surface flow', 'Wetlands, surface flow')], max_length=64)),
                ('bacteria_min', models.FloatField(blank=True, null=True)),
                ('bacteria_max', models.FloatField(blank=True, null=True)),
                ('viruses_min', models.FloatField(blank=True, null=True)),
                ('viruses_max', models.FloatField(blank=True, null=True)),
                ('protozoa_min', models.FloatField(blank=True, null=True)),
                ('protozoa_max', models.FloatField(blank=True, null=True)),
                ('risk_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatments', to='risk_assessment.riskassessment')),
            ],
        ),
    ]