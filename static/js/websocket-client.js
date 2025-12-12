/**
 * WebSocket Client for Real-time Inventory Updates
 * K-Auto Parts Management System
 */

class InventoryWebSocket {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
        this.isConnecting = false;
        this.listeners = {
            'product_created': [],
            'product_updated': [],
            'product_sold': [],
            'stock_added': [],
            'connected': [],
            'disconnected': [],
            'error': []
        };
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
            console.log('📡 WebSocket already connected or connecting');
            return;
        }

        this.isConnecting = true;

        // Determine WebSocket protocol (ws:// or wss://)
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/inventory/`;

        console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

        try {
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = (event) => {
                console.log('✅ WebSocket connected successfully');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.emit('connected', event);

                // Send ping to keep connection alive
                this.startHeartbeat();
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('📨 WebSocket message received:', data);

                    // Handle different message types
                    switch(data.type) {
                        case 'product_created':
                            this.emit('product_created', data);
                            this.handleProductUpdate(data);
                            break;
                        case 'product_updated':
                            this.emit('product_updated', data);
                            this.handleProductUpdate(data);
                            break;
                        case 'product_sold':
                            this.emit('product_sold', data);
                            this.handleProductUpdate(data);
                            this.showNotification('ສິນຄ້າຂາຍອອກ', `${data.product.name} - ສະຕັອກເຫຼືອ: ${data.product.quantity}`);
                            break;
                        case 'stock_added':
                            this.emit('stock_added', data);
                            this.handleProductUpdate(data);
                            this.showNotification('ເພີ່ມສິນຄ້າເຂົ້າ', `${data.product.name} - ສະຕັອກ: ${data.product.quantity}`);
                            break;
                        case 'pong':
                            // Heartbeat response
                            break;
                        default:
                            console.warn('Unknown message type:', data.type);
                    }
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };

            this.socket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.emit('error', error);
            };

            this.socket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected:', event.code, event.reason);
                this.isConnecting = false;
                this.stopHeartbeat();
                this.emit('disconnected', event);

                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`🔄 Reconnecting (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => this.connect(), this.reconnectDelay);
                } else {
                    console.error('❌ Max reconnection attempts reached');
                }
            };

        } catch (error) {
            console.error('❌ Failed to create WebSocket:', error);
            this.isConnecting = false;
        }
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        this.stopHeartbeat();
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    /**
     * Send message to WebSocket server
     */
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.warn('⚠️ WebSocket not connected, cannot send message');
        }
    }

    /**
     * Start heartbeat (ping/pong) to keep connection alive
     */
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatInterval = setInterval(() => {
            this.send({ type: 'ping' });
        }, 30000); // Every 30 seconds
    }

    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * Add event listener
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Emit event to all listeners
     */
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    /**
     * Handle product update - refresh UI
     */
    handleProductUpdate(data) {
        const product = data.product;

        // Update product cards in grid
        const productCards = document.querySelectorAll(`[data-product-id="${product.id}"]`);
        productCards.forEach(card => {
            // Update quantity
            const quantityElement = card.querySelector('.product-quantity');
            if (quantityElement) {
                quantityElement.textContent = product.quantity;
            }

            // Update stock status
            const stockElement = card.querySelector('.product-stock');
            if (stockElement) {
                stockElement.textContent = `ສະຕັອກ: ${product.quantity} ຊິ້ນ`;

                // Update stock status color
                stockElement.classList.remove('stock-available', 'stock-low', 'stock-out');
                if (product.quantity > 10) {
                    stockElement.classList.add('stock-available');
                } else if (product.quantity > 0) {
                    stockElement.classList.add('stock-low');
                } else {
                    stockElement.classList.add('stock-out');
                }
            }
        });

        // If on product detail page, update that too
        const currentUrl = window.location.pathname;
        if (currentUrl.includes(`/product/${product.slug}/`)) {
            const quantityElements = document.querySelectorAll('.product-quantity, [data-quantity]');
            quantityElements.forEach(el => {
                el.textContent = product.quantity;
            });
        }
    }

    /**
     * Show notification
     */
    showNotification(title, message) {
        // Check if browser supports notifications
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png'
            });
        }

        // Also show in-page notification
        console.log(`🔔 ${title}: ${message}`);
    }

    /**
     * Request notification permission
     */
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

// Create global instance
window.inventoryWS = new InventoryWebSocket();

// Auto-connect when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing WebSocket connection...');
    window.inventoryWS.connect();
    window.inventoryWS.requestNotificationPermission();
});

// Reconnect when page becomes visible
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && (!window.inventoryWS.socket || window.inventoryWS.socket.readyState !== WebSocket.OPEN)) {
        console.log('👀 Page visible, reconnecting WebSocket...');
        window.inventoryWS.connect();
    }
});

// Disconnect when page is closed
window.addEventListener('beforeunload', () => {
    window.inventoryWS.disconnect();
});
