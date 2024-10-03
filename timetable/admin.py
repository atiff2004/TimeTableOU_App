from django.contrib import admin
from .models import Room, Timeslot,CourseOffering, Shift,Day, Course, Class, Schedule, Teacher, CourseAssignment, Department, Semester


admin.site.register(Department)
admin.site.register(Shift)
admin.site.register(Semester)
admin.site.register(Class)
admin.site.register(Course)
admin.site.register(CourseAssignment)
admin.site.register(CourseOffering)
admin.site.register(Teacher)
admin.site.register(Day)
admin.site.register(Room)
admin.site.register(Timeslot)
admin.site.register(Schedule)
