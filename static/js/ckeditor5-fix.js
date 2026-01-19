/**
 * CKEditor 5 null value fix
 * Fixes the "can't access property 'toString', t is null" error
 * that occurs when CKEditor config contains null values
 */

// Override the CKEditor initialization to handle null values properly
(function() {
    // Wait for the original script to load
    if (typeof window.initCKEditor5 !== 'undefined') {
        const originalInit = window.initCKEditor5;

        window.initCKEditor5 = function(element) {
            // Patch JSON.parse calls to handle null values
            const originalParse = JSON.parse;
            JSON.parse = function(text, reviver) {
                if (reviver) {
                    // Wrap the reviver to handle null/undefined values
                    const safeReviver = function(key, value) {
                        // Skip null/undefined values for toString operations
                        if (value === null || value === undefined) {
                            return value;
                        }
                        return reviver.call(this, key, value);
                    };
                    return originalParse.call(this, text, safeReviver);
                }
                return originalParse.call(this, text, reviver);
            };

            try {
                return originalInit.call(this, element);
            } finally {
                // Restore original JSON.parse
                JSON.parse = originalParse;
            }
        };
    }
})();
