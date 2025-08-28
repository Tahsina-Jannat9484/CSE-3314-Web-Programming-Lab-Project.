from django.contrib import admin
from .models import CSVUpload, CSVRecord, ChatSession, ChatMessage


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ['name', 'uploaded_at', 'uploaded_by', 'processed']
    list_filter = ['processed', 'uploaded_at']
    search_fields = ['name']
    readonly_fields = ['uploaded_at']


@admin.register(CSVRecord)
class CSVRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'csv_upload', 'score', 'rank', 'created_at']
    list_filter = ['csv_upload', 'created_at']
    search_fields = ['csv_upload__name']
    readonly_fields = ['created_at']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'csv_upload', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session_id', 'csv_upload__name']
    readonly_fields = ['created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
