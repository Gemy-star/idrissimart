/*
 * Dynamic city dropdown for CustomUserAdmin.
 * When the admin selects a country (ForeignKey → ID), fetches the city list via
 * /content/api/countries/{id}/cities/ and rebuilds the city <select>.
 */
'use strict';
(function () {
    const $ = django.jQuery;

    function buildCitySelect(countryId, currentCity) {
        const $city = $('#id_city');
        if (!$city.length) return;

        if (!countryId) {
            $city.empty().append('<option value="">---------</option>');
            return;
        }

        $city.prop('disabled', true)
            .empty()
            .append('<option value="">جاري التحميل...</option>');

        $.getJSON('/content/api/countries/' + countryId + '/cities/')
            .done(function (data) {
                $city.empty().append('<option value="">--- اختر المدينة ---</option>');
                var cities = data.cities || [];
                var found = false;
                cities.forEach(function (c) {
                    // The endpoint returns objects {name: "..."} or plain strings
                    var name = (typeof c === 'object') ? (c.name || c) : c;
                    var $opt = $('<option>').val(name).text(name);
                    if (name === currentCity) { $opt.prop('selected', true); found = true; }
                    $city.append($opt);
                });
                // If stored city is not in the list, keep it valid
                if (currentCity && !found) {
                    $city.append($('<option>').val(currentCity).text(currentCity).prop('selected', true));
                }
                $city.prop('disabled', false);
            })
            .fail(function () {
                $city.empty().append('<option value="">--- تعذّر التحميل ---</option>');
                $city.prop('disabled', false);
            });
    }

    $(document).ready(function () {
        var $country = $('#id_country');
        var $city    = $('#id_city');
        if (!$country.length || !$city.length) return;

        // On page load, populate cities for the already-selected country
        var initCountry = $country.val();
        var initCity    = $city.val();   // current stored city (text value)
        if (initCountry) {
            buildCitySelect(initCountry, initCity);
        }

        // On country change, reload cities and clear current selection
        $country.on('change', function () {
            buildCitySelect($(this).val(), '');
        });
    });
}());
