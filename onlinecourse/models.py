from django.contrib.auth.models import User
from django.db import models


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateField(auto_now_add=True)
    instructors = models.ManyToManyField(Instructor, blank=True)
    learners = models.ManyToManyField(Learner, blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=512)
    grade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='submissions')
    learner = models.ForeignKey(Learner, on_delete=models.SET_NULL, null=True, blank=True)
    choices = models.ManyToManyField(Choice, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        learner = self.learner or 'Anonymous learner'
        return f'{learner} - {self.course.name} - {self.created_at:%Y-%m-%d %H:%M}'
