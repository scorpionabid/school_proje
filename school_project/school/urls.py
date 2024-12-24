from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # Auth URLs
    path('login/', views.SchoolLoginView.as_view(), name='login'),
    path('logout/', views.SchoolLogoutView.as_view(), name='logout'),
    path('password_change/', views.SchoolPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.SchoolPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Dashboard
    path('dashboard/', views.school_dashboard, name='dashboard'),

    # Settings
    path('settings/', views.school_settings, name='settings'),
    path('settings/profile/', views.school_profile, name='settings_profile'),
    path('settings/staff/', views.SettingsStaffListView.as_view(), name='settings_staff_list'),
    path('settings/staff/add/', views.SettingsStaffCreateView.as_view(), name='settings_staff_add'),
    path('settings/staff/<int:pk>/edit/', views.SettingsStaffUpdateView.as_view(), name='settings_staff_edit'),
    path('settings/staff/<int:pk>/delete/', views.SettingsStaffDeleteView.as_view(), name='settings_staff_delete'),

    # School URLs
    path('', views.SchoolListView.as_view(), name='school_list'),
    path('create/', views.SchoolCreateView.as_view(), name='school_create'),
    path('<int:pk>/', views.SchoolDetailView.as_view(), name='school_detail'),
    path('<int:pk>/edit/', views.SchoolUpdateView.as_view(), name='school_edit'),
    path('<int:pk>/delete/', views.SchoolDeleteView.as_view(), name='school_delete'),

    # Staff URLs
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', views.StaffCreateView.as_view(), name='staff_add'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/edit/', views.StaffUpdateView.as_view(), name='staff_edit'),
    path('staff/<int:pk>/delete/', views.StaffDeleteView.as_view(), name='staff_delete'),

    # Class URLs
    path('class/', views.ClassRoomListView.as_view(), name='classroom_list'),
    path('class/add/', views.ClassRoomCreateView.as_view(), name='classroom_add'),
    path('class/<int:pk>/', views.ClassRoomDetailView.as_view(), name='classroom_detail'),
    path('class/<int:pk>/edit/', views.ClassRoomUpdateView.as_view(), name='classroom_edit'),
    path('class/<int:pk>/delete/', views.ClassRoomDeleteView.as_view(), name='classroom_delete'),
    path('class/<int:pk>/students/', views.ClassStudentsView.as_view(), name='class_students'),

    # Student URLs
    path('student/', views.StudentListView.as_view(), name='student_list'),
    path('student/add/', views.StudentCreateView.as_view(), name='student_add'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('student/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),

    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/bulk/', views.AttendanceBulkCreateView.as_view(), name='attendance_bulk_create'),

    # Grade URLs
    path('grade/ksq/', views.GradeKSQView.as_view(), name='grade_ksq'),
    path('grade/bsq/', views.GradeBSQView.as_view(), name='grade_bsq'),
    path('grade/monitoring/', views.GradeMonitoringView.as_view(), name='grade_monitoring'),
    path('grade/final/', views.GradeFinalView.as_view(), name='grade_final'),
]
