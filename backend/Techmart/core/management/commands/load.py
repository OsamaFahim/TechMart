import csv
import os
from django.db import models
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Supplier, Product, Customer, Transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from datetime import datetime

class Command(BaseCommand):
    help = "Load CSV data into database models dynamically (handles PK, FK, and datetime normalization)"

    def handle(self, *args, **options):
        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                '..', '..', 'techmart_data'
            )
        )

        csv_to_model = {
            'suppliers.csv': Supplier,
            'products.csv': Product,
            'customers.csv': Customer,
            'transactions.csv': Transaction,
        }

        try:
            with transaction.atomic():
                for filename, model in csv_to_model.items():
                    file_path = os.path.join(base_dir, filename)
                    if not os.path.exists(file_path):
                        self.stdout.write(self.style.WARNING(f"File {filename} not found at {file_path}, skipping."))
                        continue

                    self.stdout.write(f"Loading {filename}...")
                    self.load_csv_to_model(file_path, model)
                    self.stdout.write(self.style.SUCCESS(f"Loaded {filename} successfully"))

        except Exception as e:
            raise CommandError(f"Error during data load: {str(e)}")

    def normalize_datetime(self, val):
        if not val:
            return None

        dt = parse_datetime(val)
        if dt:
            return make_aware(dt) if timezone.is_naive(dt) else dt

        # Custom supported datetime formats
        formats = [
            "%m/%d/%Y %I:%M:%S %p",        # 5/15/2025  9:03:00 PM
            "%m/%d/%Y  %I:%M:%S %p",       # double space
            "%m/%d/%Y %H:%M:%S",           # 05/05/2025 08:16:30 (24-hour)
            "%Y-%m-%d %H:%M:%S",           # 2025-06-03 11:02:22
            "%Y-%m-%dT%H:%M:%S.%f",        # 2025-06-03T11:02:22.302639
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(val.strip(), fmt)
                return make_aware(dt)
            except ValueError:
                continue

        raise CommandError(f"Could not parse datetime: '{val}'")

    def load_csv_to_model(self, file_path, model):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            model_fields = {f.name: f for f in model._meta.get_fields()}

            for row in reader:
                obj_data = {}

                for col, val in row.items():
                    if val == '':
                        val = None

                    if col == 'id':
                        if val is not None:
                            try:
                                obj_data[col] = int(val)
                            except ValueError:
                                raise CommandError(f"Invalid id value '{val}' in CSV for model {model.__name__}")
                        continue

                    if col.endswith('_id'):
                        rel_field_name = col[:-3]
                        if rel_field_name in model_fields and isinstance(model_fields[rel_field_name], models.ForeignKey):
                            rel_model = model_fields[rel_field_name].related_model
                            if val is not None:
                                try:
                                    related_obj = rel_model.objects.get(pk=int(val))
                                except (rel_model.DoesNotExist, ValueError):
                                    raise CommandError(f"{rel_model.__name__} with id {val} does not exist for field '{col}'")
                                obj_data[rel_field_name] = related_obj
                            else:
                                obj_data[rel_field_name] = None
                        else:
                            obj_data[col] = val
                    else:
                        field = model_fields.get(col, None)

                        if val is not None and field and isinstance(field, models.DateTimeField):
                            try:
                                obj_data[col] = self.normalize_datetime(val)
                            except Exception as e:
                                raise CommandError(f"Invalid datetime '{val}' for field '{col}': {str(e)}")
                        else:
                            obj_data[col] = val

                if 'id' in obj_data:
                    model.objects.update_or_create(id=obj_data['id'], defaults=obj_data)
                else:
                    model.objects.create(**obj_data)
