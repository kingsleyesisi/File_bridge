// Enhanced FileBridge JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Form validation for receiver page
    const inputField1 = document.getElementById('username');
    const inputField2 = document.getElementById('Room_Name');
    const text = document.getElementById('iptext');
    const btn = document.querySelector('#submit-btn');

    if (inputField1 && inputField2 && btn) {
        function validateForm() {
            const username = inputField1.value.trim();
            const roomName = inputField2.value.trim();
            
            // Clear previous messages
            text.textContent = '';
            text.className = '';
            
            if (!username || !roomName) {
                text.textContent = 'Please enter both your name and room name';
                text.className = 'status-message status-error';
                btn.disabled = true;
                return false;
            }
            
            if (username.length < 2) {
                text.textContent = 'Name must be at least 2 characters long';
                text.className = 'status-message status-error';
                btn.disabled = true;
                return false;
            }
            
            if (roomName.length < 3) {
                text.textContent = 'Room name must be at least 3 characters long';
                text.className = 'status-message status-error';
                btn.disabled = true;
                return false;
            }
            
            // Validate characters (alphanumeric, spaces, hyphens, underscores)
            const validPattern = /^[a-zA-Z0-9\s\-_]+$/;
            if (!validPattern.test(username)) {
                text.textContent = 'Name can only contain letters, numbers, spaces, hyphens, and underscores';
                text.className = 'status-message status-error';
                btn.disabled = true;
                return false;
            }
            
            if (!validPattern.test(roomName)) {
                text.textContent = 'Room name can only contain letters, numbers, spaces, hyphens, and underscores';
                text.className = 'status-message status-error';
                btn.disabled = true;
                return false;
            }
            
            // All validations passed
            btn.disabled = false;
            return true;
        }

        // Real-time validation
        inputField1.addEventListener('input', validateForm);
        inputField2.addEventListener('input', validateForm);
        
        // Initial validation
        validateForm();
        
        // Form submission
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (!validateForm()) {
                    e.preventDefault();
                    return false;
                }
                
                // Show loading state
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
                btn.disabled = true;
            });
        }
    }

    // Enhanced file upload handling
    const fileInput = document.getElementById('fileinput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
            }
        });
    }

    function validateFile(file) {
        const maxSize = 2000 * 1024 * 1024; // 2GB
        const allowedTypes = [
            // Documents
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'text/csv',
            
            // Images
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/gif',
            'image/webp',
            'image/svg+xml',
            
            // Audio
            'audio/mpeg',
            'audio/wav',
            'audio/ogg',
            'audio/mp4',
            
            // Video
            'video/mp4',
            'video/avi',
            'video/mov',
            'video/wmv',
            'video/webm',
            
            // Archives
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip'
        ];

        if (file.size > maxSize) {
            showNotification('File size exceeds 2GB limit', 'error');
            fileInput.value = '';
            return false;
        }

        // For security, we'll be more permissive but still validate
        const fileName = file.name.toLowerCase();
        const dangerousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js', '.jar'];
        
        if (dangerousExtensions.some(ext => fileName.endsWith(ext))) {
            showNotification('This file type is not allowed for security reasons', 'error');
            fileInput.value = '';
            return false;
        }

        return true;
    }

    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `status-message status-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
        `;
        
        // Add to page
        const container = document.querySelector('.main-container') || document.body;
        container.insertBefore(notification, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // Format file size helper
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Copy room link functionality
    function copyRoomLink() {
        const roomName = new URLSearchParams(window.location.search).get('room');
        if (roomName) {
            const link = `${window.location.origin}/receiver?room=${encodeURIComponent(roomName)}`;
            navigator.clipboard.writeText(link).then(() => {
                showNotification('Room link copied to clipboard!', 'success');
            }).catch(() => {
                showNotification('Failed to copy link', 'error');
            });
        }
    }

    // Auto-populate room name from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const roomParam = urlParams.get('room');
    if (roomParam && inputField2) {
        inputField2.value = decodeURIComponent(roomParam);
        validateForm();
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const submitBtn = document.querySelector('#submit-btn');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
    });

    // Enhanced accessibility
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Global utility functions
window.FileBridge = {
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `status-message status-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
        `;
        
        const container = document.querySelector('.main-container') || document.body;
        container.insertBefore(notification, container.firstChild);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
};