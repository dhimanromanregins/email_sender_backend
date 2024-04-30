from django.urls import path
from .views import SendEmailList, ProductList,ProductDetail,ProfileDetailAPIView,GroupEmailsList,GroupEmailsDetail,ProfileAPIView,EmailDetailView,GroupEmailsListAPIView,EmailsDetail,EmailListView,EmailsList,EmailCountByGroup,SendBulkEmail,SendEmailGroup,UserLoginAPIView, UserRegisterAPIView

urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('register/', UserRegisterAPIView.as_view(), name='user_register'),
    path('send-email/', SendEmailList.as_view(), name='send-email-list'),
    path('send-email/', SendEmailList.as_view(), name='send_email'),
    path('send-bulk-email/', SendBulkEmail.as_view(), name='send_bulk_email'),
    path('send-group-email/', SendEmailGroup.as_view(), name='send_group_email'),
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('email-count/', EmailCountByGroup.as_view(), name='email-count-by-group'),
    path('emails/', EmailsList.as_view(), name='emails-list'),
    path('emails/<int:pk>/', EmailsDetail.as_view(), name='emails-detail'),
    path('emailgroup/', EmailListView.as_view(), name='email-list'),
    path('emailgroup/<int:pk>/', EmailDetailView.as_view(), name='email-detail'),
    path('group-emails/', GroupEmailsListAPIView.as_view(), name='group-emails-list'),
    path('profiles/', ProfileAPIView.as_view(), name='profile-list'),
    path('profiles/<int:user_id>/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    path('addgroups/', GroupEmailsList.as_view(), name='group-list'),
    path('addgroups/<int:pk>/', GroupEmailsDetail.as_view(), name='group-detail'),
]
