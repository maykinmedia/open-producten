document.addEventListener('DOMContentLoaded', function () {
    const productTypeSelect = document.querySelector('#id_product_type');

    productTypeSelect.onchange = element => {
        const selectedProductType = element.target.value;

        const DataFieldSelects = document.querySelectorAll('select[id^="id_data-"][id$="-field"]');

        const filteredDataFieldSelects = Array.from(DataFieldSelects).filter(element => !element.id.includes('__prefix__'));


        for (const fieldSelect of filteredDataFieldSelects) {

            // reset field select
            fieldSelect.selectedIndex = 0;

            const options = Array.from(fieldSelect.options);

            for (const option of options.slice(1)) {
                if (option.getAttribute("product_type") === selectedProductType) {
                    option.style.display = 'block';
                } else {
                    option.style.display = 'none';
                }
            }
        }
    };
});
