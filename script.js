// SevDesk API Client - Main JavaScript File

class SevDeskClient {
    constructor() {
        this.apiKey = null;
        this.apiUrl = 'https://my.sevdesk.de/api/v1';
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkStoredCredentials();
        this.setCurrentDate();
    }

    // Event Binding
    bindEvents() {
        // Authentication events
        document.getElementById('auth-form').addEventListener('submit', this.handleAuth.bind(this));
        document.getElementById('logout-btn').addEventListener('click', this.handleLogout.bind(this));

        // Navigation events
        document.querySelector('[data-module="bulk-invoices"]').addEventListener('click', this.showBulkInvoicesView.bind(this));
        document.getElementById('back-to-main').addEventListener('click', this.showMainView.bind(this));

        // Bulk invoice events
        document.getElementById('manual-entry-btn').addEventListener('click', () => this.switchInputMethod('manual'));
        document.getElementById('csv-import-btn').addEventListener('click', () => this.switchInputMethod('csv'));
        
        // Invoice form events
        document.getElementById('add-position').addEventListener('click', this.addPosition.bind(this));
        document.getElementById('invoice-form').addEventListener('submit', this.handleSingleInvoice.bind(this));
        document.getElementById('add-to-batch').addEventListener('click', this.addToBatch.bind(this));
        document.getElementById('create-batch').addEventListener('click', this.createBatchInvoices.bind(this));
        document.getElementById('clear-batch').addEventListener('click', this.clearBatch.bind(this));

        // CSV events
        document.getElementById('csv-file').addEventListener('change', this.handleCSVFile.bind(this));
        document.querySelector('.file-upload-area').addEventListener('click', () => {
            document.getElementById('csv-file').click();
        });
        document.getElementById('process-csv').addEventListener('click', this.processCSV.bind(this));

        // Dynamic position removal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-position')) {
                this.removePosition(e.target);
            }
        });
    }

    // Authentication Methods
    checkStoredCredentials() {
        const storedApiKey = localStorage.getItem('sevdesk_api_key');
        const storedApiUrl = localStorage.getItem('sevdesk_api_url');
        
        if (storedApiKey) {
            this.apiKey = storedApiKey;
            this.apiUrl = storedApiUrl || this.apiUrl;
            this.showMainView();
        }
    }

    async handleAuth(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const apiKey = formData.get('apiKey');
        const apiUrl = formData.get('apiUrl') || this.apiUrl;

        if (!apiKey) {
            this.showError('Please enter your API key');
            return;
        }

        this.showLoading(true);

        try {
            // Test the API connection
            const isValid = await this.testApiConnection(apiKey, apiUrl);
            
            if (isValid) {
                this.apiKey = apiKey;
                this.apiUrl = apiUrl;
                
                // Store credentials
                localStorage.setItem('sevdesk_api_key', apiKey);
                localStorage.setItem('sevdesk_api_url', apiUrl);
                
                this.showMainView();
                this.showSuccess('Successfully connected to SevDesk API!');
            } else {
                this.showError('Invalid API key or connection failed. Please check your credentials.');
            }
        } catch (error) {
            this.showError('Connection failed: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async testApiConnection(apiKey, apiUrl) {
        try {
            const response = await fetch(`${apiUrl}/Contact`, {
                method: 'GET',
                headers: {
                    'Authorization': apiKey,
                    'Content-Type': 'application/json'
                }
            });

            return response.ok;
        } catch (error) {
            console.error('API test failed:', error);
            return false;
        }
    }

    handleLogout() {
        localStorage.removeItem('sevdesk_api_key');
        localStorage.removeItem('sevdesk_api_url');
        this.apiKey = null;
        this.showAuthView();
        this.clearBatch();
    }

    // View Management
    showAuthView() {
        this.hideAllViews();
        document.getElementById('auth-view').classList.add('active');
    }

    showMainView() {
        this.hideAllViews();
        document.getElementById('main-view').classList.add('active');
    }

    showBulkInvoicesView() {
        this.hideAllViews();
        document.getElementById('bulk-invoices-view').classList.add('active');
    }

    hideAllViews() {
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
    }

    // Bulk Invoice Methods
    switchInputMethod(method) {
        // Update button states
        document.getElementById('manual-entry-btn').classList.toggle('active', method === 'manual');
        document.getElementById('csv-import-btn').classList.toggle('active', method === 'csv');
        
        // Show/hide sections
        document.getElementById('manual-entry-section').classList.toggle('active', method === 'manual');
        document.getElementById('csv-import-section').classList.toggle('active', method === 'csv');
    }

    setCurrentDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('invoice-date').value = today;
    }

    addPosition() {
        const container = document.getElementById('positions-container');
        const positionRow = document.createElement('div');
        positionRow.className = 'position-row';
        positionRow.innerHTML = `
            <div class="form-group">
                <label>Description *</label>
                <input type="text" name="description" required placeholder="Item description">
            </div>
            <div class="form-group">
                <label>Quantity *</label>
                <input type="number" name="quantity" required min="1" step="0.01" value="1">
            </div>
            <div class="form-group">
                <label>Price *</label>
                <input type="number" name="price" required min="0" step="0.01" placeholder="0.00">
            </div>
            <div class="form-group">
                <label>Tax Rate %</label>
                <select name="taxRate">
                    <option value="19">19%</option>
                    <option value="7">7%</option>
                    <option value="0">0%</option>
                </select>
            </div>
            <button type="button" class="btn btn-danger remove-position">Remove</button>
        `;
        container.appendChild(positionRow);
    }

    removePosition(button) {
        const positionRow = button.closest('.position-row');
        const container = document.getElementById('positions-container');
        
        // Don't remove if it's the last position
        if (container.children.length > 1) {
            positionRow.remove();
        } else {
            this.showError('At least one position is required');
        }
    }

    // Invoice Processing
    async handleSingleInvoice(e) {
        e.preventDefault();
        
        const invoiceData = this.getInvoiceFormData();
        if (!invoiceData) return;

        this.showLoading(true);

        try {
            const result = await this.createInvoice(invoiceData);
            if (result.success) {
                this.showResults([{
                    success: true,
                    message: `Invoice created successfully! ID: ${result.data.id}`,
                    invoiceNumber: result.data.invoiceNumber
                }]);
                this.resetInvoiceForm();
            } else {
                this.showError('Failed to create invoice: ' + result.error);
            }
        } catch (error) {
            this.showError('Error creating invoice: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    addToBatch() {
        const invoiceData = this.getInvoiceFormData();
        if (!invoiceData) return;

        const batch = this.getBatch();
        batch.push(invoiceData);
        localStorage.setItem('invoice_batch', JSON.stringify(batch));
        
        this.updateBatchPreview();
        this.resetInvoiceForm();
        this.showSuccess('Invoice added to batch!');
    }

    async createBatchInvoices() {
        const batch = this.getBatch();
        if (batch.length === 0) {
            this.showError('No invoices in batch');
            return;
        }

        this.showLoading(true);
        const results = [];

        try {
            for (let i = 0; i < batch.length; i++) {
                try {
                    const result = await this.createInvoice(batch[i]);
                    results.push({
                        success: result.success,
                        message: result.success 
                            ? `Invoice ${i + 1} created successfully! ID: ${result.data.id}`
                            : `Invoice ${i + 1} failed: ${result.error}`,
                        invoiceNumber: result.success ? result.data.invoiceNumber : null
                    });
                } catch (error) {
                    results.push({
                        success: false,
                        message: `Invoice ${i + 1} error: ${error.message}`
                    });
                }
                
                // Small delay to avoid rate limiting
                await this.sleep(200);
            }

            this.showResults(results);
            this.clearBatch();
            
        } catch (error) {
            this.showError('Batch processing failed: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    clearBatch() {
        localStorage.removeItem('invoice_batch');
        this.updateBatchPreview();
    }

    getBatch() {
        return JSON.parse(localStorage.getItem('invoice_batch') || '[]');
    }

    updateBatchPreview() {
        const batch = this.getBatch();
        const batchList = document.getElementById('batch-list');
        const createButton = document.getElementById('create-batch');

        batchList.innerHTML = '';
        
        if (batch.length === 0) {
            batchList.innerHTML = '<p>No invoices in batch</p>';
            createButton.disabled = true;
        } else {
            batch.forEach((invoice, index) => {
                const item = document.createElement('div');
                item.className = 'batch-item';
                item.innerHTML = `
                    <h5>Invoice ${index + 1}</h5>
                    <p><strong>Contact ID:</strong> ${invoice.contact}</p>
                    <p><strong>Date:</strong> ${invoice.invoiceDate}</p>
                    <p><strong>Positions:</strong> ${invoice.invoicePosSave.length}</p>
                    <p><strong>Total:</strong> €${this.calculateTotal(invoice.invoicePosSave).toFixed(2)}</p>
                `;
                batchList.appendChild(item);
            });
            createButton.disabled = false;
        }
    }

    // API Methods
    async createInvoice(invoiceData) {
        try {
            const response = await fetch(`${this.apiUrl}/Invoice/Factory/saveInvoice`, {
                method: 'POST',
                headers: {
                    'Authorization': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(invoiceData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                return {
                    success: true,
                    data: result.objects
                };
            } else {
                return {
                    success: false,
                    error: result.error?.message || 'Unknown error occurred'
                };
            }
        } catch (error) {
            throw new Error('Network error: ' + error.message);
        }
    }

    // CSV Processing
    handleCSVFile(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const csvData = this.parseCSV(event.target.result);
            this.displayCSVPreview(csvData);
            document.getElementById('process-csv').disabled = false;
        };
        reader.readAsText(file);
    }

    parseCSV(text) {
        const lines = text.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            data.push(row);
        }

        return { headers, data };
    }

    displayCSVPreview(csvData) {
        const preview = document.getElementById('csv-preview');
        const table = document.createElement('table');
        table.className = 'csv-table';

        // Headers
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        csvData.headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Data (show first 5 rows)
        const tbody = document.createElement('tbody');
        csvData.data.slice(0, 5).forEach(row => {
            const tr = document.createElement('tr');
            csvData.headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] || '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        preview.innerHTML = `
            <h5>CSV Preview (first 5 rows of ${csvData.data.length} total)</h5>
        `;
        preview.appendChild(table);
    }

    async processCSV() {
        const csvFile = document.getElementById('csv-file').files[0];
        if (!csvFile) {
            this.showError('Please select a CSV file first');
            return;
        }

        const reader = new FileReader();
        reader.onload = async (event) => {
            const csvData = this.parseCSV(event.target.result);
            await this.processCsvData(csvData);
        };
        reader.readAsText(csvFile);
    }

    async processCsvData(csvData) {
        this.showLoading(true);
        const results = [];

        try {
            for (let i = 0; i < csvData.data.length; i++) {
                const row = csvData.data[i];
                
                try {
                    const invoiceData = this.csvRowToInvoiceData(row);
                    const result = await this.createInvoice(invoiceData);
                    
                    results.push({
                        success: result.success,
                        message: result.success 
                            ? `Row ${i + 1} - Invoice created successfully! ID: ${result.data.id}`
                            : `Row ${i + 1} - Failed: ${result.error}`,
                        invoiceNumber: result.success ? result.data.invoiceNumber : null
                    });
                } catch (error) {
                    results.push({
                        success: false,
                        message: `Row ${i + 1} - Error: ${error.message}`
                    });
                }
                
                // Small delay to avoid rate limiting
                await this.sleep(200);
            }

            this.showResults(results);
            
        } catch (error) {
            this.showError('CSV processing failed: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    csvRowToInvoiceData(row) {
        // Expected CSV columns: contactId, invoiceDate, description, quantity, price, taxRate
        return {
            invoice: {
                invoiceType: "RE",
                contact: {
                    id: parseInt(row.contactId),
                    objectName: "Contact"
                },
                invoiceDate: row.invoiceDate,
                status: 100,
                header: "Invoice",
                headText: null,
                footText: null,
                addressName: null,
                currency: "EUR",
                showNet: 1,
                sendType: "VPR"
            },
            invoicePosSave: [{
                objectName: "InvoicePos",
                mapAll: true,
                quantity: parseFloat(row.quantity) || 1,
                price: parseFloat(row.price) || 0,
                name: row.description || "Item",
                unity: {
                    id: 1,
                    objectName: "Unity"
                },
                taxRate: parseFloat(row.taxRate) || 19,
                temporary: false
            }],
            invoicePosDelete: null,
            discountSave: null,
            discountDelete: null
        };
    }

    // Form Data Processing
    getInvoiceFormData() {
        const form = document.getElementById('invoice-form');
        const formData = new FormData(form);
        
        const contactId = parseInt(formData.get('contactId'));
        const invoiceDate = formData.get('invoiceDate');
        const invoiceType = formData.get('invoiceType');
        const currency = formData.get('currency');

        if (!contactId || !invoiceDate) {
            this.showError('Please fill in all required fields');
            return null;
        }

        // Get all positions
        const positions = [];
        const positionRows = document.querySelectorAll('.position-row');
        
        positionRows.forEach(row => {
            const description = row.querySelector('[name="description"]').value;
            const quantity = parseFloat(row.querySelector('[name="quantity"]').value);
            const price = parseFloat(row.querySelector('[name="price"]').value);
            const taxRate = parseFloat(row.querySelector('[name="taxRate"]').value);

            if (description && quantity && price >= 0) {
                positions.push({
                    objectName: "InvoicePos",
                    mapAll: true,
                    quantity: quantity,
                    price: price,
                    name: description,
                    unity: {
                        id: 1,
                        objectName: "Unity"
                    },
                    taxRate: taxRate,
                    temporary: false
                });
            }
        });

        if (positions.length === 0) {
            this.showError('Please add at least one position');
            return null;
        }

        return {
            invoice: {
                invoiceType: invoiceType,
                contact: {
                    id: contactId,
                    objectName: "Contact"
                },
                invoiceDate: invoiceDate,
                status: 100,
                header: "Invoice",
                headText: null,
                footText: null,
                addressName: null,
                currency: currency,
                showNet: 1,
                sendType: "VPR"
            },
            invoicePosSave: positions,
            invoicePosDelete: null,
            discountSave: null,
            discountDelete: null
        };
    }

    resetInvoiceForm() {
        document.getElementById('invoice-form').reset();
        this.setCurrentDate();
        
        // Reset positions to just one
        const container = document.getElementById('positions-container');
        const positions = container.querySelectorAll('.position-row');
        
        // Remove all but the first position
        for (let i = 1; i < positions.length; i++) {
            positions[i].remove();
        }
        
        // Clear the first position
        const firstPosition = container.querySelector('.position-row');
        firstPosition.querySelectorAll('input').forEach(input => {
            if (input.name === 'quantity') {
                input.value = '1';
            } else if (input.name !== 'taxRate') {
                input.value = '';
            }
        });
    }

    // Utility Methods
    calculateTotal(positions) {
        return positions.reduce((total, pos) => {
            return total + (pos.quantity * pos.price);
        }, 0);
    }

    showResults(results) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        resultsContent.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = `result-item ${result.success ? 'success' : 'error'}`;
            item.innerHTML = `
                <strong>${result.success ? '✓' : '✗'}</strong> ${result.message}
                ${result.invoiceNumber ? `<br><small>Invoice Number: ${result.invoiceNumber}</small>` : ''}
            `;
            resultsContent.appendChild(item);
        });
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    showLoading(show) {
        document.getElementById('loading-overlay').classList.toggle('active', show);
    }

    showError(message) {
        // You could implement a more sophisticated notification system here
        alert('Error: ' + message);
    }

    showSuccess(message) {
        // You could implement a more sophisticated notification system here
        alert('Success: ' + message);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SevDeskClient();
});

// Initialize batch preview on page load
document.addEventListener('DOMContentLoaded', () => {
    const client = new SevDeskClient();
    setTimeout(() => {
        client.updateBatchPreview();
    }, 100);
});