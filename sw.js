self.addEventListener('push', e => {
  const d = e.data ? e.data.json() : {};
  e.waitUntil(
    self.registration.showNotification(d.title || '멤버스허브', {
      body: d.body || '오늘의 업무를 확인하세요.',
      icon: '/assets/members-symbol.png',
      badge: '/assets/members-symbol.png',
      data: { url: d.url || 'https://sfmi.members-center.co.kr' }
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data.url));
});
