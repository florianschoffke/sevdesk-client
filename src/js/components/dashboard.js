// Dashboard View Component
import { BaseView } from './base-view.js';
import { Toast } from '../utils/toast.js';

export class DashboardView extends BaseView {
  constructor() {
    super();
    this.authManager = null;
  }

  async render() {
    this.container = this.createElement('div', 'container');
    this.container.innerHTML = `
      <div class="dashboard-view">
        <!-- App Header -->
        <header class="app-header">
          <h1>SevDesk API Client</h1>
          <div class="header-actions">
            <span id="connection-status" class="status-indicator">Connected</span>
            <button id="logout-btn" class="btn btn-secondary">Logout</button>
          </div>
        </header>

        <!-- Modules Grid -->
        <div class="modules-grid">
          <div class="module-card" data-module="bulk-invoices">
            <div class="module-icon">📄</div>
            <h3>Create Bulk Invoices</h3>
            <p>Create multiple invoices at once using CSV import or manual entry</p>
            <div class="module-stats">
              <div class="module-stat">
                <span class="module-stat-value" id="invoice-count">0</span>
                <span class="module-stat-label">Created Today</span>
              </div>
              <div class="module-stat">
                <span class="module-stat-value" id="batch-count">0</span>
                <span class="module-stat-label">In Batch</span>
              </div>
            </div>
            <button class="btn btn-primary">Open Module</button>
          </div>
          
          <!-- Future modules -->
          <div class="module-card disabled">
            <div class="module-icon">👥</div>
            <h3>Contact Management</h3>
            <p>Manage customers and suppliers</p>
            <button class="btn btn-secondary" disabled>Coming Soon</button>
          </div>
          
          <div class="module-card disabled">
            <div class="module-icon">📊</div>
            <h3>Reports</h3>
            <p>Generate financial reports and analytics</p>
            <button class="btn btn-secondary" disabled>Coming Soon</button>
          </div>
          
          <div class="module-card disabled">
            <div class="module-icon">📋</div>
            <h3>Document Templates</h3>
            <p>Manage invoice and document templates</p>
            <button class="btn btn-secondary" disabled>Coming Soon</button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h2>Quick Actions</h2>
          <div class="quick-actions-grid">
            <div class="quick-action" data-action="single-invoice">
              <span class="quick-action-icon">⚡</span>
              <div class="quick-action-text">
                <h4 class="quick-action-title">Create Single Invoice</h4>
                <p class="quick-action-description">Quick single invoice creation</p>
              </div>
            </div>
            
            <div class="quick-action" data-action="view-contacts">
              <span class="quick-action-icon">📇</span>
              <div class="quick-action-text">
                <h4 class="quick-action-title">View Contacts</h4>
                <p class="quick-action-description">Browse your customer list</p>
              </div>
            </div>
            
            <div class="quick-action" data-action="api-test">
              <span class="quick-action-icon">🔌</span>
              <div class="quick-action-text">
                <h4 class="quick-action-title">Test API Connection</h4>
                <p class="quick-action-description">Verify your SevDesk connection</p>
              </div>
            </div>
            
            <div class="quick-action" data-action="settings">
              <span class="quick-action-icon">⚙️</span>
              <div class="quick-action-text">
                <h4 class="quick-action-title">Settings</h4>
                <p class="quick-action-description">Configure application settings</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  bindEvents() {
    // Logout button
    const logoutBtn = this.container.querySelector('#logout-btn');
    if (logoutBtn) {
      this.addEventListener(logoutBtn, 'click', this.handleLogout.bind(this));
    }

    // Module cards
    const moduleCards = this.container.querySelectorAll('.module-card:not(.disabled)');
    moduleCards.forEach(card => {
      this.addEventListener(card, 'click', this.handleModuleClick.bind(this));
    });

    // Quick actions
    const quickActions = this.container.querySelectorAll('.quick-action');
    quickActions.forEach(action => {
      this.addEventListener(action, 'click', this.handleQuickAction.bind(this));
    });
  }

  async onShow() {
    // Get app instance and auth manager
    const app = window.sevdeskApp;
    if (app) {
      this.authManager = app.getAuthManager();
      
      // Update connection status
      this.updateConnectionStatus();
      
      // Load dashboard data
      await this.loadDashboardData();
    }
  }

  updateConnectionStatus() {
    const statusIndicator = this.container.querySelector('#connection-status');
    if (statusIndicator && this.authManager) {
      if (this.authManager.isAuthenticated()) {
        statusIndicator.textContent = 'Connected';
        statusIndicator.className = 'status-indicator';
      } else {
        statusIndicator.textContent = 'Disconnected';
        statusIndicator.className = 'status-indicator disconnected';
      }
    }
  }

  async loadDashboardData() {
    try {
      // Load batch count from localStorage
      const batch = JSON.parse(localStorage.getItem('invoice_batch') || '[]');
      const batchCountElement = this.container.querySelector('#batch-count');
      if (batchCountElement) {
        batchCountElement.textContent = batch.length;
      }

      // You could add more dashboard data loading here
      // For example: recent invoices, today's statistics, etc.
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  }

  handleLogout() {
    const app = window.sevdeskApp;
    if (app && this.authManager) {
      this.authManager.logout();
      // The auth manager will emit an event that the app will handle
    }
  }

  handleModuleClick(event) {
    const card = event.currentTarget;
    const module = card.dataset.module;
    
    if (!module || card.classList.contains('disabled')) return;

    const app = window.sevdeskApp;
    if (app) {
      app.getRouter().navigate(`/${module}`);
    }
  }

  async handleQuickAction(event) {
    const action = event.currentTarget;
    const actionType = action.dataset.action;
    
    switch (actionType) {
      case 'single-invoice':
        // Navigate to bulk invoices but in single mode
        const app = window.sevdeskApp;
        if (app) {
          app.getRouter().navigate('/bulk-invoices');
        }
        break;
        
      case 'view-contacts':
        Toast.info('Contact management coming soon!');
        break;
        
      case 'api-test':
        await this.testApiConnection();
        break;
        
      case 'settings':
        Toast.info('Settings panel coming soon!');
        break;
        
      default:
        console.log('Unknown quick action:', actionType);
    }
  }

  async testApiConnection() {
    if (!this.authManager) {
      Toast.error('Authentication manager not available');
      return;
    }

    try {
      Toast.info('Testing API connection...');
      
      // Test the connection
      await this.authManager.validateCredentials();
      
      Toast.success('API connection successful!');
      this.updateConnectionStatus();
      
    } catch (error) {
      console.error('API test failed:', error);
      Toast.error(`API test failed: ${error.message}`);
      
      // Update status
      const statusIndicator = this.container.querySelector('#connection-status');
      if (statusIndicator) {
        statusIndicator.textContent = 'Connection Failed';
        statusIndicator.className = 'status-indicator disconnected';
      }
    }
  }
}