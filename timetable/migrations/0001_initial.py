# Generated by Django 5.0.6 on 2024-10-27 03:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('section', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=20)),
                ('short_name', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=200)),
                ('credit_hours', models.CharField(max_length=200)),
                ('lab_crh', models.IntegerField(default=0)),
                ('pre_req', models.CharField(blank=True, max_length=200, null=True)),
                ('category', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=12, null=True)),
                ('gmail', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.class')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='timetable.teacher')),
            ],
            options={
                'unique_together': {('course', 'class_assigned')},
            },
        ),
        migrations.AddField(
            model_name='class',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.department'),
        ),
        migrations.AddField(
            model_name='class',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.semester'),
        ),
        migrations.CreateModel(
            name='NewTimeslot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.CharField(max_length=20)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.shift')),
            ],
        ),
        migrations.AddField(
            model_name='class',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.shift'),
        ),
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.CharField(max_length=20)),
                ('category', models.CharField(blank=True, max_length=20, null=True)),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.shift')),
            ],
        ),
        migrations.CreateModel(
            name='CourseOffering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.department')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.semester')),
            ],
            options={
                'unique_together': {('course', 'department', 'semester', 'year')},
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.courseassignment')),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.day')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.room')),
                ('timeslot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.timeslot')),
            ],
            options={
                'unique_together': {('day', 'room', 'timeslot')},
            },
        ),
    ]
