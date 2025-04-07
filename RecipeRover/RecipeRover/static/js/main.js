document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && 
                !mobileMenuToggle.contains(event.target) && 
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }
    
    // Notifications dropdown
    const notificationToggle = document.querySelector('.notification-toggle');
    const notificationsDropdown = document.querySelector('.notifications-dropdown');
    
    if (notificationToggle && notificationsDropdown) {
        notificationToggle.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            notificationsDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (notificationsDropdown.classList.contains('show') && 
                !notificationsDropdown.contains(event.target) && 
                !notificationToggle.contains(event.target)) {
                notificationsDropdown.classList.remove('show');
            }
        });
        
        // Mark notifications as read
        const markAllReadBtn = document.querySelector('.mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                fetch('/notifications/mark_all_read', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const unreadItems = document.querySelectorAll('.notification-item.unread');
                        unreadItems.forEach(item => {
                            item.classList.remove('unread');
                        });
                        
                        const badge = document.querySelector('.notification-badge .badge');
                        if (badge) {
                            badge.textContent = '0';
                            badge.style.display = 'none';
                        }
                    }
                });
            });
        }
        
        // Handle individual notification click
        const notificationItems = document.querySelectorAll('.notification-item');
        notificationItems.forEach(item => {
            item.addEventListener('click', function() {
                const notificationId = this.dataset.id;
                if (notificationId && this.classList.contains('unread')) {
                    fetch(`/notifications/mark_read/${notificationId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken()
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            this.classList.remove('unread');
                            
                            const badge = document.querySelector('.notification-badge .badge');
                            if (badge) {
                                const count = parseInt(badge.textContent) - 1;
                                badge.textContent = count;
                                if (count <= 0) {
                                    badge.style.display = 'none';
                                }
                            }
                        }
                    });
                }
                
                // If there's a link associated with the notification
                const link = this.dataset.link;
                if (link) {
                    window.location.href = link;
                }
            });
        });
    }
    
    // Setup AJAX for forms
    setupAjaxForms();
    
    // Setup delete confirmations
    setupDeleteConfirmations();
    
    // Journal entry lines
    setupJournalEntryLines();
    
    // Setup datepickers
    setupDatepickers();
    
    // Initialize tooltips
    initTooltips();
});

// Get CSRF token from meta tag
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Setup AJAX forms
function setupAjaxForms() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.getAttribute('action');
            const method = this.getAttribute('method');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Traitement...';
                submitBtn.disabled = true;
            }
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else if (data.reload) {
                        window.location.reload();
                    } else {
                        // Show success message
                        showAlert('success', data.message || 'Opération réussie.');
                        
                        // Clear form
                        if (data.clearForm) {
                            this.reset();
                        }
                    }
                } else {
                    // Show error message
                    showAlert('danger', data.message || 'Une erreur est survenue.');
                    
                    // Show field errors
                    if (data.errors) {
                        for (const field in data.errors) {
                            const errorElement = document.getElementById(`${field}-error`);
                            if (errorElement) {
                                errorElement.textContent = data.errors[field];
                                errorElement.style.display = 'block';
                            }
                        }
                    }
                }
                
                if (submitBtn) {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Une erreur est survenue lors de la requête.');
                
                if (submitBtn) {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            });
        });
    });
}

// Setup delete confirmations
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {
                e.preventDefault();
            }
        });
    });
}

// Show alert
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertsContainer.removeChild(alert);
        }, 150);
    }, 5000);
}

// Journal entry lines
function setupJournalEntryLines() {
    const addLineForm = document.getElementById('add-line-form');
    if (!addLineForm) return;
    
    addLineForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const url = this.getAttribute('action');
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Add line to table
                const tbody = document.querySelector('#journal-lines tbody');
                const row = document.createElement('tr');
                row.dataset.id = data.line.id;
                
                row.innerHTML = `
                    <td>${data.line.account_code} - ${data.line.account_name}</td>
                    <td>${data.line.description || ''}</td>
                    <td class="text-right">${Number(data.line.debit).toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="text-right">${Number(data.line.credit).toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="text-center">
                        <button type="button" class="btn btn-sm btn-danger delete-line" data-id="${data.line.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
                
                // Update totals
                updateJournalEntryTotals();
                
                // Reset form
                this.reset();
                
                // Show success message
                showAlert('success', data.message || 'Ligne ajoutée avec succès.');
                
                // Attach delete listener to new button
                attachDeleteLineListener(row.querySelector('.delete-line'));
            } else {
                // Show error message
                showAlert('danger', data.message || 'Une erreur est survenue.');
                
                // Show field errors
                if (data.errors) {
                    for (const field in data.errors) {
                        const errorElement = document.getElementById(`${field}-error`);
                        if (errorElement) {
                            errorElement.textContent = data.errors[field];
                            errorElement.style.display = 'block';
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Une erreur est survenue lors de la requête.');
        });
    });
    
    // Attach delete listeners to existing buttons
    document.querySelectorAll('.delete-line').forEach(attachDeleteLineListener);
    
    function attachDeleteLineListener(button) {
        button.addEventListener('click', function() {
            const lineId = this.dataset.id;
            const entryId = document.getElementById('entry_id').value;
            const url = `/journal/${entryId}/delete_line/${lineId}`;
            
            if (!confirm('Êtes-vous sûr de vouloir supprimer cette ligne ?')) {
                return;
            }
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Remove row from table
                    const row = document.querySelector(`tr[data-id="${lineId}"]`);
                    if (row) {
                        row.remove();
                    }
                    
                    // Update totals
                    updateJournalEntryTotals();
                    
                    // Show success message
                    showAlert('success', data.message || 'Ligne supprimée avec succès.');
                } else {
                    // Show error message
                    showAlert('danger', data.message || 'Une erreur est survenue.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'Une erreur est survenue lors de la requête.');
            });
        });
    }
    
    function updateJournalEntryTotals() {
        const rows = document.querySelectorAll('#journal-lines tbody tr');
        let totalDebit = 0;
        let totalCredit = 0;
        
        rows.forEach(row => {
            const debitCell = row.cells[2].textContent;
            const creditCell = row.cells[3].textContent;
            
            totalDebit += parseFloat(debitCell.replace(/\s/g, '').replace(',', '.')) || 0;
            totalCredit += parseFloat(creditCell.replace(/\s/g, '').replace(',', '.')) || 0;
        });
        
        document.getElementById('total-debit').textContent = totalDebit.toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.getElementById('total-credit').textContent = totalCredit.toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        const balanceElement = document.getElementById('balance');
        if (balanceElement) {
            const difference = Math.abs(totalDebit - totalCredit).toFixed(2);
            balanceElement.textContent = difference;
            
            if (Math.abs(totalDebit - totalCredit) < 0.01) {
                balanceElement.parentElement.classList.remove('text-danger');
                balanceElement.parentElement.classList.add('text-success');
                document.getElementById('balance-status').innerHTML = '<i class="fas fa-check-circle"></i> Écriture équilibrée';
                document.getElementById('balance-status').className = 'text-success';
            } else {
                balanceElement.parentElement.classList.remove('text-success');
                balanceElement.parentElement.classList.add('text-danger');
                document.getElementById('balance-status').innerHTML = '<i class="fas fa-exclamation-circle"></i> Écriture non équilibrée';
                document.getElementById('balance-status').className = 'text-danger';
            }
        }
    }
    
    // Update totals on page load
    updateJournalEntryTotals();
}

// Setup datepickers
function setupDatepickers() {
    const datepickers = document.querySelectorAll('.datepicker');
    
    datepickers.forEach(input => {
        if (window.flatpickr) {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                locale: "fr",
                altInput: true,
                altFormat: "d/m/Y"
            });
        }
    });
}

// Initialize tooltips
function initTooltips() {
    if (window.bootstrap && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}
