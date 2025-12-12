// Language translations
const translations = {
    lo: {
        home: 'ໜ້າຫຼັກ',
        pos: 'ຂາຍສິນຄ້າ',
        stock: 'ສິນຄ້າເຂົ້າ',
        company: 'ກ່ຽວກັບພວກເຮົາ',
        company_name: 'K-Auto Parts',
        company_desc: 'ລະບົບຄຸ້ມຄອງສິນຄ້າອາໄຫຼ່ລົດທີ່ທັນສະໄໝ',
        quick_links: 'ລິ້ງດ່ວນ',
        contact: 'ຕິດຕໍ່ພວກເຮົາ',
        address: 'ວຽງຈັນ, ສປປ ລາວ',
        copyright: '© 2025 K-Auto Parts. ສະຫງວນລິຂະສິດທັງໝົດ.',
        dashboard: 'ແດັສບອດ',
        products: 'ສິນຄ້າ',
        sales: 'ການຂາຍ',
        reports: 'ລາຍງານ',
        settings: 'ຕັ້ງຄ່າ',
        search: 'ຄົ້ນຫາ',
        add_product: 'ເພີ່ມສິນຄ້າ',
        product_name: 'ຊື່ສິນຄ້າ',
        price: 'ລາຄາ',
        quantity: 'ຈຳນວນ',
        category: 'ປະເພດ',
        actions: 'ການດຳເນີນການ',
        edit: 'ແກ້ໄຂ',
        delete: 'ລຶບ',
        save: 'ບັນທຶກ',
        cancel: 'ຍົກເລີກ',
        total: 'ລວມທັງໝົດ',
        customer: 'ລູກຄ້າ',
        payment_method: 'ວິທີການຊຳລະ',
        cash: 'ເງິນສົດ',
        card: 'ບັດ',
        bank_transfer: 'ໂອນເງິນ',
    },
    th: {
        home: 'หน้าแรก',
        pos: 'ขายสินค้า',
        stock: 'สินค้าเข้า',
        company: 'เกี่ยวกับเรา',
        company_name: 'K-Auto Parts',
        company_desc: 'ระบบจัดการสินค้าอะไหล่รถยนต์ที่ทันสมัย',
        quick_links: 'ลิงก์ด่วน',
        contact: 'ติดต่อเรา',
        address: 'เวียงจันทน์, สปป ลาว',
        copyright: '© 2025 K-Auto Parts. สงวนลิขสิทธิ์ทั้งหมด.',
        dashboard: 'แดชบอร์ด',
        products: 'สินค้า',
        sales: 'การขาย',
        reports: 'รายงาน',
        settings: 'ตั้งค่า',
        search: 'ค้นหา',
        add_product: 'เพิ่มสินค้า',
        product_name: 'ชื่อสินค้า',
        price: 'ราคา',
        quantity: 'จำนวน',
        category: 'ประเภท',
        actions: 'การดำเนินการ',
        edit: 'แก้ไข',
        delete: 'ลบ',
        save: 'บันทึก',
        cancel: 'ยกเลิก',
        total: 'รวมทั้งหมด',
        customer: 'ลูกค้า',
        payment_method: 'วิธีการชำระเงิน',
        cash: 'เงินสด',
        card: 'บัตร',
        bank_transfer: 'โอนเงิน',
    },
    en: {
        home: 'Home',
        pos: 'Point of Sale',
        stock: 'Stock In',
        company: 'About Us',
        company_name: 'K-Auto Parts',
        company_desc: 'Modern Auto Parts Management System',
        quick_links: 'Quick Links',
        contact: 'Contact Us',
        address: 'Vientiane, Lao PDR',
        copyright: '© 2025 K-Auto Parts. All rights reserved.',
        dashboard: 'Dashboard',
        products: 'Products',
        sales: 'Sales',
        reports: 'Reports',
        settings: 'Settings',
        search: 'Search',
        add_product: 'Add Product',
        product_name: 'Product Name',
        price: 'Price',
        quantity: 'Quantity',
        category: 'Category',
        actions: 'Actions',
        edit: 'Edit',
        delete: 'Delete',
        save: 'Save',
        cancel: 'Cancel',
        total: 'Total',
        customer: 'Customer',
        payment_method: 'Payment Method',
        cash: 'Cash',
        card: 'Card',
        bank_transfer: 'Bank Transfer',
    }
};

// Language display names
const languageNames = {
    lo: 'ລາວ',
    th: 'ไทย',
    en: 'English'
};

// Get current language from localStorage or default to 'lo'
function getCurrentLanguage() {
    return localStorage.getItem('language') || 'lo';
}

// Set current language
function setCurrentLanguage(lang) {
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
}

// Update all translated elements
function updatePageLanguage(lang) {
    const elements = document.querySelectorAll('[data-translate]');

    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            // Check if element has input/textarea tag
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });

    // Update current language display
    const currentLangElement = document.getElementById('currentLang');
    if (currentLangElement) {
        currentLangElement.textContent = languageNames[lang];
    }

    // Update HTML lang attribute
    document.documentElement.lang = lang;
}

// Change language function
function changeLanguage(lang) {
    if (translations[lang]) {
        setCurrentLanguage(lang);
        updatePageLanguage(lang);

        // Hide language menu
        const languageMenu = document.getElementById('languageMenu');
        if (languageMenu) {
            languageMenu.classList.add('hidden');
        }

        // Trigger custom event for other scripts to listen to
        const event = new CustomEvent('languageChanged', { detail: { language: lang } });
        document.dispatchEvent(event);

        // Reload page to update server-side translations (optional)
        // location.reload();
    }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    const currentLang = getCurrentLanguage();
    updatePageLanguage(currentLang);
});

// Export functions for global use
window.changeLanguage = changeLanguage;
window.getCurrentLanguage = getCurrentLanguage;
window.translations = translations;
