# from rest_framework import status, generics
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.db.models import Prefetch

# from .models import Block
# from .serializers import (
#     BlockSerializer, 
#     BlockedUserSerializer, 
#     BlockRequestSerializer,
#     BlockUserSerializer,
#     UnblockUserSerializer,
#     ToggleBlockSerializer,
#     CheckBlockSerializer
# )

# User = get_user_model()


# class BlockViewSet(GenericViewSet, 
#                     ListModelMixin, 
#                     CreateModelMixin, 
#                     DestroyModelMixin):
#     """
#     ViewSet for managing user blocks
#     """
#     permission_classes = [IsAuthenticated]
#     http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
#     def get_serializer_class(self):
#         if self.action == 'blocked_list':
#             return BlockedUserSerializer
#         return BlockSerializer
    
#     def get_queryset(self):
#         return Block.objects.filter(blocker=self.request.user)
    
#     @action(detail=False, methods=['get'], url_path='blocked-list')
#     def blocked_list(self, request):
#         """
#         Get list of users blocked by current user
#         """
#         blocked_users = User.objects.filter(
#             blocked_by_set__blocker=request.user
#         ).prefetch_related(
#             Prefetch(
#                 'blocked_by_set',
#                 queryset=Block.objects.filter(blocker=request.user),
#                 to_attr='blocked_info'
#             )
#         ).order_by('-blocked_by_set__created_at')
        
#         page = self.paginate_queryset(blocked_users)
#         if page is not None:
#             serializer = BlockedUserSerializer(
#                 page, many=True, context={'request': request}
#             )
#             return self.get_paginated_response(serializer.data)
        
#         serializer = BlockedUserSerializer(
#             blocked_users, many=True, context={'request': request}
#         )
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['post'], url_path='block', serializer_class=BlockUserSerializer)
#     def block_user(self, request):
#         """
#         Block a user
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
#         reason = serializer.validated_data.get('reason', '')
        
#         try:
#             user_to_block = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'not found user'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         if user_to_block == request.user:
#             return Response(
#                 {'error': 'خود در گیری داری؟؟'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         exists = Block.objects.filter(
#             blocker=request.user,
#             blocked=user_to_block
#         ).exists()
        
#         if exists:
#             return Response(
#                 {'status': 'already has been blocked', 'message': 'this user had in block list in past'},
#                 status=status.HTTP_200_OK
#             )
        
#         block = Block.objects.create(
#             blocker=request.user,
#             blocked=user_to_block,
#             reason=reason
#         )
        
#         return Response(
#             {
#                 'status': 'blocked',
#                 'message': f'{user_to_block.username}',
#                 'blocked_user': {
#                     'id': user_to_block.id,
#                     'username': user_to_block.username,
#                     'phone': user_to_block.phone
#                 }
#             },
#             status=status.HTTP_201_CREATED
#         )
    
#     @action(detail=False, methods=['post'], url_path='unblock', serializer_class=UnblockUserSerializer)
#     def unblock_user(self, request):
#         """
#         Unblock a user
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
        
#         try:
#             user_to_unblock = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'user not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         deleted, _ = Block.objects.filter(
#             blocker=request.user,
#             blocked=user_to_unblock
#         ).delete()
        
#         if deleted:
#             return Response(
#                 {
#                     'status': 'unblocked',
#                     'message': f'user {user_to_unblock.username} has been unblocked'
#                 },
#                 status=status.HTTP_200_OK
#             )
        
#         return Response(
#             {'status': 'not_blocked', 'message': 'this user was not blocked'},
#             status=status.HTTP_200_OK
#         )
    
#     # @action(detail=False, methods=['post'], url_path='toggle-block', serializer_class=ToggleBlockSerializer)
#     # def toggle_block(self, request):
#     #     """
#     #     Toggle block status for a user (block if not blocked, unblock if blocked)
#     #     """
#     #     serializer = self.get_serializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
        
#     #     user_id = serializer.validated_data['user_id']
#     #     reason = serializer.validated_data.get('reason', '')
        
#     #     try:
#     #         user = User.objects.get(id=user_id)
#     #     except User.DoesNotExist:
#     #         return Response(
#     #             {'error': 'user not found error'},
#     #             status=status.HTTP_404_NOT_FOUND
#     #         )
        
