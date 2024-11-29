from dataclasses import dataclass

from django.core.management.base import BaseCommand, CommandError

from open_producten.producttypen.models import (
    UniformeProductNaam as UniformProductNaamModel,
)

from ..parsers import CsvParser


@dataclass
class UniformProductName:
    name: str
    uri: str


class Command(BaseCommand):

    def __init__(self):
        self.help = "Load upn to the database from a given XML/CSV file."
        self.parser = CsvParser()
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            help="The name of the file to be imported.",
        )

    def handle(self, **options):
        filename = options.pop("filename")

        self.stdout.write(f"Importing upn from {filename}...")

        try:
            data = self.parser.parse(filename)
            upn_objects = [
                UniformProductName(name=entry["UniformeProductnaam"], uri=entry["URI"])
                for entry in data
            ]
            created_count = self.load_upl(upn_objects)

        except KeyError as e:
            raise CommandError(f"{str(e)} does not exist in csv.")
        except Exception as e:
            raise CommandError(str(e))

        self.stdout.write(f"Done ({created_count} objects).")

    def load_upl(self, data: list[UniformProductName]) -> int:
        count = 0
        upn_updated_list = []

        for obj in data:
            upn, created = UniformProductNaamModel.objects.update_or_create(
                uri=obj.uri,
                defaults={"naam": obj.name, "is_verwijderd": False},
            )
            upn_updated_list.append(upn.id)

            if created:
                count += 1

        UniformProductNaamModel.objects.exclude(id__in=upn_updated_list).update(
            is_verwijderd=True,
        )
        return count
