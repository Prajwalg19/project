from .serializers import DepartmentSerializer, LabSerializer, PurchaseOrderSerializer, EquipmentSerializer, EquipmentIssueSerializer, EquipmentReviewSerializer, InvoiceSerializer
from rest_framework import viewsets
from .models import Department, Lab, PurchaseOrder, Equipment, EquipmentIssue, EquipmentReview, Invoice
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from lab.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from lab.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.db import models
@authentication_classes([JWTAuthentication])
class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()

class LabViewSet(viewsets.ModelViewSet):
    serializer_class = LabSerializer
    queryset = Lab.objects.all()

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()

class EquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()

class EquipmentIssueViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentIssueSerializer
    queryset = EquipmentIssue.objects.all()

class EquipmentReviewViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentReviewSerializer
    queryset = EquipmentReview.objects.all()

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    @authentication_classes([AllowAny])
    @permission_classes([AllowAny])
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            role = user.role
            token = get_tokens_for_user(user)
            return Response({'token': token, 'role': role, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset link sent. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def search(request):
    query = request.GET.get('query', '')

    # Define a list of models you want to search across
    models_to_search = [
        Department,
        Lab,
        Equipment,
        PurchaseOrder,
        Invoice,
        EquipmentIssue,
        EquipmentReview,
    ]

    # Create a dictionary to store search results for each model
    search_results = {}

    for model in models_to_search:
        # Get the serializer for the current model
        if model == Department:
            serializer_class = DepartmentSerializer
        elif model == Lab:
            serializer_class = LabSerializer
        elif model == Equipment:
            serializer_class = EquipmentSerializer
        elif model == PurchaseOrder:
            serializer_class = PurchaseOrderSerializer
        elif model == Invoice:
            serializer_class = InvoiceSerializer
        elif model == EquipmentIssue:
            serializer_class = EquipmentIssueSerializer
        elif model == EquipmentReview:
            serializer_class = EquipmentReviewSerializer
        # Add more elif statements for other models if needed

        # Create a Q object to search across all text fields of the model
        q_objects = Q()
        for field in model._meta.get_fields():
            if isinstance(field, (models.CharField, models.TextField)):
                q_objects |= Q(**{f"{field.name}__icontains": query})

        # Query the model using the Q object
        results = model.objects.filter(q_objects)

        # Serialize the results using the corresponding serializer
        serializer = serializer_class(results, many=True)
        model_data = serializer.data

        # Store the results in the search_results dictionary
        search_results[model._meta.model_name.lower()] = model_data

    return Response(search_results)
