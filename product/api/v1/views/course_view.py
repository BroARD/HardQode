from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Group
from users.models import Subscription, Balance


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_queryset(self):
        queryset = super(CourseViewSet, self).get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    #Реализовать API оплаты продукты за бонусы.
    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        course = Course.objects.get(id=pk)
        Balance.objects.get_or_create(user=self.request.user)
        money = Balance.objects.get(user=self.request.user)
        #По факту оплаты и списания бонусов с баланса пользователя должен быть открыт доступ к курсу.
        if course.price <= money.balance:
            Subscription.objects.create(user=self.request.user, product=course)
            money.balance -= 200
            money.save()

        return Response(
            status=status.HTTP_201_CREATED
        )

    #Реализовать API на список продуктов, доступных для покупки
    @action(detail=False, methods=['GET'])
    def can_buy(self, request):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        courses = Course.objects.exclude(id__in=subscriptions.values('product_id'))
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)