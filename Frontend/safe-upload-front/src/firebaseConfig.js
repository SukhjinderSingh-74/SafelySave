// firebaseConfig.js
import { initializeApp } from "firebase/app";

const firebaseConfig = {
    apiKey: "AIzaSyCXS6gW5RJlGtgVCb-WMOFx7OENpfPmYQo",
  authDomain: "safelysave-ce984.firebaseapp.com",
  projectId: "safelysave-ce984",
  storageBucket: "safelysave-ce984.appspot.com",
  messagingSenderId: "535853796445",
  appId: "1:535853796445:web:d5b9d138f034fd474151b4",
  measurementId: "G-PENJ98KF0K"
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);

export { firebaseApp };
