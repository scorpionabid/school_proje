from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # Authentication URLs
    path('login/', views.SchoolLoginView.as_view(), name='login'),
    path('logout/', views.SchoolLogoutView.as_view(), name='logout'),
    path('password_change/', views.SchoolPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.SchoolPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Dashboard URL
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Settings URLs
    path('settings/', views.settings_view, name='settings'),
    path('settings/profile/', views.school_profile, name='school_profile'),
    path('settings/school/update/', views.SchoolUpdateView.as_view(), name='school_update'),

    # Məktəb URL-ləri
    path('', views.SchoolListView.as_view(), name='school_list'),
    path('create/', views.SchoolCreateView.as_view(), name='school_create'),
    path('<int:pk>/', views.SchoolDetailView.as_view(), name='school_detail'),
    path('<int:pk>/delete/', views.SchoolDeleteView.as_view(), name='school_delete'),
    
    # Sinif URL-ləri
    path('classroom/', views.ClassRoomListView.as_view(), name='classroom_list'),
    path('classroom/create/', views.ClassRoomCreateView.as_view(), name='classroom_create'),
    path('classroom/<int:pk>/', views.ClassRoomDetailView.as_view(), name='classroom_detail'),
    path('classroom/<int:pk>/update/', views.ClassRoomUpdateView.as_view(), name='classroom_update'),
    path('classroom/<int:pk>/delete/', views.ClassRoomDeleteView.as_view(), name='classroom_delete'),
    path('classroom/<int:pk>/students/', views.ClassStudentsView.as_view(), name='classroom_students'),
    path('classroom/<int:pk>/attendance/', views.ClassAttendanceView.as_view(), name='classroom_attendance'),
    path('classroom/<int:pk>/grades/', views.ClassGradesView.as_view(), name='classroom_grades'),
    
    # Şagird URL-ləri
    path('student/', views.StudentListView.as_view(), name='student_list'),
    path('student/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('student/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('student/<int:pk>/update/', views.StudentUpdateView.as_view(), name='student_update'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    path('student/export/', views.export_students_excel, name='export_students'),
    path('student/import/', views.import_students_excel, name='import_students'),
    
    # İşçi URL-ləri
    path('staff/', views.SchoolStaffListView.as_view(), name='staff_list'),
    path('staff/create/', views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/update/', views.StaffUpdateView.as_view(), name='staff_update'),
    path('staff/<int:pk>/delete/', views.StaffDeleteView.as_view(), name='staff_delete'),
    
    # Davamiyyət URL-ləri
    path('attendance/', views.GeneralAttendanceView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/bulk/', views.AttendanceBulkCreateView.as_view(), name='attendance_bulk_create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/<int:pk>/update/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),
    path('attendance/class/<int:pk>/', views.AttendanceClassDetailView.as_view(), name='attendance_class_detail'),
    
    # Qiymət URL-ləri
    path('grades/ksq/', views.KSQGradeView.as_view(), name='grade_ksq'),
    path('grades/bsq/', views.BSQGradeView.as_view(), name='grade_bsq'),
    path('grades/monitoring/', views.MonitoringGradeView.as_view(), name='grade_monitoring'),
    path('grades/final/', views.FinalGradeView.as_view(), name='grade_final'),
]
