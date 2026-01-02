from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import OCRDocument, OCRResult, PDFPageResult, OCRProcessingLog


@admin.register(OCRDocument)
class OCRDocumentAdmin(admin.ModelAdmin):
    """Admin interface for OCR Documents"""
    
    list_display = [
        'id', 'file_name', 'file_type', 'status_badge', 
        'file_size_display', 'language', 'uploaded_at', 'view_results'
    ]
    list_filter = ['status', 'file_type', 'language', 'is_deleted', 'uploaded_at']
    search_fields = ['file_name', 'file_hash', 'uuid']
    readonly_fields = [
        'uuid', 'file_hash', 'uploaded_at', 'processed_at', 
        'deleted_at', 'archived_at', 'file_size_display'
    ]
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Identification', {
            'fields': ('uuid', 'file_name', 'file_type')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'file_size_display', 'file_hash')
        }),
        ('Processing', {
            'fields': ('status', 'language', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'archived_at', 'is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_archived', 'mark_as_completed', 'soft_delete_documents']
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#FFA500',
            'processing': '#2196F3',
            'completed': '#4CAF50',
            'failed': '#F44336',
            'archived': '#9E9E9E',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    file_size_display.short_description = 'File Size'
    
    def view_results(self, obj):
        """Link to view results"""
        count = obj.results.count()
        if count > 0:
            url = reverse('admin:ocr_ocrresult_changelist') + f'?document__id__exact={obj.id}'
            return format_html('<a href="{}">{} result(s)</a>', url, count)
        return '-'
    view_results.short_description = 'Results'
    
    def mark_as_archived(self, request, queryset):
        """Archive selected documents"""
        count = 0
        for doc in queryset:
            doc.archive()
            count += 1
        self.message_user(request, f'{count} document(s) archived successfully.')
    mark_as_archived.short_description = 'Archive selected documents'
    
    def mark_as_completed(self, request, queryset):
        """Mark selected documents as completed"""
        updated = queryset.update(status='completed', processed_at=timezone.now())
        self.message_user(request, f'{updated} document(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def soft_delete_documents(self, request, queryset):
        """Soft delete selected documents"""
        count = 0
        for doc in queryset:
            doc.soft_delete()
            count += 1
        self.message_user(request, f'{count} document(s) soft deleted.')
    soft_delete_documents.short_description = 'Soft delete selected documents'


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    """Admin interface for OCR Results"""
    
    list_display = [
        'id', 'document_link', 'extraction_method', 'language',
        'word_count', 'character_count', 'confidence_display', 
        'processing_time_display', 'created_at'
    ]
    list_filter = ['extraction_method', 'language', 'created_at']
    search_fields = ['document__file_name', 'uuid', 'extracted_text']
    readonly_fields = [
        'uuid', 'word_count', 'character_count', 'created_at', 
        'text_preview', 'processing_time_display'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identification', {
            'fields': ('uuid', 'document')
        }),
        ('Extraction Results', {
            'fields': ('extracted_text', 'text_preview', 'word_count', 'character_count')
        }),
        ('Processing Details', {
            'fields': (
                'extraction_method', 'language', 'processing_time_ms', 
                'processing_time_display', 'confidence_score'
            )
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def document_link(self, obj):
        """Link to document"""
        url = reverse('admin:ocr_ocrdocument_change', args=[obj.document.id])
        return format_html('<a href="{}">{}</a>', url, obj.document.file_name)
    document_link.short_description = 'Document'
    
    def confidence_display(self, obj):
        """Display confidence score with color"""
        if obj.confidence_score is None:
            return '-'
        score = obj.confidence_score
        if score >= 80:
            color = '#4CAF50'
        elif score >= 60:
            color = '#FFA500'
        else:
            color = '#F44336'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, score
        )
    confidence_display.short_description = 'Confidence'
    
    def processing_time_display(self, obj):
        """Display processing time in human-readable format"""
        if obj.processing_time_ms is None:
            return '-'
        if obj.processing_time_ms < 1000:
            return f"{obj.processing_time_ms} ms"
        return f"{obj.processing_time_ms / 1000:.2f} s"
    processing_time_display.short_description = 'Processing Time'
    
    def text_preview(self, obj):
        """Show preview of extracted text"""
        if obj.extracted_text:
            preview = obj.extracted_text[:200]
            if len(obj.extracted_text) > 200:
                preview += '...'
            return preview
        return '-'
    text_preview.short_description = 'Text Preview'


@admin.register(PDFPageResult)
class PDFPageResultAdmin(admin.ModelAdmin):
    """Admin interface for PDF Page Results"""
    
    list_display = [
        'id', 'result_link', 'page_number', 'extraction_method',
        'word_count', 'character_count', 'confidence_display', 'created_at'
    ]
    list_filter = ['extraction_method', 'created_at']
    search_fields = ['result__document__file_name', 'extracted_text']
    readonly_fields = ['word_count', 'character_count', 'created_at', 'text_preview']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identification', {
            'fields': ('result', 'page_number')
        }),
        ('Extraction Results', {
            'fields': ('extracted_text', 'text_preview', 'word_count', 'character_count')
        }),
        ('Processing Details', {
            'fields': ('extraction_method', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def result_link(self, obj):
        """Link to parent result"""
        url = reverse('admin:ocr_ocrresult_change', args=[obj.result.id])
        return format_html('<a href="{}">{}</a>', url, obj.result)
    result_link.short_description = 'Result'
    
    def confidence_display(self, obj):
        """Display confidence score"""
        if obj.confidence_score is None:
            return '-'
        return f"{obj.confidence_score:.2f}%"
    confidence_display.short_description = 'Confidence'
    
    def text_preview(self, obj):
        """Show preview of extracted text"""
        if obj.extracted_text:
            preview = obj.extracted_text[:200]
            if len(obj.extracted_text) > 200:
                preview += '...'
            return preview
        return '-'
    text_preview.short_description = 'Text Preview'


@admin.register(OCRProcessingLog)
class OCRProcessingLogAdmin(admin.ModelAdmin):
    """Admin interface for OCR Processing Logs"""
    
    list_display = [
        'id', 'document_link', 'level_badge', 'message_preview', 'created_at'
    ]
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'document__file_name']
    readonly_fields = ['document', 'level', 'message', 'details', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('document', 'level', 'message')
        }),
        ('Details', {
            'fields': ('details',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Logs are created programmatically"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs are read-only"""
        return False
    
    def document_link(self, obj):
        """Link to document"""
        url = reverse('admin:ocr_ocrdocument_change', args=[obj.document.id])
        return format_html('<a href="{}">{}</a>', url, obj.document.file_name)
    document_link.short_description = 'Document'
    
    def level_badge(self, obj):
        """Display log level with color"""
        colors = {
            'info': '#2196F3',
            'warning': '#FFA500',
            'error': '#F44336',
        }
        color = colors.get(obj.level, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_level_display()
        )
    level_badge.short_description = 'Level'
    
    def message_preview(self, obj):
        """Show preview of message"""
        if len(obj.message) > 100:
            return obj.message[:100] + '...'
        return obj.message
    message_preview.short_description = 'Message'
