/**
 * Price Formatter - Format all prices with comma separator
 * ຈັດຮູບແບບລາຄາທັງໝົດດ້ວຍ comma separator
 */

(function() {
    'use strict';

    /**
     * Format number with comma separator
     * @param {number|string} number - Number to format
     * @returns {string} Formatted number with commas
     */
    function formatNumber(number) {
        // Remove any existing formatting
        const cleanNumber = String(number).replace(/,/g, '');

        // Convert to number and format with commas
        const num = parseFloat(cleanNumber);

        if (isNaN(num)) {
            return number;
        }

        return num.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    /**
     * Format all price elements on the page
     */
    function formatAllPrices() {
        // Find all product price elements
        const priceElements = document.querySelectorAll('.product-price');

        priceElements.forEach(function(priceElement) {
            // Get the text content
            const text = priceElement.textContent || priceElement.innerText;

            // Extract number (before currency symbol)
            const match = text.match(/(\d+(?:\.\d+)?)/);

            if (match) {
                const number = match[1];
                const formattedNumber = formatNumber(number);

                // Replace the number while keeping the currency
                const newText = text.replace(number, formattedNumber);
                priceElement.innerHTML = newText;
            }
        });

        // Also format price-amount elements (for detail page)
        const priceAmountElements = document.querySelectorAll('.price-amount');

        priceAmountElements.forEach(function(element) {
            const number = element.textContent.trim();
            const formattedNumber = formatNumber(number);
            element.textContent = formattedNumber;
        });

        // Format stat-value elements (for dashboard)
        const statValueElements = document.querySelectorAll('.stat-value');

        statValueElements.forEach(function(element) {
            // Skip if it's not a pure number (e.g., contains text)
            const text = element.textContent.trim();
            const number = text.replace(/,/g, '');

            // Only format if it's a valid number
            if (!isNaN(number) && number !== '') {
                const formattedNumber = formatNumber(number);
                element.textContent = formattedNumber;
            }
        });
    }

    /**
     * Initialize price formatting
     */
    function init() {
        // Format prices when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', formatAllPrices);
        } else {
            // DOM is already ready
            formatAllPrices();
        }

        // Re-format prices when language changes
        document.addEventListener('languageChanged', formatAllPrices);
    }

    // Initialize
    init();

    // Expose formatNumber function globally for other scripts
    window.formatPrice = formatNumber;

})();
