import csv
import os
from tempfile import NamedTemporaryFile
from typing import List

import requests


class CsvParser:

    def parse(self, filename: str):
        _, extension = os.path.splitext(filename)
        file_format = extension[1:]

        if file_format != "csv":
            raise Exception("File format is not csv")

        if not filename.startswith("http"):
            return self.process_csv(filename)

        with NamedTemporaryFile() as f:
            f.write(requests.get(filename).content)
            f.seek(0)
            return self.process_csv(f.name)

    def process_csv(self, filename: str) -> List[dict]:
        with open(filename, encoding="utf-8-sig") as f:
            data = csv.DictReader(f)
            return list(data)
