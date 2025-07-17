import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx'; // Make sure the path to your App component is correct
import './index.css'; // Make sure your global CSS file is imported

// This is the standard way to render a React app.
// The error "React is not defined" happens if 'import React from 'react';' is missing.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
