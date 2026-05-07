from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Programme, Teacher, Student, Assignment, Task

# Foydalanuvchi ma'lumotlarini chiroyli formatda qaytarish uchun yordamchi serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# Dasturlar (Yo'nalishlar) uchun serializer
class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = '__all__'

# O'qituvchilar profilini to'liq ko'rsatish uchun serializer
class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    
    class Meta:
        model = Teacher
        fields = '__all__'

# Talabalar profilini ko'rsatish uchun serializer
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'

# Talaba ro'yxatdan o'tayotganda ham User, ham Student profilini birga yaratish uchun
class RegisterStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    programme_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'programme_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        programme_id = validated_data.pop('programme_id')
        
        # 1. Asosiy User'ni yaratamiz va parolni shifrlaymiz
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # 2. Ushbu user uchun Student profilini yaratamiz va yo'nalishni biriktiramiz
        programme = Programme.objects.get(id=programme_id)
        Student.objects.create(user=user, programme=programme)

        return user

# Vazifalar uchun serializer
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        # student va status ni bu yerdan butunlay olib tashlaymiz:
        fields = ['id', 'programme', 'name', 'description', 'deadline', 'created_at'] 
        
        # Yoki shunchaki barchasini olish uchun quyidagicha yozib qo'yishingiz ham mumkin:
        # fields = '__all__'

# Shaxsiy tasklar uchun serializer
class TaskSerializer(serializers.ModelSerializer):
    # Student maydoni avtomatik to'ldirilishi va xavfsizlik uchun read_only qilinadi
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Task
        fields = ['id', 'student', 'name', 'description', 'status', 'created_at']