// Sets the dar/light mode based on the browser.
// Copied minimal needed stuff from open-forms

'use strict';
{
    function initTinyMCE(el) {
        if (el.closest('.empty-form') === null) {
            // Don't do empty inlines
            var mce_conf = JSON.parse(el.dataset.mceConf);
            const useDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

            mce_conf = {
                ...mce_conf,
                ...{
                    skin: useDarkMode ? 'oxide-dark' : 'oxide',
                    content_css: useDarkMode ? 'dark' : 'default',
                },
            };

            const id = el.id;

            if (!tinyMCE.get(id)) {
                tinyMCE.init(mce_conf);
            }
        }
    }

    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    function initializeTinyMCE(element, formsetName) {
        Array.from(element.querySelectorAll('.tinymce')).forEach(area => initTinyMCE(area));
    }

    ready(function () {
        // initialize the TinyMCE editors on load
        initializeTinyMCE(document);
    });
}
