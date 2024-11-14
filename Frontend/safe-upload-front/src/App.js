import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Login';  // Import your Login component
import Home from './Home';  // Import your Home component, if it exists

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Route for home */}
        <Route path="/" element={<Home />} />  {/* This renders your Home component for the root path */}

        {/* Define the route for login */}
        <Route path="/login" element={<Login />} />  {/* Correct usage for React Router v6 */}
      </Routes>
    </Router>
  );
};

export default App;
