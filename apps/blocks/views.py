from django.shortcuts import render

# Create your views here.
# apps/blocks/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from .models import Block
from .serializers import BlockSerializer, BlockedUserSerializer, BlockRequestSerializer

User = get_user_model()


class BlockViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'blocked_list':
            return BlockedUserSerializer
        return BlockSerializer
    
    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='blocked-list')
    def blocked_list(self, request):
        
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
    
    @action(detail=False, methods=['post'], url_path='block')
    def block_user(self, request):
        
        serializer = BlockRequestSerializer(data=request.data)
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
                {'status': 'already_blocked', 'message': 'this user had in bloke list in passt'},
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
                'message': f' {user_to_block.username} ',
                'blocked_user': {
                    'id': user_to_block.id,
                    'username': user_to_block.username,
                    'phone': user_to_block.phone
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], url_path='unblock')
    def unblock_user(self, request):
        
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id '},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_unblock = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'the '},
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
                    'message': f'user {user_to_unblock.username} this user has been unbloked'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'status': 'not_blocked', 'message': 'this user has been bloked'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='toggle-block')
    def toggle_block(self, request):
        
        
        serializer = BlockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'user not found error'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user == request.user:
            return Response(
                {'error': 'خود درگیری داری ؟؟'},
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
                {'status': 'unblocked', 'action': 'unblock'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'status': 'blocked', 'action': 'block'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], url_path='check-block')
    def check_block(self, request):
        
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id  is should put in '},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': ' not founds user  '},
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
            'user_id': user.id,
            'username': user.username,
            'is_blocked': is_blocked,
            'is_blocked_by': is_blocked_by,
            'can_interact': not is_blocked and not is_blocked_by
        })



class BlockedUsersMixin:
    # who one user bloced this user
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