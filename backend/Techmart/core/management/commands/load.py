import csv
import os
import gc  # Optimization: For manual garbage collection
import psutil  # Optimization: For memory monitoring
from django.db import models
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Supplier, Product, Customer, Transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from datetime import datetime

BATCH_SIZE = 1000  # Optimization: Batch size for bulk operations

class Command(BaseCommand):
    help = "Load CSV data into database models dynamically (handles PK, FK, and datetime normalization)"

    def handle(self, *args, **options):
        # Set the base directory for the CSV files (relative to this script)
        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                '..', '..', 'techmart_data'
            )
        )

        # Map each CSV file to its corresponding Django model
        csv_to_model = {
            'suppliers.csv': Supplier,
            'products.csv': Product,
            'customers.csv': Customer,
            'transactions.csv': Transaction,
        }

        try:
            # Use a single DB transaction for all loads for consistency
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
        # Convert various datetime string formats to Django-aware datetime objects
        if not val:
            return None

        dt = parse_datetime(val)
        if dt:
            return make_aware(dt) if timezone.is_naive(dt) else dt

        # Try several common datetime formats
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

    def log_memory_usage(self, note=""):
        # Print current memory usage to help monitor for leaks or spikes
        process = psutil.Process(os.getpid())
        #rss is amount of ram currently used by python process, and then dividing by (2024 * 1024),
        # converts bytes into memory 
        mem = process.memory_info().rss / (1024 * 1024)
        print(f"[Memory] {note} RSS: {mem:.2f} MB")  # Always print to stdout
        self.stdout.write(self.style.NOTICE(f"[Memory] {note} RSS: {mem:.2f} MB"))

    def load_csv_to_model(self, file_path, model):
        # Optimization: Preload FK caches for Transaction to avoid per-row DB lookups
        fk_caches = {}
        if model == Transaction:
            # Preload all customers and products into dictionaries for fast lookup by ID
            fk_caches['customer'] = {c.id: c for c in Customer.objects.all()}
            fk_caches['product'] = {p.id: p for p in Product.objects.all()}

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            # Use DictReader to read one row at a time as a dict (column_name: value)
            reader = csv.DictReader(csvfile)
            model_fields = {f.name: f for f in model._meta.get_fields()}
            batch = []
            total = 0
            for idx, row in enumerate(reader, 1):
                obj_data = {}

                for col, val in row.items():
                    if val == '':
                        val = None  # Treat empty strings as None (NULL)

                    if col == 'id':
                        # Convert id to integer if present
                        if val is not None:
                            try:
                                obj_data[col] = int(val)
                            except ValueError:
                                raise CommandError(f"Invalid id value '{val}' in CSV for model {model.__name__}")
                        continue

                    # Optimization: Fast FK assignment for Transaction using cache
                    if model == Transaction and col == 'customer_id':
                        # Use preloaded customer cache for FK assignment
                        obj_data['customer'] = fk_caches['customer'].get(int(val)) if val else None
                        continue
                    if model == Transaction and col == 'product_id':
                        # Use preloaded product cache for FK assignment
                        obj_data['product'] = fk_caches['product'].get(int(val)) if val else None
                        continue

                    if col.endswith('_id'):
                        # Handle other foreign keys (for other models)
                        rel_field_name = col[:-3]
                        if rel_field_name in model_fields and isinstance(model_fields[rel_field_name], models.ForeignKey):
                            rel_model = model_fields[rel_field_name].related_model
                            if val is not None:
                                try:
                                    # Query the related object by PK
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
                        # Handle datetime fields with normalization
                        if val is not None and field and isinstance(field, models.DateTimeField):
                            try:
                                obj_data[col] = self.normalize_datetime(val)
                            except Exception as e:
                                raise CommandError(f"Invalid datetime '{val}' for field '{col}': {str(e)}")
                        else:
                            obj_data[col] = val  # Assign other fields as-is

                batch.append(obj_data)
                total += 1

                # Optimization: Bulk insert/update in batches for performance
                if len(batch) >= BATCH_SIZE:
                    self.bulk_upsert(model, batch)
                    batch.clear()
                    gc.collect()  # Optimization: Manual garbage collection
                    # Print memory usage every 5 batches
                    if idx % (BATCH_SIZE * 5) == 0:
                        self.log_memory_usage(f"Processed {idx} rows")

            # Insert any remaining objects in the last batch
            if batch:
                self.bulk_upsert(model, batch)
                batch.clear()
                gc.collect()
                self.log_memory_usage(f"Processed {total} rows (final)")

            print(f"Total {total} rows processed for {model.__name__}")
            self.stdout.write(self.style.SUCCESS(f"Total {total} rows processed for {model.__name__}"))

    def bulk_upsert(self, model, batch):
        # Optimization: Use bulk_create with ignore_conflicts for Django 4.1+
        # Fallback to update_or_create for older Django
        if hasattr(model.objects, "bulk_create"):
            objs = []
            for obj_data in batch:
                # Create model instances for each row in the batch
                if 'id' in obj_data:
                    obj = model(**obj_data)
                    objs.append(obj)
                else:
                    objs.append(model(**obj_data))
            try:
                # Fast bulk insert, ignore conflicts (e.g., duplicate PKs)
                model.objects.bulk_create(objs, ignore_conflicts=True)
            except Exception:
                # Fallback: If bulk_create fails, fall back to update_or_create
                for obj_data in batch:
                    if 'id' in obj_data:
                        model.objects.update_or_create(id=obj_data['id'], defaults=obj_data)
                    else:
                        model.objects.create(**obj_data)
        else:
            # Fallback for very old Django
            for obj_data in batch:
                if 'id' in obj_data:
                    model.objects.update_or_create(id=obj_data['id'], defaults=obj_data)
                else:
                    model.objects.create(**obj_data)