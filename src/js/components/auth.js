// Authentication View Component
import { BaseView } from './base-view.js';
import { Toast } from '../utils/toast.js';

export class AuthView extends BaseView {
  constructor() {
    super();
    this.authForm = null;
  }

  async render() {
    this.container = this.createElement('div', 'container');
    this.container.innerHTML = `
      <div class="auth-view">
        <div class="auth-card">
          <div class="logo">
            <h1>SevDesk API Client</h1>
          </div>
          <p class="subtitle">Welcome! To get started, please configure your API settings.</p>
          
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
            
            <button type="submit" class="btn btn-primary btn-lg">
              Connect to SevDesk
            </button>
          </form>

          <div class="auth-help">
            <h3>Need Help?</h3>
            <p>
              <strong>Finding your API Key:</strong><br>
              1. Log into your SevDesk account<br>
              2. Go to Settings → API<br>
              3. Generate or copy your API key
            </p>
            <p>
              <a href="https://api.sevdesk.de/" target="_blank" rel="noopener">
                View SevDesk API Documentation →
              </a>
            </p>
          </div>
        </div>
      </div>
    `;
  }

  bindEvents() {
    this.authForm = this.container.querySelector('#auth-form');
    if (this.authForm) {
      this.addEventListener(this.authForm, 'submit', this.handleSubmit.bind(this));
    }

    // Real-time validation
    const apiKeyInput = this.container.querySelector('#api-key');
    if (apiKeyInput) {
      this.addEventListener(apiKeyInput, 'input', this.validateApiKey.bind(this));
    }
  }

  async handleSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(this.authForm);
    const apiKey = formData.get('apiKey')?.trim();
    const apiUrl = formData.get('apiUrl')?.trim() || 'https://my.sevdesk.de/api/v1';

    if (!apiKey) {
      Toast.error('Please enter your API key');
      return;
    }

    // Get auth manager from global app instance
    const app = window.sevdeskApp;
    if (!app) {
      Toast.error('Application not initialized');
      return;
    }

    const submitButton = this.authForm.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    try {
      // Show loading state
      submitButton.disabled = true;
      submitButton.textContent = 'Connecting...';
      
      // Attempt authentication
      await app.getAuthManager().authenticate(apiKey, apiUrl);
      
      // Success is handled by the app's event listeners
      
    } catch (error) {
      console.error('Authentication failed:', error);
      Toast.error(`Authentication failed: ${error.message}`);
      
      // Reset button state
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  }

  validateApiKey(event) {
    const input = event.target;
    const value = input.value.trim();
    
    // Remove existing validation messages
    const existingMessage = input.parentNode.querySelector('.field-message.error');
    if (existingMessage) {
      existingMessage.remove();
    }

    if (value.length > 0 && value.length < 10) {
      const errorMessage = this.createElement('small', 'field-message error', 'API key seems too short');
      input.parentNode.appendChild(errorMessage);
    }
  }

  async onShow() {
    // Focus on API key input
    const apiKeyInput = this.container.querySelector('#api-key');
    if (apiKeyInput) {
      setTimeout(() => apiKeyInput.focus(), 100);
    }

    // Check if user is already authenticated
    const app = window.sevdeskApp;
    if (app && app.getAuthManager().isAuthenticated()) {
      Toast.info('Already authenticated, redirecting...');
      setTimeout(() => {
        app.getRouter().navigate('/dashboard');
      }, 1000);
    }
  }
}