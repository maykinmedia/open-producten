def build_formset_data(form_name, *forms, **extra):
    data = {
        f"{form_name}-TOTAL_FORMS": len(forms),
        f"{form_name}-INITIAL_FORMS": "0",
    } | extra

    for i, form in enumerate(forms):
        for key in form:
            data[f"{form_name}-{i}-{key}"] = form[key]

    return data