#     #     if user == request.user:
#     #         return Response(
#     #             {'error': 'خود درگیری داری ؟؟'},
#     #             status=status.HTTP_400_BAD_REQUEST
#     #         )
        
#     #     blocked, created = Block.objects.get_or_create(
#     #         blocker=request.user,
#     #         blocked=user,
#     #         defaults={'reason': reason} # dict show create time not resive time 
#     #     )
        
#     #     if not created:
#     #         blocked.delete()
#     #         return Response(
#     #             {'status': 'unblocked', 'action': 'unblock'},
#     #             status=status.HTTP_200_OK
#     #         )
        
#     #     return Response(
#     #         {'status': 'blocked', 'action': 'block'},
#     #         status=status.HTTP_201_CREATED
#     #     )





























# # بخش toggle_block در views.py رو اینطور اصلاح کن:

# @action(detail=False, methods=['post'], url_path='toggle-block', serializer_class=ToggleBlockSerializer)
# def toggle_block(self, request):
#     """
#     Toggle block status for a user (block if not blocked, unblock if blocked)
#     """
#     serializer = self.get_serializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
    
#     user_id = serializer.validated_data['user_id']
#     reason = serializer.validated_data.get('reason', '')
    
#     # UUID به صورت رشته است
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response(
#             {'error': 'user not found error', 'success': False},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     if user == request.user:
#         return Response(
#             {'error': 'نمیتوانید خودتان را بلاک کنید', 'success': False},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     blocked, created = Block.objects.get_or_create(
#         blocker=request.user,
#         blocked=user,
#         defaults={'reason': reason}
#     )
    
#     if not created:
#         blocked.delete()
#         return Response(
#             {'success': True, 'action': 'unblocked', 'message': f'کاربر {user.username} آنبلاک شد'},
#             status=status.HTTP_200_OK
#         )
    
#     return Response(
#         {'success': True, 'action': 'blocked', 'message': f'کاربر {user.username} بلاک شد'},
#         status=status.HTTP_201_CREATED
#     )


# # @action(detail=False, methods=['get'], url_path='check-block', serializer_class=CheckBlockSerializer)
# # def check_block(self, request):
# #     """
# #     Check block status between current user and another user
# #     """
# #     serializer = self.get_serializer(data=request.query_params)
# #     serializer.is_valid(raise_exception=True)
    
# #     user_id = serializer.validated_data['user_id']
    
# #     try:
# #         user = User.objects.get(id=user_id)
# #     except User.DoesNotExist:
# #         return Response(
# #             {'error': 'user not found', 'success': False},
# #             status=status.HTTP_404_NOT_FOUND
# #         )
    
# #     is_blocked = Block.objects.filter(
# #         blocker=request.user,
# #         blocked=user
# #     ).exists()
    
# #     is_blocked_by = Block.objects.filter(
# #         blocker=user,
# #         blocked=request.user
# #     ).exists()
    
# #     return Response({
# #         'success': True,
# #         'user_id': str(user.id),
# #         'username': user.username,
# #         'is_blocked': is_blocked,
# #         'is_blocked_by': is_blocked_by,
# #         'can_interact': not is_blocked and not is_blocked_by
# #     })




#     @action(detail=False, methods=['get'], url_path='check-block', serializer_class=CheckBlockSerializer)
#     def check_block(self, request):
#         """
#         Check block status between current user and another user
#         """
#         serializer = self.get_serializer(data=request.query_params)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
        
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'user not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         is_blocked = Block.objects.filter(
#             blocker=request.user,
#             blocked=user
#         ).exists()
        
#         is_blocked_by = Block.objects.filter(
#             blocker=user,
#             blocked=request.user
#         ).exists()
        
#         return Response({
#             'user_id': user.id,
#             'username': user.username,
#             'is_blocked': is_blocked,
#             'is_blocked_by': is_blocked_by,
#             'can_interact': not is_blocked and not is_blocked_by
#         })


# class BlockedUsersMixin:
#     """
#     Mixin for handling blocked users in other views
#     """
    
#     def get_blocked_user_ids(self, user):
#         return list(
#             Block.objects.filter(blocker=user)
#             .values_list('blocked_id', flat=True)
#         )
    
#     def get_mutually_blocked_ids(self, user):
#         blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
#         blocked_by_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
#         return list(set(list(blocked_ids) + list(blocked_by_ids) + [user.id]))
    
#     def exclude_blocked(self, queryset, user):
#         blocked_ids = self.get_mutually_blocked_ids(user)
#         return queryset.exclude(id__in=blocked_ids)




# from rest_framework import status, generics
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.db.models import Prefetch

# from .models import Block
# from .serializers import (
#     BlockSerializer, 
#     BlockedUserSerializer, 
#     BlockRequestSerializer,
#     BlockUserSerializer,
#     UnblockUserSerializer,
#     ToggleBlockSerializer,
#     CheckBlockSerializer
# )

# User = get_user_model()


# class BlockViewSet(GenericViewSet, 
#                     ListModelMixin, 
#                     CreateModelMixin, 
#                     DestroyModelMixin):
#     """
#     ViewSet for managing user blocks
#     """
#     permission_classes = [IsAuthenticated]
#     http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
#     def get_serializer_class(self):
#         if self.action == 'blocked_list':
#             return BlockedUserSerializer
#         return BlockSerializer
    
#     def get_queryset(self):
#         return Block.objects.filter(blocker=self.request.user)
    
#     @action(detail=False, methods=['get'], url_path='blocked-list')
#     def blocked_list(self, request):
#         """
#         Get list of users blocked by current user
#         """
#         blocked_users = User.objects.filter(
#             blocked_by_set__blocker=request.user
#         ).prefetch_related(
#             Prefetch(
#                 'blocked_by_set',
#                 queryset=Block.objects.filter(blocker=request.user),
#                 to_attr='blocked_info'
#             )
#         ).order_by('-blocked_by_set__created_at')
        
#         page = self.paginate_queryset(blocked_users)
#         if page is not None:
#             serializer = BlockedUserSerializer(
#                 page, many=True, context={'request': request}
#             )
#             return self.get_paginated_response(serializer.data)
        
#         serializer = BlockedUserSerializer(
#             blocked_users, many=True, context={'request': request}
#         )
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['post'], url_path='block', serializer_class=BlockUserSerializer)
#     def block_user(self, request):
#         """
#         Block a user
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
#         reason = serializer.validated_data.get('reason', '')
        
