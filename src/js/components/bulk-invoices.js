// Bulk Invoices View Component
import { BaseView } from './base-view.js';
import { Toast } from '../utils/toast.js';
import { LoadingManager } from '../utils/loading.js';

export class BulkInvoicesView extends BaseView {
  constructor() {
    super();
    this.apiClient = null;
    this.invoiceBatch = [];
    this.contacts = [];
  }

  async render() {
    this.container = this.createElement('div', 'container');
    this.container.innerHTML = `
      <div class="bulk-invoices-view">
        <!-- Header with navigation -->
        <header class="view-header">
          <div class="header-nav">
            <button id="back-btn" class="btn btn-secondary">← Back to Dashboard</button>
            <h1>Bulk Invoice Creation</h1>
          </div>
          <div class="header-actions">
            <span class="batch-counter">Batch: <span id="batch-count">0</span> invoices</span>
            <button id="create-batch-btn" class="btn btn-primary" disabled>Create All Invoices</button>
          </div>
        </header>

        <!-- Method Selection -->
        <div class="method-selection">
          <h2>Choose Creation Method</h2>
          <div class="method-cards">
            <div class="method-card active" data-method="manual">
              <div class="method-icon">✏️</div>
              <h3>Manual Entry</h3>
              <p>Add invoices one by one</p>
            </div>
            <div class="method-card" data-method="csv">
              <div class="method-icon">📄</div>
              <h3>CSV Import</h3>
              <p>Upload CSV file with invoice data</p>
            </div>
          </div>
        </div>

        <!-- Manual Entry Form -->
        <div id="manual-entry" class="creation-method active">
          <div class="form-section">
            <h3>Add New Invoice</h3>
            <form id="invoice-form" class="invoice-form">
              <div class="form-grid">
                <div class="form-group">
                  <label for="contact-select">Customer</label>
                  <select id="contact-select" required>
                    <option value="">Loading contacts...</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label for="invoice-date">Invoice Date</label>
                  <input type="date" id="invoice-date" required>
                </div>
                
                <div class="form-group">
                  <label for="due-date">Due Date</label>
                  <input type="date" id="due-date" required>
                </div>
                
                <div class="form-group">
                  <label for="invoice-number">Invoice Number</label>
                  <input type="text" id="invoice-number" placeholder="Auto-generated if empty">
                </div>
              </div>

              <!-- Invoice Items -->
              <h4>Invoice Items</h4>
              <div id="invoice-items" class="invoice-items">
                <div class="invoice-item" data-item-index="0">
                  <div class="item-grid">
                    <div class="form-group">
                      <label>Description</label>
                      <input type="text" name="description" placeholder="Item description" required>
                    </div>
                    <div class="form-group">
                      <label>Quantity</label>
                      <input type="number" name="quantity" min="1" value="1" step="0.01" required>
                    </div>
                    <div class="form-group">
                      <label>Unit Price (€)</label>
                      <input type="number" name="price" min="0" step="0.01" placeholder="0.00" required>
                    </div>
                    <div class="form-group">
                      <label>Tax Rate (%)</label>
                      <select name="taxRate">
                        <option value="19">19% (Standard)</option>
                        <option value="7">7% (Reduced)</option>
                        <option value="0">0% (Tax-free)</option>
                      </select>
                    </div>
                    <div class="item-actions">
                      <button type="button" class="btn btn-danger btn-small remove-item-btn" disabled>Remove</button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="button" id="add-item-btn" class="btn btn-secondary">Add Item</button>
                <div class="invoice-total">
                  Total: €<span id="invoice-total">0.00</span>
                </div>
              </div>

              <div class="form-footer">
                <button type="submit" class="btn btn-primary">Add to Batch</button>
                <button type="button" id="clear-form-btn" class="btn btn-secondary">Clear Form</button>
              </div>
            </form>
          </div>
        </div>

        <!-- CSV Import -->
        <div id="csv-import" class="creation-method">
          <div class="form-section">
            <h3>CSV Import</h3>
            <div class="csv-info">
              <p>Upload a CSV file with the following columns:</p>
              <code>contact_name, invoice_date, due_date, description, quantity, price, tax_rate</code>
            </div>
            
            <div class="file-upload">
              <input type="file" id="csv-file" accept=".csv" style="display: none;">
              <button id="upload-btn" class="btn btn-primary">Choose CSV File</button>
              <span id="file-name" class="file-name"></span>
            </div>
            
            <div id="csv-preview" class="csv-preview" style="display: none;">
              <h4>Preview</h4>
              <div class="table-container">
                <table id="csv-table" class="data-table">
                  <thead></thead>
                  <tbody></tbody>
                </table>
              </div>
              <div class="csv-actions">
                <button id="import-csv-btn" class="btn btn-primary">Import to Batch</button>
                <button id="cancel-csv-btn" class="btn btn-secondary">Cancel</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Invoice Batch -->
        <div class="batch-section">
          <h3>Invoice Batch <span class="batch-count-small">(<span id="batch-count-text">0</span>)</span></h3>
          <div id="batch-container" class="batch-container">
            <div class="empty-batch">
              <p>No invoices in batch. Add invoices using the methods above.</p>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  bindEvents() {
    // Navigation
    const backBtn = this.container.querySelector('#back-btn');
    this.addEventListener(backBtn, 'click', this.handleBack.bind(this));

    // Method selection
    const methodCards = this.container.querySelectorAll('.method-card');
    methodCards.forEach(card => {
      this.addEventListener(card, 'click', this.handleMethodChange.bind(this));
    });

    // Manual entry form
    const invoiceForm = this.container.querySelector('#invoice-form');
    this.addEventListener(invoiceForm, 'submit', this.handleFormSubmit.bind(this));

    const addItemBtn = this.container.querySelector('#add-item-btn');
    this.addEventListener(addItemBtn, 'click', this.addInvoiceItem.bind(this));

    const clearFormBtn = this.container.querySelector('#clear-form-btn');
    this.addEventListener(clearFormBtn, 'click', this.clearForm.bind(this));

    // CSV upload
    const uploadBtn = this.container.querySelector('#upload-btn');
    const csvFile = this.container.querySelector('#csv-file');
    this.addEventListener(uploadBtn, 'click', () => csvFile.click());
    this.addEventListener(csvFile, 'change', this.handleFileUpload.bind(this));

    const importCsvBtn = this.container.querySelector('#import-csv-btn');
    this.addEventListener(importCsvBtn, 'click', this.importCsvData.bind(this));

    const cancelCsvBtn = this.container.querySelector('#cancel-csv-btn');
    this.addEventListener(cancelCsvBtn, 'click', this.cancelCsvImport.bind(this));

    // Batch actions
    const createBatchBtn = this.container.querySelector('#create-batch-btn');
    this.addEventListener(createBatchBtn, 'click', this.createBatchInvoices.bind(this));

    // Dynamic events for invoice items
    this.bindInvoiceItemEvents();
  }

  bindInvoiceItemEvents() {
    const itemsContainer = this.container.querySelector('#invoice-items');
    
    // Price calculation
    this.addEventListener(itemsContainer, 'input', (e) => {
      if (e.target.matches('input[name="quantity"], input[name="price"]')) {
        this.calculateInvoiceTotal();
      }
    });

    // Remove item buttons
    this.addEventListener(itemsContainer, 'click', (e) => {
      if (e.target.matches('.remove-item-btn')) {
        this.removeInvoiceItem(e.target.closest('.invoice-item'));
      }
    });
  }

  async onShow() {
    // Get app instance and API client
    const app = window.sevdeskApp;
    if (app) {
      this.apiClient = app.getApiClient();
      
      // Load contacts and batch
      await this.loadContacts();
      this.loadBatch();
      
      // Set default dates
      const today = new Date().toISOString().split('T')[0];
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + 30);
      
      this.container.querySelector('#invoice-date').value = today;
      this.container.querySelector('#due-date').value = dueDate.toISOString().split('T')[0];
    }
  }

  async loadContacts() {
    try {
      if (!this.apiClient) return;
      
      LoadingManager.show('Loading contacts...');
      this.contacts = await this.apiClient.getContacts();
      
      const contactSelect = this.container.querySelector('#contact-select');
      contactSelect.innerHTML = '<option value="">Select a customer...</option>';
      
      this.contacts.forEach(contact => {
        const option = document.createElement('option');
        option.value = contact.id;
        option.textContent = contact.name || `${contact.familyname} ${contact.surename}`.trim();
        contactSelect.appendChild(option);
      });
      
    } catch (error) {
      console.error('Failed to load contacts:', error);
      Toast.error('Failed to load contacts');
    } finally {
      LoadingManager.hide();
    }
  }

  loadBatch() {
    this.invoiceBatch = JSON.parse(localStorage.getItem('invoice_batch') || '[]');
    this.updateBatchDisplay();
  }

  saveBatch() {
    localStorage.setItem('invoice_batch', JSON.stringify(this.invoiceBatch));
    this.updateBatchDisplay();
  }

  updateBatchDisplay() {
    const batchCount = this.container.querySelector('#batch-count');
    const batchCountText = this.container.querySelector('#batch-count-text');
    const createBatchBtn = this.container.querySelector('#create-batch-btn');
    const batchContainer = this.container.querySelector('#batch-container');
    
    const count = this.invoiceBatch.length;
    batchCount.textContent = count;
    batchCountText.textContent = count;
    
    createBatchBtn.disabled = count === 0;
    
    if (count === 0) {
      batchContainer.innerHTML = '<div class="empty-batch"><p>No invoices in batch. Add invoices using the methods above.</p></div>';
    } else {
      this.renderBatchItems(batchContainer);
    }
  }

  renderBatchItems(container) {
    container.innerHTML = this.invoiceBatch.map((invoice, index) => `
      <div class="batch-item" data-index="${index}">
        <div class="batch-item-header">
          <h4>${invoice.contactName}</h4>
          <div class="batch-item-actions">
            <button class="btn btn-danger btn-small remove-batch-item" data-index="${index}">Remove</button>
          </div>
        </div>
        <div class="batch-item-details">
          <p><strong>Date:</strong> ${invoice.invoiceDate} | <strong>Due:</strong> ${invoice.dueDate}</p>
          <p><strong>Items:</strong> ${invoice.items.length} | <strong>Total:</strong> €${invoice.total.toFixed(2)}</p>
        </div>
      </div>
    `).join('');
    
    // Bind remove events
    container.querySelectorAll('.remove-batch-item').forEach(btn => {
      this.addEventListener(btn, 'click', (e) => {
        const index = parseInt(e.target.dataset.index);
        this.invoiceBatch.splice(index, 1);
        this.saveBatch();
      });
    });
  }

  handleBack() {
    const app = window.sevdeskApp;
    if (app) {
      app.getRouter().navigate('/dashboard');
    }
  }

  handleMethodChange(event) {
    const method = event.currentTarget.dataset.method;
    
    // Update active method card
    this.container.querySelectorAll('.method-card').forEach(card => {
      card.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    // Show/hide method sections
    this.container.querySelectorAll('.creation-method').forEach(section => {
      section.classList.remove('active');
    });
    this.container.querySelector(`#${method === 'manual' ? 'manual-entry' : 'csv-import'}`).classList.add('active');
  }

