importScripts("https://www.gstatic.com/firebasejs/9.6.9/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.9/firebase-messaging-compat.js");

// Same config as in HTML
firebase.initializeApp({
  apiKey: "AIzaSyBJBvk-hLQclolkj-jEHRzTBv45ucxG39Y",
  authDomain: "smart-waste-bin-a9ef7.firebaseapp.com",
  databaseURL: "https://smart-waste-bin-a9ef7-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "smart-waste-bin-a9ef7",
  storageBucket: "smart-waste-bin-a9ef7.firebasestorage.app",
  messagingSenderId: "653088937024",
  appId: "1:653088937024:web:361a88d2af81bba537fba5",
  measurementId: "G-V6X6R5SG6B"
});

const messaging = firebase.messaging();

// Handle background notifications
messaging.onBackgroundMessage(function (payload) {
  console.log("[firebase-messaging-sw.js] Background message received:", payload);

  const notificationTitle = payload.notification?.title || "Smart Waste Bin";
  const notificationOptions = {
    body: payload.notification?.body || "Bin status updated.",
    icon: "/static/icons/bin-icon.png" // optional, you can remove or change
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
