// Main Application Entry Point
import { App } from './app.js';
import { Toast } from './utils/toast.js';
import './utils/polyfills.js';

// Initialize error handling
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  Toast.error('An unexpected error occurred. Please try again.');
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  Toast.error('A network or processing error occurred. Please check your connection and try again.');
});

// Simple, direct initialization
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, showing API key form...');
  
  // Add a small delay to ensure everything is ready
  setTimeout(() => {
  
  // Completely replace the body content to bypass any CSS issues
  document.body.innerHTML = `
    <div id="app" style="min-height: 100vh; display: flex; align-items: center; justify-content: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <div style="background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 500px; width: 100%;">
        <h1 style="margin: 0 0 10px 0; color: #333; text-align: center;">SevDesk API Client</h1>
        <p style="margin: 0 0 30px 0; color: #666; text-align: center;">Enter your SevDesk API key to get started</p>
        
        <form id="auth-form" style="display: flex; flex-direction: column; gap: 20px;">
          <div>
            <label for="api-key" style="display: block; margin-bottom: 8px; font-weight: 500; color: #333;">API Key *</label>
            <input 
              type="password" 
              id="api-key" 
              required 
              placeholder="Enter your SevDesk API key"
              style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box;"
            >
            <small style="color: #666; font-size: 12px; margin-top: 4px; display: block;">Find your API key in SevDesk account settings</small>
          </div>
          
          <div>
            <label for="api-url" style="display: block; margin-bottom: 8px; font-weight: 500; color: #333;">API Base URL</label>
            <input 
              type="url" 
              id="api-url" 
              value="https://my.sevdesk.de/api/v1"
              placeholder="https://my.sevdesk.de/api/v1"
              style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box;"
            >
          </div>
          
          <button 
            type="submit" 
            id="connect-btn" 
            style="background: #007bff; color: white; border: none; padding: 14px 24px; border-radius: 4px; font-size: 16px; font-weight: 500; cursor: pointer;"
          >
            Connect to SevDesk
          </button>
        </form>
        
        <div id="connection-status" style="display: none; text-align: center; margin-top: 20px; color: #007bff;">
          <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #f3f3f3; border-top: 2px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
          Testing connection...
        </div>
        
        <div id="connection-error" style="display: none; margin-top: 20px; padding: 12px; background: #f8d7da; color: #721c24; border-radius: 4px; text-align: center;">
          Connection failed. Please check your API key and try again.
        </div>
      </div>
    </div>
    
    <style>
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      body {
        margin: 0;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
      }
      
      button:hover {
        background: #0056b3 !important;
      }
      
      input:focus {
        outline: none;
        border-color: #007bff !important;
      }
    </style>
  `;
  
  // Bind form submission
  const form = document.getElementById('auth-form');
  form.addEventListener('submit', handleApiKeySubmit);
  
  console.log('API key form should now be visible!');
  
  }, 100); // End setTimeout
});

function showApiKeyForm() {
  const appContainer = document.getElementById('app-container');
  
  appContainer.innerHTML = `
    <div class="container">
      <div class="auth-view">
        <div class="auth-card">
          <div class="logo">
            <h1>SevDesk API Client</h1>
          </div>
          <p class="subtitle">Welcome! To get started, please enter your SevDesk API key.</p>
          
          <form id="auth-form" class="auth-form">
            <div class="form-group">
              <label for="api-key" class="required">API Key</label>
              <input 
                type="password" 
                id="api-key" 
                name="apiKey" 
                class="form-input"
                required 
                placeholder="Enter your SevDesk API key"
              >
              <small class="field-message help">You can find your API key in your SevDesk account settings</small>
            </div>
            
            <div class="form-group">
              <label for="api-url">API Base URL</label>
              <input 
                type="url" 
                id="api-url" 
                name="apiUrl" 
                class="form-input"
                value="https://my.sevdesk.de/api/v1"
                placeholder="https://my.sevdesk.de/api/v1"
              >
              <small class="field-message help">Default SevDesk API endpoint</small>
            </div>
            
            <button type="submit" id="connect-btn" class="btn btn-primary btn-lg">
              Connect to SevDesk
            </button>
          </form>
          
          <div id="connection-status" class="connection-status" style="display: none;">
            <div class="loading-spinner"></div>
            <p>Testing connection...</p>
          </div>
          
          <div id="connection-error" class="connection-error" style="display: none;">
            <p>Connection failed. Please check your API key and try again.</p>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Bind form submission
  const form = document.getElementById('auth-form');
  form.addEventListener('submit', handleApiKeySubmit);
}

async function handleApiKeySubmit(event) {
  event.preventDefault();
  
  const apiKey = document.getElementById('api-key').value.trim();
  const apiUrl = document.getElementById('api-url').value.trim() || 'https://my.sevdesk.de/api/v1';
  
  if (!apiKey) {
    alert('Please enter your API key');
    return;
  }
  
  // Show loading state
  const connectBtn = document.getElementById('connect-btn');
  const statusDiv = document.getElementById('connection-status');
  const errorDiv = document.getElementById('connection-error');
  
  connectBtn.disabled = true;
  connectBtn.textContent = 'Connecting...';
  statusDiv.style.display = 'block';
  errorDiv.style.display = 'none';
  
  try {
    // Test the API key
    const response = await fetch(`${apiUrl}/Contact?limit=1`, {
      headers: {
        'Authorization': apiKey,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data && data.objects !== undefined) {
        // Success! Store credentials and initialize full app
        localStorage.setItem('sevdesk_api_key', apiKey);
        localStorage.setItem('sevdesk_api_url', apiUrl);
        
        // Show success and initialize full app
        statusDiv.innerHTML = '<p style="color: green;">✅ Connection successful! Loading dashboard...</p>';
        
        setTimeout(() => {
          initFullApp();
        }, 1000);
        
        return;
      }
    }
    
    throw new Error('Invalid API response');
    
  } catch (error) {
    console.error('API test failed:', error);
    
    // Show error
    statusDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    errorDiv.innerHTML = `<p style="color: red;">❌ Connection failed: ${error.message}</p>`;
    
    connectBtn.disabled = false;
    connectBtn.textContent = 'Connect to SevDesk';
  }
}

async function initFullApp() {
  try {
    // Import and initialize the full app
    const { App } = await import('./app.js');
    const app = new App();
    await app.init();
    
    // Make app globally accessible
    window.sevdeskApp = app;
    
    console.log('Full application initialized');
  } catch (error) {
    console.error('Failed to initialize full app:', error);
    document.getElementById('connection-error').innerHTML = `
      <p style="color: red;">❌ Failed to load application: ${error.message}</p>
      <button onclick="window.location.reload()" class="btn btn-secondary">Reload</button>
    `;
  }
}

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}