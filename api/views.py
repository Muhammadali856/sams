from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Programme, Assignment, Task, Student, Teacher
from .serializers import AssignmentSerializer, TaskSerializer
from .serializers import StudentSerializer, RegisterStudentSerializer, ProgrammeSerializer

class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Agar so'rov turi xavfsiz (ya'ni faqat o'qish - GET, HEAD, OPTIONS) bo'lsa, ruxsat!
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Aks holda (yozish, o'zgartirish, o'chirish bo'lsa), faqat o'qituvchilarga ruxsat!
        # hasattr() funksiyasi User modelida 'teacher' profili bor yoki yo'qligini tekshiradi.
        return hasattr(request.user, 'teacher')

# 1. Talabalar uchun ro'yxatdan o'tish (Sign Up) API'si
class StudentSignUpView(generics.CreateAPIView):
    serializer_class = RegisterStudentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student muvaffaqiyatli ro'yxatdan o'tdi!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Assignment (Vazifalar) uchun CRUD API
class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    # Ham tizimga kirgan bo'lishi shart, ham bizning maxsus ruxsatnomadan o'tishi shart
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'teacher'):
            return Assignment.objects.all()
            
        elif hasattr(user, 'student_profile'):
            # Use __in to fetch assignments from ALL enrolled programmes
            return Assignment.objects.filter(programme__in=user.student_profile.programmes.all())
            
        return Assignment.objects.none()

# 3. Task (Shaxsiy topshiriqlar) uchun CRUD API
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # To'g'ridan-to'g'ri tizimga kirgan User ni beramiz
        return Task.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        # Yaratishda ham faqat User ning o'zini saqlaymiz
        serializer.save(student=self.request.user)

class ProgrammeViewSet(viewsets.ModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAuthenticated]

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]