  addInvoiceItem() {
    const itemsContainer = this.container.querySelector('#invoice-items');
    const itemIndex = itemsContainer.children.length;
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'invoice-item';
    itemDiv.dataset.itemIndex = itemIndex;
    itemDiv.innerHTML = `
      <div class="item-grid">
        <div class="form-group">
          <label>Description</label>
          <input type="text" name="description" placeholder="Item description" required>
        </div>
        <div class="form-group">
          <label>Quantity</label>
          <input type="number" name="quantity" min="1" value="1" step="0.01" required>
        </div>
        <div class="form-group">
          <label>Unit Price (€)</label>
          <input type="number" name="price" min="0" step="0.01" placeholder="0.00" required>
        </div>
        <div class="form-group">
          <label>Tax Rate (%)</label>
          <select name="taxRate">
            <option value="19">19% (Standard)</option>
            <option value="7">7% (Reduced)</option>
            <option value="0">0% (Tax-free)</option>
          </select>
        </div>
        <div class="item-actions">
          <button type="button" class="btn btn-danger btn-small remove-item-btn">Remove</button>
        </div>
      </div>
    `;
    
    itemsContainer.appendChild(itemDiv);
    this.updateRemoveButtons();
  }

  removeInvoiceItem(itemElement) {
    itemElement.remove();
    this.updateRemoveButtons();
    this.calculateInvoiceTotal();
  }

