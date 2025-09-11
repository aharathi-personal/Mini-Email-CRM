# Global UI Design Guidelines - Enhanced

## Color Scheme:
- **Primary**: Blue (#2196F3)
- **Success**: Green (#4CAF50)
- **Error**: Red (#F44336)
- **Warning**: Orange (#FF9800)
- **Background**: Light gray (#F5F5F5)
- **Text**: Dark gray (#333333)
- **Secondary**: Light blue (#E3F2FD) - for attachment areas, info panels
- **Neutral**: Gray (#9E9E9E) - for disabled states, placeholder text

## Typography:
- **Headers**: Bold, 14-16pt
- **Body text**: Regular, 10-12pt
- **Buttons**: Bold, 10pt
- **Monospace**: For email addresses and code
- **Small text**: Regular, 9pt - for file sizes, metadata
- **Captions**: Regular, 8pt - for help text, secondary info

## Common Elements:
- **Buttons**: Consistent sizing, rounded corners (4px border radius)
- **Input fields**: Clear borders, focus states
- **Progress indicators**: Consistent styling
- **Error messages**: Clear, actionable text
- **Cards/Panels**: Subtle drop shadow, 8px border radius
- **Icons**: Consistent size (16px for inline, 24px for standalone)

## **NEW: Attachment UI Elements:**

### File Attachment Areas:
- **Background**: Light blue (#E3F2FD)
- **Border**: Dashed border (#2196F3) for drop zones
- **Solid border** for attachment lists
- **Hover state**: Slightly darker background (#BBDEFB)

### Attachment Items:
- **Container**: White background with light gray border
- **File icon**: 20px, positioned left
- **Remove button**: Red (#F44336) X icon, 16px
- **File size**: Gray (#9E9E9E) text, 9pt
- **File name**: Regular text, 10pt, truncated if too long

### File Type Icons:
- **PDF**: Red icon (#F44336)
- **Images**: Blue icon (#2196F3) 
- **Documents**: Green icon (#4CAF50)
- **Other**: Gray icon (#9E9E9E)

## **NEW: Interactive States:**

### Drag and Drop:
- **Drag over**: Blue dashed border becomes solid
- **Drop zone active**: Background changes to #E3F2FD
- **Invalid file**: Red border (#F44336) with warning message

### Loading States:
- **File processing**: Small spinner next to filename
- **Upload progress**: Mini progress bar under attachment item
- **Validation**: Check mark (green) or X (red) icons

## Navigation Flow:
- **Back buttons**: Always available (except on landing)
- **Clear step indicators**: Progress dots or breadcrumb
- **Confirmation dialogs**: For destructive actions
- **Keyboard shortcuts**: For power users (optional)

## **ENHANCED: Error Handling:**

### Validation Messages:
- **Inline validation**: Red text below input fields
- **Clear error states**: Red borders on invalid inputs
- **Recovery suggestions**: Actionable help text
- **Non-blocking notifications**: Toast messages for system feedback

### **NEW: Attachment-Specific Errors:**
- **File too large**: "File size exceeds 25MB limit. Please choose a smaller file."
- **Invalid file type**: "This file type is not supported. Please select PDF, image, or document files."
- **Total size limit**: "Total attachment size would exceed 25MB. Please remove some files."
- **Upload failed**: "Failed to attach [filename]. Please try again."

## **NEW: Spacing and Layout:**

### Consistent Spacing:
- **Component padding**: 12px internal padding
- **Element margins**: 8px between related elements, 16px between sections
- **Button spacing**: 8px between buttons
- **Attachment list**: 4px between items

### Responsive Behavior:
- **Min-width**: 800px for optimal experience
- **Attachment list**: Scrollable if more than 5 items
- **File names**: Truncate with ellipsis (...) if longer than container

## **NEW: Visual Hierarchy:**

### Attachment Section Priority:
- **Attached files**: Clear section divider
- **File count**: Show total count and size summary
- **Visual weight**: Lighter than main email content but clearly present
- **Collapsible**: Allow hiding attachment area when not in use (optional)

### Icon Usage:
- **Consistent size**: 16px for toolbar icons, 20px for file type icons
- **Color coding**: Use theme colors for different file types
- **Hover states**: Slight opacity change (0.8) or color shift

## **NEW: Accessibility Considerations:**

### Keyboard Navigation:
- **Tab order**: Logical flow through attachment controls
- **Enter/Space**: Activate attachment button and remove buttons
- **Escape**: Cancel file selection dialog

### Screen Readers:
- **Alt text**: Descriptive text for attachment icons
- **Labels**: Clear labels for attachment controls
- **Status**: Announce attachment count and validation errors

### Visual Accessibility:
- **Color contrast**: Ensure all text meets WCAG AA standards
- **Focus indicators**: Clear visual focus states for all interactive elements
- **Error states**: Don't rely solely on color for error indication

## Implementation Notes:

### CSS Classes Suggestion:
```
.attachment-zone { /* Drop zone styling */ }
.attachment-item { /* Individual attachment styling */ }
.attachment-error { /* Error state styling */ }
.file-icon-pdf/.file-icon-img/.file-icon-doc { /* File type icons */ }
.attachment-remove { /* Remove button styling */ }
```

### Animation Guidelines:
- **Subtle**: 200ms transitions for hover states
- **File drops**: Brief highlight animation on successful drop
- **Removal**: Small fade-out animation when removing attachments
- **Progress**: Smooth progress bar animations during upload/sending

This enhanced design system maintains your existing clean, professional aesthetic while providing comprehensive guidance for implementing the attachment feature seamlessly.