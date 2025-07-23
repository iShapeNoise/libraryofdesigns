import os
import re 
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from design.models import Category
from django.db import transaction


class Command(BaseCommand):
    help = 'Load categories from markdown file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='CATEGORIES.md',
            help='Path to the markdown file containing categories (default: CATEGORIES.md in LOD_CONTENT_ROOT)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing categories before loading new ones (keeps existing IDs if categories match)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing categories (create if not exists, keep existing IDs)'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Replace all categories: clear database completely and reload all categories with new IDs'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        # If relative path, assume it's in LOD_CONTENT_ROOT 
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.LOD_CONTENT_ROOT, 'designs', file_path)
        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist.')

        # Handle different operation modes
        if options['replace']:
            self.stdout.write('REPLACE mode: Clearing all categories and reloading...')
            self.clear_all_categories()
            categories_created = self.load_categories_from_file(file_path, update_mode=False)
        elif options['clear']:
            self.stdout.write('CLEAR mode: Clearing existing categories before loading...')
            self.clear_all_categories()
            categories_created = self.load_categories_from_file(file_path, update_mode=False)
        elif options['update']:
            self.stdout.write('UPDATE mode: Updating existing categories...')
            categories_created = self.load_categories_from_file(file_path, update_mode=True)
        else:
            self.stdout.write('DEFAULT mode: Creating new categories only...')
            categories_created = self.load_categories_from_file(file_path, update_mode=False)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {categories_created} categories from "{file_path}"'
            )
        )

    def clear_all_categories(self):
        """Completely clear all categories from the database"""
        try:
            with transaction.atomic():
                # Get count before deletion for reporting  
                count = Category.objects.count()

                # Delete all categories (this will cascade to children due to MPTT) 
                Category.objects.all().delete()

                # Reset the auto-increment counter (PostgreSQL specific)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("ALTER SEQUENCE design_category_id_seq RESTART WITH 1;")

                self.stdout.write(f'Cleared {count} existing categories and reset ID sequence.')
        except Exception as e:
            raise CommandError(f'Error clearing categories: {str(e)}')

    def load_categories_from_file(self, file_path, update_mode=False):
        """Parse markdown file and create category tree"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        lines = content.split('\n')
        category_stack = []  # Stack to track parent categories at each level
        categories_processed = 0

        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            if not line:
                continue

            # Parse markdown list structure (-, *, +) or numbered lists 
            level, category_name = self.parse_line(line)

            if level is None or not category_name:
                continue

            # Adjust stack size to current level  
            category_stack = category_stack[:level]

            # Get parent category (if any)
            parent = category_stack[-1] if category_stack else None

            # Create or get category
            category = self.get_or_create_category(category_name, parent, update_mode)

            if category:
                # Add to stack for potential children
                if len(category_stack) == level:
                    category_stack.append(category)
                else:
                    category_stack = category_stack[:level] + [category]

                categories_processed += 1
                self.stdout.write(f'  {"  " * level}✓ {category_name} (ID: {category.id})')

        # Rebuild MPTT tree structure
        Category.objects.rebuild()

        return categories_processed

    def parse_line(self, line):
        """Parse a line to extract indentation level and category name"""
        # Handle markdown list formats: -, *, +, or numbered lists
        patterns = [
            r'^(\s*)([-*+])\s+(.+)$',  # Unordered lists
            r'^(\s*)\d+\.\s+(.+)$',    # Numbered lists 
            r'^(\s*)(.+)$'             # Plain indented text  
        ]

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 3:  # Unordered list
                    indent, marker, name = match.groups()
                    level = len(indent) // 2  # Assume 2 spaces per level
                    return level, name.strip()
                elif len(match.groups()) == 2:  # Numbered or plain 
                    indent, name = match.groups()
                    level = len(indent) // 2
                    return level, name.strip()

        return None, None

    def get_or_create_category(self, name, parent, update_mode):
        """Create or update a category"""
        try:
            if update_mode:
                category, created = Category.objects.get_or_create(
                    name=name,
                    parent=parent,
                    defaults={'name': name, 'parent': parent}
                )
                if created:
                    self.stdout.write(f'    Created: {name}')
                else:
                    self.stdout.write(f'    Updated: {name}')
                return category
            else:
                # Check if category already exists with same parent 
                existing = Category.objects.filter(name=name, parent=parent).first()
                if existing:
                    self.stdout.write(f'    Exists: {name}')
                    return existing
                else:
                    category = Category.objects.create(name=name, parent=parent)
                    self.stdout.write(f'    Created: {name}')
                    return category
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'    Error creating "{name}": {str(e)}')
            )
            return None
