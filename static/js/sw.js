/*
 * Service Worker for EastWest Portal Web Push Notifications.
 * This script runs in the background even when the portal tab is closed.
 */

self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.message,
            icon: '/static/img/icon.png', // Add your icon here
            badge: '/static/img/badge.png', // Add your badge icon here
            data: {
                url: data.link || '/'
            },
            vibrate: [100, 50, 100],
            actions: [
                { action: 'view', title: 'View Update' }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    if (event.action === 'view' || !event.action) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});
