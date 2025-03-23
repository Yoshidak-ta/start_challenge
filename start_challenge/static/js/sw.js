self.addEventListener("install", (event) => {
  console.log("Service Worker インストール");
  self.skipWaiting(); // 即時有効化
});

self.addEventListener("activate", (event) => {
  console.log("Service Worker アクティブ");
  self.clients.claim();
  console.log("Service Worker はすべてのページを制御しました。");
});

self.addEventListener("push", (event) => {
  console.log("プッシュ通知受信");
  let data = { title: "通知", message: "新しいメッセージがあります。" };
  
  try {
    if (event.data) {
      try {
        data = event.data.json();
      } catch (e) {
        console.warn('受信データがJSONではない', event.data.text());
        data = {title: '通知', message: event.data.text()};
      }
    }
  } catch (error) {
    console.error('プッシュ通知の処理中にエラーが発生しました', error)
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
        body: data.message,
        icon: "/static/icons/notification-icon.png",
        badge: "/static/icons/badge-icon.png", 
        vibrate: [200, 100, 200],
    })
  );
});