#         try:
#             user_to_block = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'not found user'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         if user_to_block == request.user:
#             return Response(
#                 {'error': 'خود در گیری داری؟؟'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         exists = Block.objects.filter(
#             blocker=request.user,
#             blocked=user_to_block
#         ).exists()
        
#         if exists:
#             return Response(
#                 {'status': 'already has been blocked', 'message': 'this user had in block list in past'},
#                 status=status.HTTP_200_OK
#             )
        
#         block = Block.objects.create(
#             blocker=request.user,
#             blocked=user_to_block,
#             reason=reason
#         )
        
#         return Response(
#             {
#                 'status': 'blocked',
#                 'message': f'{user_to_block.username}',
#                 'blocked_user': {
#                     'id': user_to_block.id,
#                     'username': user_to_block.username,
#                     'phone': user_to_block.phone
#                 }
#             },
#             status=status.HTTP_201_CREATED
#         )
    
#     @action(detail=False, methods=['post'], url_path='unblock', serializer_class=UnblockUserSerializer)
#     def unblock_user(self, request):
#         """
#         Unblock a user
#         """
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
        
#         try:
#             user_to_unblock = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'user not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         deleted, _ = Block.objects.filter(
#             blocker=request.user,
#             blocked=user_to_unblock
#         ).delete()
        
#         if deleted:
#             return Response(
#                 {
#                     'status': 'unblocked',
#                     'message': f'user {user_to_unblock.username} has been unblocked'
#                 },
#                 status=status.HTTP_200_OK
#             )
        
#         return Response(
#             {'status': 'not_blocked', 'message': 'this user was not blocked'},
#             status=status.HTTP_200_OK
#         )
    
#     # @action(detail=False, methods=['post'], url_path='toggle-block', serializer_class=ToggleBlockSerializer)
#     # def toggle_block(self, request):
#     #     """
#     #     Toggle block status for a user (block if not blocked, unblock if blocked)
#     #     """
#     #     serializer = self.get_serializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
        
#     #     user_id = serializer.validated_data['user_id']
#     #     reason = serializer.validated_data.get('reason', '')
        
