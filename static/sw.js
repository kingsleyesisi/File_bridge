self.addEventListener('push', event => {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: data.icon || '/static/Filebridge.png',
        badge: '/static/Filebridge.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url
        }
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
