#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, TextStringObject


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{prefix}{i}.")
    else:
        yield prefix[:-1], obj


def parse_args():
    p = argparse.ArgumentParser(
        description="Fill a PDF form from JSON and flatten for sharing."
    )
    p.add_argument("input_pdf", help="path to the blank fillable PDF")
    p.add_argument("json_file", help="path to the JSON data file")
    p.add_argument("output_pdf", help="path to write the flattened, filled PDF")
    return p.parse_args()


def main():
    args = parse_args()
    data = json.loads(Path(args.json_file).read_text())

    reader = PdfReader(args.input_pdf)
    field_names = list(reader.get_form_text_fields().keys())
    flat = list(flatten(data))

    filled_fields = {}
    for field, (path, val) in zip(field_names, flat):
        if field.lower().startswith("checkbox"):
            state = "Yes" if val else "Off"
            pdf_val = NameObject(f"/{state}")
        else:
            pdf_val = TextStringObject(str(val))
        filled_fields[field] = pdf_val

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        writer.update_page_form_field_values(page, filled_fields)

    writer._root_object["/AcroForm"].update({
        NameObject("/NeedAppearances"): BooleanObject(True)
    })

    out_path = Path(args.output_pdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        writer.write(f)

    print(f"✅ Flattened, filled PDF written to: {out_path}")


if __name__ == "__main__":
    main()
