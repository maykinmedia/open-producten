from sys import stdout


def custom_postprocessing_hook(result, generator, request, public):
    """
    DRF Spectacular adds default = [] to the item inside an array on PrimaryKeyRelatedField fields with many=True like

    `onderwerp_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Onderwerp.objects.all(),
        source="onderwerpen",
    )`

    (src/open_producten/producttypen/serializers/producttype.py)

    """

    schemas = result.get("components", {}).get("schemas", {})

    for schema_key, schema in schemas.items():
        properties = schema.get("properties", {})

        for prop_key, prop in properties.items():
            if prop_key.endswith("_ids"):
                stdout.write(f"removed default=[] from {schema_key}.{prop_key}\n")
                items = prop.get("items", {})
                items.pop("default", None)
                items.pop("writeOnly", None)

    return result
