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

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  try {
    const app = new App();
    app.init();
    
    // Make app globally accessible for debugging
    if (import.meta.env.DEV) {
      window.sevdeskApp = app;
    }
  } catch (error) {
    console.error('Failed to initialize application:', error);
    document.body.innerHTML = `
      <div class="loading-screen">
        <div style="text-align: center; color: var(--color-danger);">
          <h2>Application Failed to Load</h2>
          <p>Please refresh the page and try again.</p>
          <p style="font-size: 14px; color: var(--color-text-muted); margin-top: 20px;">
            Error: ${error.message}
          </p>
        </div>
      </div>
    `;
  }
});

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