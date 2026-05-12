from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Programme, Teacher, Student, Assignment, Task, Quiz

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
    
    # This magic line grabs the 'name' of EVERY programme the student is in
    programme_names = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
        source='programmes'
    )
    
    class Meta:
        model = Student
        # We use 'programmes' (plural) to match the new model field name
        fields = ['id', 'user', 'programmes', 'programme_names', 'is_active']

# Talaba ro'yxatdan o'tayotganda ham User, ham Student profilini birga yaratish uchun
class RegisterStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Changed to ListField to accept an array like [1, 2, 4]
    programme_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    student_id = serializers.CharField(source='username') 

    class Meta:
        model = User
        fields = ['student_id', 'password', 'first_name', 'last_name', 'email', 'programme_ids']

    # This built-in method automatically validates the programme_ids array
    def validate_programme_ids(self, value):
        if len(value) > 6:
            raise serializers.ValidationError("A student can only choose up to 6 programmes.")
        if len(value) == 0:
            raise serializers.ValidationError("A student must choose at least 1 programme.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        programme_ids = validated_data.pop('programme_ids')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create the student profile first
        student = Student.objects.create(user=user)
        
        # Fetch the selected programmes from the database and link them to the student
        programmes = Programme.objects.filter(id__in=programme_ids)
        student.programmes.set(programmes)

        return user
# Vazifalar uchun serializer
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        # student va status ni bu yerdan butunlay olib tashlaymiz:
        fields = ['id', 'programme', 'name', 'description', 'deadline', 'created_at'] 

# Shaxsiy tasklar uchun serializer
class TaskSerializer(serializers.ModelSerializer):
    # Student maydoni avtomatik to'ldirilishi va xavfsizlik uchun read_only qilinadi
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Task
        fields = ['id', 'student', 'name', 'description', 'status', 'created_at']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'programme', 'name', 'description', 'deadline', 'created_at']