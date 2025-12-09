/**
 * Dynamic City Loading
 * Loads cities based on selected country
 */

(function() {
    'use strict';

    // Cache for country codes mapping (id -> code)
    let countryCodesMap = {};

    // Function to load cities for a country
    function loadCities(countryId, cityFieldId, selectedCity = null) {
        const cityField = document.getElementById(cityFieldId || 'id_city');
        if (!cityField || !countryId) {
            return;
        }

        // Show loading state
        cityField.disabled = true;
        cityField.innerHTML = '<option value="">جاري التحميل...</option>';

        // Get country code from our map or from data attribute
        let countryCode = countryCodesMap[countryId];

        if (!countryCode) {
            const countrySelect = document.getElementById('id_country');
            if (countrySelect) {
                const selectedOption = countrySelect.querySelector(`option[value="${countryId}"]`);
                if (selectedOption) {
                    countryCode = selectedOption.getAttribute('data-code');
                }
            }
        }

        if (!countryCode) {
            console.error('Country code not found for ID:', countryId);
            cityField.disabled = false;
            cityField.innerHTML = '<option value="">اختر المدينة</option>';
            return;
        }

        // Fetch cities from API
        fetch(`/content/api/cities/${countryCode}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch cities');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.cities) {
                    // Clear and populate city options
                    cityField.innerHTML = '<option value="">اختر المدينة</option>';

                    data.cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city;
                        option.textContent = city;

                        // Select the previously selected city if provided
                        if (selectedCity && city === selectedCity) {
                            option.selected = true;
                        }

                        cityField.appendChild(option);
                    });

                    cityField.disabled = false;
                } else {
                    throw new Error(data.error || 'No cities found');
                }
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                cityField.innerHTML = '<option value="">خطأ في تحميل المدن</option>';
                cityField.disabled = false;
            });
    }

    // Function to build country codes map from select options
    function buildCountryCodesMap() {
        const countrySelect = document.getElementById('id_country');
        if (!countrySelect) return;

        const options = countrySelect.querySelectorAll('option[value]');
        options.forEach(option => {
            if (option.value) {
                let code = option.getAttribute('data-code');

                // If data-code not set, try to infer from text
                if (!code) {
                    const text = option.textContent.trim();
                    if (text.includes('🇸🇦') || text.includes('السعودية') || text.includes('Saudi')) {
                        code = 'SA';
                    } else if (text.includes('🇪🇬') || text.includes('مصر') || text.includes('Egypt')) {
                        code = 'EG';
                    } else if (text.includes('🇦🇪') || text.includes('الإمارات') || text.includes('UAE')) {
                        code = 'AE';
                    } else if (text.includes('🇰🇼') || text.includes('الكويت') || text.includes('Kuwait')) {
                        code = 'KW';
                    } else if (text.includes('🇶🇦') || text.includes('قطر') || text.includes('Qatar')) {
                        code = 'QA';
                    } else if (text.includes('🇧🇭') || text.includes('البحرين') || text.includes('Bahrain')) {
                        code = 'BH';
                    }

                    if (code) {
                        option.setAttribute('data-code', code);
                    }
                }

                if (code) {
                    countryCodesMap[option.value] = code;
                }
            }
        });
    }

    // Function to setup country change listener
    function setupCountryListener() {
        const countrySelect = document.getElementById('id_country');
        const cityField = document.getElementById('id_city');

        if (!countrySelect || !cityField) {
            return;
        }

        // Build the country codes map
        buildCountryCodesMap();

        // Listen for country changes
        countrySelect.addEventListener('change', function() {
            const countryId = this.value;
            if (countryId) {
                loadCities(countryId, 'id_city');
            } else {
                // Reset city field
                cityField.innerHTML = '<option value="">اختر المدينة</option>';
                cityField.disabled = true;
            }
        });

        // Load cities on page load if country is already selected
        if (countrySelect.value) {
            const currentCity = cityField.value;
            loadCities(countrySelect.value, 'id_city', currentCity);
        } else {
            cityField.disabled = true;
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupCountryListener);
    } else {
        setupCountryListener();
    }

    // Function to initialize with custom field IDs
    function initializeDynamicCities(countryFieldId, cityFieldId) {
        const countrySelect = document.getElementById(countryFieldId);
        const cityField = document.getElementById(cityFieldId);

        if (!countrySelect || !cityField) {
            console.error('Country or city field not found:', countryFieldId, cityFieldId);
            return;
        }

        // Build country codes map from select options
        const options = countrySelect.querySelectorAll('option[value]');
        options.forEach(option => {
            if (option.value) {
                let code = option.value; // In checkout, value is already the code

                // Check if value looks like a country code (2 letters)
                if (code.length === 2) {
                    countryCodesMap[code] = code;
                } else {
                    // Try to get from data-code attribute
                    code = option.getAttribute('data-code');
                    if (code) {
                        countryCodesMap[option.value] = code;
                    } else {
                        // Infer from text
                        const text = option.textContent.trim();
                        if (text.includes('🇸🇦') || text.includes('السعودية') || text.includes('Saudi')) {
                            code = 'SA';
                        } else if (text.includes('🇪🇬') || text.includes('مصر') || text.includes('Egypt')) {
                            code = 'EG';
                        } else if (text.includes('🇦🇪') || text.includes('الإمارات') || text.includes('UAE')) {
                            code = 'AE';
                        } else if (text.includes('🇰🇼') || text.includes('الكويت') || text.includes('Kuwait')) {
                            code = 'KW';
                        } else if (text.includes('🇶🇦') || text.includes('قطر') || text.includes('Qatar')) {
                            code = 'QA';
                        } else if (text.includes('🇧🇭') || text.includes('البحرين') || text.includes('Bahrain')) {
                            code = 'BH';
                        }
                        if (code) {
                            countryCodesMap[option.value] = code;
                        }
                    }
                }
            }
        });

        // Listen for country changes
        countrySelect.addEventListener('change', function() {
            const countryCodeOrId = this.value;
            if (countryCodeOrId) {
                // Get the country code
                const countryCode = countryCodesMap[countryCodeOrId] || countryCodeOrId;
                loadCitiesForCustomFields(countryCode, cityFieldId);
            } else {
                // Reset city field
                cityField.innerHTML = '<option value="">اختر الدولة أولاً</option>';
                cityField.disabled = true;
            }
        });

        // Load cities on page load if country is already selected
        if (countrySelect.value) {
            const countryCode = countryCodesMap[countrySelect.value] || countrySelect.value;
            const currentCity = cityField.value;
            loadCitiesForCustomFields(countryCode, cityFieldId, currentCity);
        } else {
            cityField.disabled = true;
        }
    }

    // Function to load cities for custom field IDs
    function loadCitiesForCustomFields(countryCode, cityFieldId, selectedCity = null) {
        const cityField = document.getElementById(cityFieldId);
        if (!cityField || !countryCode) {
            return;
        }

        // Show loading state
        cityField.disabled = true;
        cityField.innerHTML = '<option value="">جاري التحميل...</option>';

        // Fetch cities from API
        fetch(`/content/api/cities/${countryCode}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch cities');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.cities) {
                    // Clear and populate city options
                    cityField.innerHTML = '<option value="">اختر المدينة</option>';

                    data.cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city;
                        option.textContent = city;

                        // Select the previously selected city if provided
                        if (selectedCity && city === selectedCity) {
                            option.selected = true;
                        }

                        cityField.appendChild(option);
                    });

                    cityField.disabled = false;
                } else {
                    throw new Error(data.error || 'No cities found');
                }
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                cityField.innerHTML = '<option value="">خطأ في تحميل المدن</option>';
                cityField.disabled = false;
            });
    }

    // Export functions for global use if needed
    window.dynamicCities = {
        loadCities: loadCities,
        setupCountryListener: setupCountryListener,
        initializeDynamicCities: initializeDynamicCities
    };

    // Make initializeDynamicCities globally accessible
    window.initializeDynamicCities = initializeDynamicCities;
})();