#     #     try:
#     #         user = User.objects.get(id=user_id)
#     #     except User.DoesNotExist:
#     #         return Response(
#     #             {'error': 'user not found error', 'success': False},
#     #             status=status.HTTP_404_NOT_FOUND
#     #         )
        
#     #     if user == request.user:
#     #         return Response(
#     #             {'error': 'نمیتوانید خودتان را بلاک کنید', 'success': False},
#     #             status=status.HTTP_400_BAD_REQUEST
#     #         )
        
#     #     blocked, created = Block.objects.get_or_create(
#     #         blocker=request.user,
#     #         blocked=user,
#     #         defaults={'reason': reason}
#     #     )
        
#     #     if not created:
#     #         blocked.delete()
#     #         return Response(
#     #             {'success': True, 'action': 'unblocked', 'message': f'کاربر {user.username} آنبلاک شد'},
#     #             status=status.HTTP_200_OK
#     #         )
        
#     #     return Response(
#     #         {'success': True, 'action': 'blocked', 'message': f'کاربر {user.username} بلاک شد'},
#     #         status=status.HTTP_201_CREATED
#     #     )


# @action(detail=False, methods=['post'], url_path='toggle-block', serializer_class=ToggleBlockSerializer)
# def toggle_block(self, request):
#     """
#     Toggle block status for a user (block if not blocked, unblock if blocked)
#     """
#     # این خط رو اضافه کن
#     print("=== toggle_block called ===")
#     print("Request method:", request.method)
    
#     serializer = self.get_serializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
    