  updateRemoveButtons() {
    const items = this.container.querySelectorAll('.invoice-item');
    items.forEach((item, index) => {
      const removeBtn = item.querySelector('.remove-item-btn');
      removeBtn.disabled = items.length === 1;
    });
  }

  calculateInvoiceTotal() {
    const items = this.container.querySelectorAll('.invoice-item');
    let total = 0;
    
    items.forEach(item => {
      const quantity = parseFloat(item.querySelector('input[name="quantity"]').value) || 0;
      const price = parseFloat(item.querySelector('input[name="price"]').value) || 0;
      const taxRate = parseFloat(item.querySelector('select[name="taxRate"]').value) || 0;
      
      const subtotal = quantity * price;
      const taxAmount = subtotal * (taxRate / 100);
      total += subtotal + taxAmount;
    });
    
    this.container.querySelector('#invoice-total').textContent = total.toFixed(2);
  }

  handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const contactId = formData.get('contact-select') || this.container.querySelector('#contact-select').value;
    const contactName = this.container.querySelector('#contact-select option:checked').textContent;
    
    // Collect invoice items
    const items = [];
    const itemElements = this.container.querySelectorAll('.invoice-item');
    
    itemElements.forEach(item => {
      const description = item.querySelector('input[name="description"]').value;
      const quantity = parseFloat(item.querySelector('input[name="quantity"]').value);
      const price = parseFloat(item.querySelector('input[name="price"]').value);
      const taxRate = parseFloat(item.querySelector('select[name="taxRate"]').value);
      
      if (description && quantity && price >= 0) {
        items.push({ description, quantity, price, taxRate });
      }
    });
    
