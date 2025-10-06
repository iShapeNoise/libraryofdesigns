# LoD - Library of Designs

---

# Overview

---

## Purpose and Scope

Library of Designs (LoD) is a comprehensive Django-based web platform for sharing, creating, and collaborating on parametric OpenSCAD designs. The platform provides integrated tools for design management, CAD editing, educational content, and community communication.

This overview introduces the system's architecture, core applications, and primary features. For detailed installation and setup instructions, see page 2 (Getting Started). For in-depth technical architecture details, see page 3 (System Architecture). For specific information about individual Django applications, see page 5 (Django Applications).

---

## System Description

Library of Designs is a complete ecosystem for parametric design workflows built around OpenSCAD. The platform enables users to:

* **Browse and download** parametric designs organized by hierarchical categories
* **Create and edit** OpenSCAD designs using an integrated web-based CAD editor
* **Manage design metadata** including bills of materials, images, and technical drawings
* **Learn** through structured tutorials and courses on CAD, CAM, and the LoD platform
* **Communicate** with other users through messaging and forum discussions
* **Track contributions** via a personal dashboard

The system is built using Django 5.2 and follows a modular application architecture with seven primary Django apps: `core`, `design`, `editor`, `knowhow`, `conversation`, `dashboard`, and `forum`. Each app provides distinct functionality while sharing common data models and authentication infrastructure.

---

## Core Functionality

The Library of Designs platform provides seven primary functional areas:

| Functional Area | Django App | Key Features | Primary Models |
|--|--|--|--|
| Design Management | design | CRUD operations, category browsing, BOM management, file downloads | Design, Category, BillOfMaterials, Tag |
| CAD Editor | editor | OpenSCAD code editing, rendering, save | CADProject, RenderJob |
| Authentication & Profiles | core | Login/signup, profile management, category system | User, UserProfile, ContactMessage |
| Educational Content | knowhow | Tutorials, courses on CAD/CAM/LoD | File-based content structure |
| User Communication | conversation | Design-related messaging, inbox | Conversation, ConversationMessage |
| Personal Dashboard | dashboard | User's own designs overview | Uses Design model |
| Community Forum | forum | Discussion boards | Forum-specific models |


---

### Design Workflow

The typical design workflow involves:

1. **Discovery**: Users browse designs by category or search
2. **Viewing**: Design detail pages show images, technical drawings, BOM, and download options
3. **Creation**: Authenticated users create new designs via forms with multi-file upload
4. **Editing**: Users can edit their own designs using web-based CAD editor
5. **Collaboration**: Users communicate about designs through conversations

---

### File Storage Architecture

Design files are organized in a hierarchical directory structure under `LOD_CONTENT_ROOT`:

```
LOD_CONTENT_ROOT/
├── designs/
│   └── category_path/
│       └── design_name/
│           ├── images/
│           ├── techdraws/
│           ├── design/
│           └── *.scad files
├── knowhow/
│   └── section/course_name/
├── utilities/
│   └── LOD_OPENSCAD_*.scad
└── static content (LICENSE.md, TERMS_OF_USE.md, etc.)
```

---

### Django Application Components

Each Django application follows a standard structure:

```
app_name/
├── apps.py              # AppConfig class
├── models.py            # Data models
├── views.py             # Request handlers
├── forms.py             # Form definitions (if applicable)
├── urls.py              # URL patterns
├── admin.py             # Admin configurations
├── templates/app_name/  # HTML templates
├── migrations/          # Database migrations
└── __init__.py
```

---

## Key Technologies and Dependencies

The Library of Designs platform is built on the following technology stack:

* **Framework**: Django (Python web framework)
* **Database**: PostgreSQL for primary data storage
* **Forms**: django-crispy-forms for enhanced form rendering
* **Administration**: Customized Django admin interface
* **Documentation**: DeepWiki integration for project documentation

The platform leverages Django's built-in capabilities for user authentication, admin interface, and ORM while extending functionality through custom models and views specific to design collaboration workflows.





[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/iShapeNoise/libraryofdesigns)
