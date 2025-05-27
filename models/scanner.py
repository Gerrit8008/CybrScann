from datetime import datetime

class Scanner:
    """Scanner model matching the database schema used in scanner_db_functions.py"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.client_id = kwargs.get('client_id')
        self.scanner_id = kwargs.get('scanner_id')  # Unique scanner identifier
        self.name = kwargs.get('name')
        self.description = kwargs.get('description', '')
        self.domain = kwargs.get('domain')
        self.api_key = kwargs.get('api_key')
        self.primary_color = kwargs.get('primary_color', '#02054c')
        self.secondary_color = kwargs.get('secondary_color', '#35a310')
        self.logo_url = kwargs.get('logo_url', '')
        self.contact_email = kwargs.get('contact_email')
        self.contact_phone = kwargs.get('contact_phone', '')
        self.email_subject = kwargs.get('email_subject', 'Your Security Scan Report')
        self.email_intro = kwargs.get('email_intro', '')
        self.scan_types = kwargs.get('scan_types', '')
        self.status = kwargs.get('status', 'draft')
        self.created_by = kwargs.get('created_by')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'scanner_id': self.scanner_id,
            'name': self.name,
            'description': self.description,
            'domain': self.domain,
            'api_key': self.api_key,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'logo_url': self.logo_url,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'email_subject': self.email_subject,
            'email_intro': self.email_intro,
            'scan_types': self.scan_types,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Scanner instance from dictionary"""
        return cls(**data)
