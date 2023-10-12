from .serializers import ConsumableSerializer, DepartmentSerializer, LabSerializer, PurchaseOrderSerializer, EquipmentSerializer, EquipmentIssueSerializer, EquipmentReviewSerializer, InvoiceSerializer
from rest_framework import viewsets
from .models import Department,Consumable, ConsumableStock , Lab, PurchaseOrder, Equipment, EquipmentIssue, EquipmentReview, Invoice
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from lab.serializers import SendPasswordResetEmailSerializer,ConsumableStockSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from lab.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.db.models import ForeignKey, ManyToManyField
from django.db import models

@authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
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


    
from django.db.models import ForeignKey, ManyToManyField
from django.db.models import Q


from django.db.models import Q
from .serializers import DepartmentSerializer, LabSerializer, PurchaseOrderSerializer, EquipmentSerializer, EquipmentIssueSerializer, EquipmentReviewSerializer, InvoiceSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db.models import Q
from .serializers import DepartmentSerializer, LabSerializer, PurchaseOrderSerializer, EquipmentSerializer, EquipmentIssueSerializer, EquipmentReviewSerializer, InvoiceSerializer, ConsumableSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def search(request):
    query = request.GET.get('query', '')

    # Create a list to store related data
    related_data = []

    # Query departments based on department_name
    departments = Department.objects.filter(Q(department_name__icontains=query) | Q(hod_name__icontains=query))
    for department in departments:
        department_data = DepartmentSerializer(department).data
        labs = Lab.objects.filter(department_number=department)
        lab_data = LabSerializer(labs, many=True).data
        equipment = Equipment.objects.filter(lab_number__in=labs)
        equipment_data = EquipmentSerializer(equipment, many=True).data
        purchase_orders = PurchaseOrder.objects.filter(originator=department)
        purchase_order_data = PurchaseOrderSerializer(purchase_orders, many=True).data
        invoices = Invoice.objects.filter(purchase_order_no__in=purchase_orders)
        invoice_data = InvoiceSerializer(invoices, many=True).data
        equipment_issues = EquipmentIssue.objects.filter(lab_incharge__in=labs)
        equipment_issue_data = EquipmentIssueSerializer(equipment_issues, many=True).data
        equipment_reviews = EquipmentReview.objects.filter(equipment__in=equipment)
        equipment_review_data = EquipmentReviewSerializer(equipment_reviews, many=True).data

        related_data.append({
            'department': department_data,
            'labs': lab_data,
            'equipment': equipment_data,
            'purchase_orders': purchase_order_data,
            'invoices': invoice_data,
            'equipment_issues': equipment_issue_data,
            'equipment_reviews': equipment_review_data,
        })

    # Query labs
    labs = Lab.objects.filter(Q(lab_name__icontains=query) | Q(lab_incharge__icontains=query))
    for lab in labs:
        lab_data = LabSerializer(lab).data
        department = lab.department_number  # Assuming lab has a foreign key to department
        department_data = DepartmentSerializer(department).data
        equipment = Equipment.objects.filter(lab_number=lab)
        equipment_data = EquipmentSerializer(equipment, many=True).data
        purchase_orders = PurchaseOrder.objects.filter(originator=department)
        purchase_order_data = PurchaseOrderSerializer(purchase_orders, many=True).data
        invoices = Invoice.objects.filter(purchase_order_no__in=purchase_orders)
        invoice_data = InvoiceSerializer(invoices, many=True).data
        equipment_issues = EquipmentIssue.objects.filter(lab_incharge=lab)
        equipment_issue_data = EquipmentIssueSerializer(equipment_issues, many=True).data
        equipment_reviews = EquipmentReview.objects.filter(equipment__in=equipment)
        equipment_review_data = EquipmentReviewSerializer(equipment_reviews, many=True).data

        related_data.append({
            'department': department_data,
            'labs': lab_data,
            'equipment': equipment_data,
            'purchase_orders': purchase_order_data,
            'invoices': invoice_data,
            'equipment_issues': equipment_issue_data,
            'equipment_reviews': equipment_review_data,
        })

    # Query purchase_orders
    purchase_orders = PurchaseOrder.objects.filter(purchase_order_number__icontains=query)
    for purchase_order in purchase_orders:
        purchase_order_data = PurchaseOrderSerializer(purchase_order).data
        invoices = Invoice.objects.filter(purchase_order_no__in=purchase_orders)
        invoice_data = InvoiceSerializer(invoices, many=True).data

        related_data.append({
            'purchase_orders': purchase_order_data,
            'invoices': invoice_data,
        })

    # Query equipment
    equipment = Equipment.objects.filter(equipment_serial_number__icontains=query)
    for equip in equipment:
        equipment_data = EquipmentSerializer(equip).data
        lab = equip.lab_number  # Assuming equipment has a foreign key to lab
        lab_data = LabSerializer(lab).data
        purchase_orders = PurchaseOrder.objects.filter(originator=lab.department_number)
        purchase_order_data = PurchaseOrderSerializer(purchase_orders, many=True).data
        invoices = Invoice.objects.filter(purchase_order_no__in=purchase_orders)
        invoice_data = InvoiceSerializer(invoices, many=True).data

        related_data.append({
            'labs': lab_data,
            'equipment': equipment_data,
            'purchase_orders': purchase_order_data,
            'invoices': invoice_data,
        })

    # Query invoices
    invoices = Invoice.objects.filter(invoice_number__icontains=query)
    for invoice in invoices:
        invoice_data = InvoiceSerializer(invoice).data
        purchase_order = invoice.purchase_order_no
        purchase_order_data = PurchaseOrderSerializer(purchase_order).data
        department = purchase_order.originator
        department_data = DepartmentSerializer(department).data

        related_data.append({
            'department': department_data,
            'purchase_orders': purchase_order_data,
            'invoices': invoice_data,
        })

    return Response(related_data)
