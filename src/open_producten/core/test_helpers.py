def build_formset_data(product_type_id, form_name, *forms):
    data = {
        "product_type": product_type_id,
        f"{form_name}-TOTAL_FORMS": len(forms),
        f"{form_name}-INITIAL_FORMS": "0",
    }

    for i, form in enumerate(forms):
        for key in form:
            data[f"{form_name}-{i}-{key}"] = form[key]

    return data
