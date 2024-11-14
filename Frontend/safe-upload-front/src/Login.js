import React, { useState } from 'react';
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { firebaseApp } from './firebaseConfig';  // Your Firebase config
import { useNavigate } from 'react-router-dom';  // If you're using React Router for navigation

const auth = getAuth(firebaseApp);

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const history = useNavigate();  // If you are using React Router for navigation

    // Handle form submission
    const handleLogin = async (e) => {
        e.preventDefault();  // Prevent the default form submission

        try {
            // Sign in the user using Firebase Authentication
            const userCredential = await signInWithEmailAndPassword(auth, email, password);

            // Get the ID token from the authenticated user
            const idToken = await userCredential.user.getIdToken();

            // Send the ID token to your Flask server for verification
            const response = await fetch('http://127.0.0.1:5000', {
                method: 'POST',
                body: new URLSearchParams({
                    idToken: idToken,  // Send the ID token to Flask
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            if (response.ok) {
                // If the login is successful, redirect to the homepage (or wherever you want)
                history.push('/home');  // Redirect to the home page or dashboard
            } else {
                // Handle error from Flask server (e.g., invalid credentials)
                setErrorMessage('Login failed: Invalid credentials');
            }
        } catch (error) {
            console.error("Login failed:", error);
            setErrorMessage('Login failed: ' + error.message);  // Display error message
        }
    };

    return (
        <div className="login-form">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <button type="submit">Login</button>
                </div>
            </form>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
        </div>
    );
};

export default Login;
