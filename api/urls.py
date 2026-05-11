from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, TaskViewSet, StudentSignUpView, ProgrammeViewSet, StudentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'programmes', ProgrammeViewSet, basename='programme')
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
    
    path('auth/signup/', StudentSignUpView.as_view(), name='student-signup'),

    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]