    if (items.length === 0) {
      Toast.error('Please add at least one invoice item');
      return;
    }
    
    // Calculate total
    const total = items.reduce((sum, item) => {
      const subtotal = item.quantity * item.price;
      const tax = subtotal * (item.taxRate / 100);
      return sum + subtotal + tax;
    }, 0);
    
    // Add to batch
    const invoice = {
      contactId,
      contactName,
      invoiceDate: this.container.querySelector('#invoice-date').value,
      dueDate: this.container.querySelector('#due-date').value,
      invoiceNumber: this.container.querySelector('#invoice-number').value || null,
      items,
      total
    };
    
    this.invoiceBatch.push(invoice);
    this.saveBatch();
    this.clearForm();
    
    Toast.success(`Invoice added to batch (${this.invoiceBatch.length} total)`);
  }

  clearForm() {
    const form = this.container.querySelector('#invoice-form');
    form.reset();
    
    // Reset to single item
    const itemsContainer = this.container.querySelector('#invoice-items');
    const items = itemsContainer.querySelectorAll('.invoice-item');
    for (let i = 1; i < items.length; i++) {
      items[i].remove();
    }
    
    this.updateRemoveButtons();
    this.calculateInvoiceTotal();
    
    // Reset dates
    const today = new Date().toISOString().split('T')[0];
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 30);
    
    this.container.querySelector('#invoice-date').value = today;
    this.container.querySelector('#due-date').value = dueDate.toISOString().split('T')[0];
  }

  async handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    this.container.querySelector('#file-name').textContent = file.name;
    
    try {
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length < 2) {
        Toast.error('CSV file must have at least a header and one data row');
        return;
      }
      
      const headers = lines[0].split(',').map(h => h.trim());
      const rows = lines.slice(1).map(line => line.split(',').map(cell => cell.trim()));
      
      this.displayCsvPreview(headers, rows);
      
    } catch (error) {
      console.error('Failed to read CSV file:', error);
      Toast.error('Failed to read CSV file');
    }
  }

  displayCsvPreview(headers, rows) {
    const preview = this.container.querySelector('#csv-preview');
    const table = this.container.querySelector('#csv-table');
    
    // Create table header
    const thead = table.querySelector('thead');
    thead.innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    
    // Create table body (show only first 5 rows)
    const tbody = table.querySelector('tbody');
    const displayRows = rows.slice(0, 5);
    tbody.innerHTML = displayRows.map(row => 
      `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
    ).join('');
    
    if (rows.length > 5) {
      tbody.innerHTML += `<tr><td colspan="${headers.length}" class="text-center"><em>... and ${rows.length - 5} more rows</em></td></tr>`;
    }
    
    preview.style.display = 'block';
    this.csvData = { headers, rows };
  }

  importCsvData() {
    if (!this.csvData) return;
    
    const { headers, rows } = this.csvData;
    let imported = 0;
    
    rows.forEach(row => {
      try {
        // Map CSV columns to invoice data
        const invoice = {
          contactName: row[headers.indexOf('contact_name')] || 'Unknown',
          contactId: null, // Will need to be resolved
          invoiceDate: row[headers.indexOf('invoice_date')] || new Date().toISOString().split('T')[0],
          dueDate: row[headers.indexOf('due_date')] || new Date().toISOString().split('T')[0],
          invoiceNumber: null,
          items: [{
            description: row[headers.indexOf('description')] || 'Imported item',
            quantity: parseFloat(row[headers.indexOf('quantity')]) || 1,
            price: parseFloat(row[headers.indexOf('price')]) || 0,
            taxRate: parseFloat(row[headers.indexOf('tax_rate')]) || 19
          }],
          total: 0
        };
        
        // Calculate total
        invoice.total = invoice.items.reduce((sum, item) => {
          const subtotal = item.quantity * item.price;
          const tax = subtotal * (item.taxRate / 100);
          return sum + subtotal + tax;
        }, 0);
        
        this.invoiceBatch.push(invoice);
        imported++;
        
      } catch (error) {
        console.error('Failed to import row:', row, error);
      }
    });
    
    this.saveBatch();
    this.cancelCsvImport();
    
    Toast.success(`Imported ${imported} invoices to batch`);
  }

  cancelCsvImport() {
    this.container.querySelector('#csv-preview').style.display = 'none';
    this.container.querySelector('#csv-file').value = '';
    this.container.querySelector('#file-name').textContent = '';
    this.csvData = null;
  }

  async createBatchInvoices() {
    if (this.invoiceBatch.length === 0) {
      Toast.error('No invoices in batch');
      return;
    }
    
    if (!this.apiClient) {
      Toast.error('API client not available');
      return;
    }
    
    try {
      LoadingManager.show(`Creating ${this.invoiceBatch.length} invoices...`);
      
      const results = {
        success: 0,
        failed: 0,
        errors: []
      };
      
      for (let i = 0; i < this.invoiceBatch.length; i++) {
        const invoice = this.invoiceBatch[i];
        
        try {
          LoadingManager.show(`Creating invoice ${i + 1} of ${this.invoiceBatch.length}...`);
          
          await this.apiClient.createInvoice(invoice);
          results.success++;
          
        } catch (error) {
          console.error('Failed to create invoice:', invoice, error);
          results.failed++;
          results.errors.push({
            invoice: invoice.contactName,
            error: error.message
          });
        }
      }
      
      // Clear batch on success
      if (results.success > 0) {
        this.invoiceBatch = [];
        this.saveBatch();
      }
      
      // Show results
      if (results.failed === 0) {
        Toast.success(`Successfully created ${results.success} invoices!`);
      } else {
        Toast.warning(`Created ${results.success} invoices, ${results.failed} failed`);
        console.log('Failed invoices:', results.errors);
      }
      
    } catch (error) {
      console.error('Batch creation failed:', error);
      Toast.error(`Batch creation failed: ${error.message}`);
    } finally {
      LoadingManager.hide();
    }
  }
}