#     user_id = serializer.validated_data['user_id']
#     reason = serializer.validated_data.get('reason', '')
    
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response(
#             {'error': 'user not found error', 'success': False},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     if user == request.user:
#         return Response(
#             {'error': 'نمیتوانید خودتان را بلاک کنید', 'success': False},
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     blocked, created = Block.objects.get_or_create(
#         blocker=request.user,
#         blocked=user,
#         defaults={'reason': reason}
#     )
    
#     if not created:
#         blocked.delete()
#         return Response(
#             {'success': True, 'action': 'unblocked', 'message': f'کاربر {user.username} آنبلاک شد'},
#             status=status.HTTP_200_OK
#         )
    
#     return Response(
#         {'success': True, 'action': 'blocked', 'message': f'کاربر {user.username} بلاک شد'},
#         status=status.HTTP_201_CREATED
#     )

#     @action(detail=False, methods=['get'], url_path='check-block', serializer_class=CheckBlockSerializer)
#     def check_block(self, request):
#         """
#         Check block status between current user and another user
#         """
#         serializer = self.get_serializer(data=request.query_params)
#         serializer.is_valid(raise_exception=True)
        
#         user_id = serializer.validated_data['user_id']
        
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'user not found', 'success': False},
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         is_blocked = Block.objects.filter(
#             blocker=request.user,
#             blocked=user
#         ).exists()
        
#         is_blocked_by = Block.objects.filter(
#             blocker=user,
#             blocked=request.user
#         ).exists()
        
#         return Response({
#             'success': True,
#             'user_id': str(user.id),
#             'username': user.username,
#             'is_blocked': is_blocked,
#             'is_blocked_by': is_blocked_by,
#             'can_interact': not is_blocked and not is_blocked_by
#         })


# class BlockedUsersMixin:
#     """
#     Mixin for handling blocked users in other views
#     """
    
#     def get_blocked_user_ids(self, user):
#         return list(
#             Block.objects.filter(blocker=user)
#             .values_list('blocked_id', flat=True)
#         )
    
#     def get_mutually_blocked_ids(self, user):
#         blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
#         blocked_by_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
#         return list(set(list(blocked_ids) + list(blocked_by_ids) + [user.id]))
    
#     def exclude_blocked(self, queryset, user):
#         blocked_ids = self.get_mutually_blocked_ids(user)
#         return queryset.exclude(id__in=blocked_ids)







from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from .models import Block
from .serializers import (
    BlockSerializer, 
    BlockedUserSerializer, 
    BlockRequestSerializer,
    BlockUserSerializer,
    UnblockUserSerializer,
    ToggleBlockSerializer,
    CheckBlockSerializer
)

User = get_user_model()


class BlockViewSet(GenericViewSet, 
                    ListModelMixin, 
                    CreateModelMixin, 
                    DestroyModelMixin):
    """
    ViewSet for managing user blocks
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'blocked_list':
            return BlockedUserSerializer
        if self.action == 'toggle_block':
            return ToggleBlockSerializer
        if self.action == 'check_block':
            return CheckBlockSerializer
        return BlockSerializer
    
    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='blocked-list')
    def blocked_list(self, request):
        """
        Get list of users blocked by current user
        """
        blocked_users = User.objects.filter(
            blocked_by_set__blocker=request.user
        ).prefetch_related(
            Prefetch(
                'blocked_by_set',
                queryset=Block.objects.filter(blocker=request.user),
                to_attr='blocked_info'
            )
        ).order_by('-blocked_by_set__created_at')
        
        page = self.paginate_queryset(blocked_users)
        if page is not None:
            serializer = BlockedUserSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = BlockedUserSerializer(
            blocked_users, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='block', serializer_class=BlockUserSerializer)
    def block_user(self, request):
        """
        Block a user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            user_to_block = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'not found user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user_to_block == request.user:
            return Response(
                {'error': 'خود در گیری داری؟؟'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = Block.objects.filter(
            blocker=request.user,
            blocked=user_to_block
        ).exists()
        
        if exists:
            return Response(
                {'status': 'already has been blocked', 'message': 'this user had in block list in past'},
                status=status.HTTP_200_OK
            )
        
        block = Block.objects.create(
            blocker=request.user,
            blocked=user_to_block,
            reason=reason
        )
        
        return Response(
            {
                'status': 'blocked',
                'message': f'{user_to_block.username}',
                'blocked_user': {
                    'id': user_to_block.id,
                    'username': user_to_block.username,
                    'phone': user_to_block.phone
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], url_path='unblock', serializer_class=UnblockUserSerializer)
    def unblock_user(self, request):
        """
        Unblock a user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            user_to_unblock = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'user not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        deleted, _ = Block.objects.filter(
            blocker=request.user,
            blocked=user_to_unblock
        ).delete()
        
        if deleted:
            return Response(
                {
                    'status': 'unblocked',
                    'message': f'user {user_to_unblock.username} has been unblocked'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'status': 'not_blocked', 'message': 'this user was not blocked'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='toggle-block', serializer_class=ToggleBlockSerializer)
    def toggle_block(self, request):
        """
        Toggle block status for a user (block if not blocked, unblock if blocked)
        """
        print("=== toggle_block called ===")
        print("Request method:", request.method)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'user not found error', 'success': False},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == request.user:
            return Response(
                {'error': 'نمیتوانید خودتان را بلاک کنید', 'success': False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blocked, created = Block.objects.get_or_create(
            blocker=request.user,
            blocked=user,
            defaults={'reason': reason}
        )
        
        if not created:
            blocked.delete()
            return Response(
                {'success': True, 'action': 'unblocked', 'message': f'کاربر {user.username} آنبلاک شد'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'success': True, 'action': 'blocked', 'message': f'کاربر {user.username} بلاک شد'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], url_path='check-block', serializer_class=CheckBlockSerializer)
    def check_block(self, request):
        """
        Check block status between current user and another user
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'user not found', 'success': False},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_blocked = Block.objects.filter(
            blocker=request.user,
            blocked=user
        ).exists()
        
        is_blocked_by = Block.objects.filter(
            blocker=user,
            blocked=request.user
        ).exists()
        
        return Response({
            'success': True,
            'user_id': str(user.id),
            'username': user.username,
            'is_blocked': is_blocked,
            'is_blocked_by': is_blocked_by,
            'can_interact': not is_blocked and not is_blocked_by
        })


class BlockedUsersMixin:
    """
    Mixin for handling blocked users in other views
    """
    
    def get_blocked_user_ids(self, user):
        return list(
            Block.objects.filter(blocker=user)
            .values_list('blocked_id', flat=True)
        )
    
    def get_mutually_blocked_ids(self, user):
        blocked_ids = Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)
        blocked_by_ids = Block.objects.filter(blocked=user).values_list('blocker_id', flat=True)
        return list(set(list(blocked_ids) + list(blocked_by_ids) + [user.id]))
    
    def exclude_blocked(self, queryset, user):
        blocked_ids = self.get_mutually_blocked_ids(user)
        return queryset.exclude(id__in=blocked_ids)