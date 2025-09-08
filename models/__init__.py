"""
Models package for Mini Email CRM
Exports all data models and related enums
"""

from .contact import Contact
from .email_template import EmailTemplate, TemplateType
from .campaign import Campaign, CampaignStatus, EmailStatus, EmailResult

__all__ = [
    'Contact',
    'EmailTemplate', 
    'TemplateType',
    'Campaign',
    'CampaignStatus', 
    'EmailStatus',
    'EmailResult'
]