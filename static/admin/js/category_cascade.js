/*
 * Cascading category → subcategory selects for Django admin.
 *
 * Mode A  (single `category` FK field):
 *   Injects a virtual "parent category" select before the real one.
 *   The real select is repopulated with the children of whatever parent is chosen.
 *
 * Mode B  (`category` + `subcategory` FK fields, e.g. PaidBanner):
 *   Limits `category` to root entries only.
 *   Repopulates `subcategory` whenever `category` changes.
 */
'use strict';
(function () {
    const $ = django.jQuery;
    const API = '/api/admin/categories/';
    const cache = {};

    /* ── helpers ─────────────────────────────────────────── */

    function fetch(params, cb) {
        const key = JSON.stringify(params);
        if (cache[key]) { cb(cache[key]); return; }
        $.getJSON(API, params)
            .done(function (data) { cache[key] = data; cb(data); })
            .fail(function () { cb({}); });
    }

    function fillSelect(sel, cats, selectedId) {
        sel.empty().append('<option value="">---------</option>');
        (cats || []).forEach(function (c) {
            const opt = $('<option>').val(c.id).text(c.name);
            if (String(c.id) === String(selectedId)) opt.prop('selected', true);
            sel.append(opt);
        });
        sel.trigger('change.select2');   // refresh Select2 if present
    }

    /* Build a labelled <select> row and insert it before `$anchor`. */
    function makeVirtualRow(inputId, labelText, $anchor) {
        const $sel = $('<select>')
            .attr({id: inputId, name: inputId})
            .css({minWidth: '200px', maxWidth: '600px'});
        const $row = $('<div>')
            .addClass('form-row field-' + inputId)
            .css('marginBottom', '8px')
            .append(
                $('<div>').addClass('flex-container').append(
                    $('<label>').attr('for', inputId).text(labelText),
                    $('<div>').addClass('readonly').append($sel)
                )
            );
        $anchor.before($row);
        return $sel;
    }

    /* ── Mode A: single `category` field ─────────────────── */
    function initSingleCategory() {
        const $catRow = $('.field-category');
        const $catSel = $('#id_category');
        if (!$catRow.length || !$catSel.length) return;
        if ($('#id_subcategory').length) return;   // handled by Mode B

        const existingId = $catSel.val();

        /* Inject virtual parent select */
        const $parentSel = makeVirtualRow(
            'id_parent_category_virtual',
            'القسم الرئيسي',
            $catRow
        );

        /* Relabel the real field */
        $catRow.find('label[for="id_category"]').text('القسم الفرعي');

        function loadChildren(parentId, preSelectChildId) {
            if (!parentId) {
                /* No parent chosen → offer root categories in the real select */
                fetch({}, function (data) { fillSelect($catSel, data.categories, null); });
                return;
            }
            fetch({parent_id: parentId}, function (data) {
                const children = data.categories || [];
                if (children.length) {
                    fillSelect($catSel, children, preSelectChildId);
                } else {
                    /* Leaf category — set the real field to the parent itself */
                    $catSel.empty().append(
                        $('<option>').val(parentId)
                            .text($parentSel.find(':selected').text())
                            .prop('selected', true)
                    ).trigger('change.select2');
                }
            });
        }

        /* Load root categories */
        fetch({}, function (data) {
            fillSelect($parentSel, data.categories, null);

            if (existingId) {
                /* Determine whether existing category is root or child */
                $.getJSON(API, {category_id: existingId})
                    .done(function (info) {
                        if (info.parent_id) {
                            $parentSel.val(info.parent_id);
                            loadChildren(info.parent_id, existingId);
                        } else {
                            /* Existing selection is a root — show its children */
                            $parentSel.val(existingId);
                            loadChildren(existingId, null);
                        }
                    });
            } else {
                fillSelect($catSel, [], null);
            }
        });

        $parentSel.on('change', function () {
            loadChildren($(this).val(), null);
        });
    }

    /* ── Mode B: `category` + `subcategory` fields ────────── */
    function initCategorySubcategory() {
        const $catSel    = $('#id_category');
        const $subcatSel = $('#id_subcategory');
        if (!$catSel.length || !$subcatSel.length) return;

        const existingCatId    = $catSel.val();
        const existingSubcatId = $subcatSel.val();

        /* Load only root categories into the category select */
        fetch({}, function (data) {
            fillSelect($catSel, data.categories, existingCatId);

            /* If a category was already selected, load its subcategories */
            if (existingCatId) {
                fetch({parent_id: existingCatId}, function (sub) {
                    fillSelect($subcatSel, sub.categories, existingSubcatId);
                });
            }
        });

        $catSel.on('change', function () {
            const parentId = $(this).val();
            if (parentId) {
                fetch({parent_id: parentId}, function (sub) {
                    fillSelect($subcatSel, sub.categories, null);
                });
            } else {
                fillSelect($subcatSel, [], null);
            }
        });
    }

    /* ── init ─────────────────────────────────────────────── */
    $(function () {
        initCategorySubcategory();   // Mode B first (checks for subcategory field)
        initSingleCategory();        // Mode A (skips if subcategory field present)
    });
})();
