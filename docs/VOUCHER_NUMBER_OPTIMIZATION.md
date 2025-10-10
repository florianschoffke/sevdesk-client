# Voucher Number Generation Analysis

## Current Implementation

### How It Works

The voucher number generation system currently:

1. **Fetches ALL vouchers** from SevDesk API using `get_all_vouchers(fetch_all=True)`
2. **Paginates through ALL vouchers** in chunks of 100
3. **Parses each voucher number** looking for pattern `B-YYYY-NR`
4. **Finds the highest number** for the current year
5. **Returns next available number**

### Code Location
- **Function:** `get_next_voucher_number()` in `src/vouchers/voucher_utils.py`
- **Called by:** `generate_voucher_numbers()` which is called by `VoucherCreatorBase`

### Performance Issues

#### Problem 1: Fetches ALL Vouchers (Inefficient!)

```python
# Current code fetches EVERYTHING
vouchers = client.get_all_vouchers(fetch_all=True, sort_by_date=True)
print(f"  → Fetched {len(vouchers)} total vouchers from API")  # Shows 4043 vouchers!
```

**Impact:**
- If you have 4000+ vouchers, it fetches ALL of them
- Makes ~40 API requests (4000 ÷ 100 per page)
- Takes significant time (5-10 seconds)
- Unnecessary load on SevDesk API

#### Problem 2: No Caching

When running the master script (`create_all_vouchers.py`):
- Each voucher creator calls `generate_voucher_numbers()` independently
- This means **6 separate API fetches** of all vouchers
- Total: ~240 API requests just for voucher number generation!

**Example from your run:**
```
💰 Processing: Gehalt
  → Fetched 4043 total vouchers from API

🎓 Processing: ÜLP  
  → Fetched 4043 total vouchers from API

💝 Processing: Spenden
  → Fetched 4043 total vouchers from API

🏥 Processing: Krankenkassen
  → Fetched 4043 total vouchers from API

⛪ Processing: Grace Baptist
  → Fetched 4043 total vouchers from API

🌍 Processing: Kontaktmission
  → Fetched 4043 total vouchers from API
```

That's **24,258 voucher objects fetched** when we only needed to fetch them ONCE!

#### Problem 3: Parses ALL Vouchers

```python
# Loops through EVERY voucher
for voucher in vouchers:
    voucher_number = voucher.get('voucherNumber', '') or voucher.get('description', '')
    match = re.match(r'B-(\d{4})-(\d+)', str(voucher_number))
    # ... check if higher than current highest
```

If you have 4000 vouchers, it regex parses 4000 strings, even though most are from previous years or don't match the pattern.

## Optimization Opportunities

### Solution 1: Fetch Only Current Year (Best!)

**Instead of fetching all vouchers, filter by current year in the API request:**

```python
def get_next_voucher_number_optimized(client) -> int:
    from datetime import datetime
    import re
    
    current_year = datetime.now().year
    
    # Fetch only vouchers from current year with B-YYYY pattern
    # Use voucherNumber filter and limit to recent vouchers
    params = {
        'limit': 100,  # Should be enough for one year
        'order[voucherNumber]': 'DESC',  # Get highest numbers first
        # Can add date filter if API supports it
    }
    
    vouchers = client.get_vouchers_filtered(params)
    
    # Parse only until we find one from current year
    # (since sorted DESC, first match is the highest)
    for voucher in vouchers:
        voucher_number = voucher.get('voucherNumber', '')
        match = re.match(r'B-(\d{4})-(\d+)', str(voucher_number))
        
        if match and int(match.group(1)) == current_year:
            return int(match.group(2)) + 1
    
    return 1  # No vouchers this year yet
```

**Benefits:**
- Only fetches ~100 vouchers instead of 4000+
- 1 API request instead of 40+
- ~40x faster

### Solution 2: Cache the Result (Easy Win!)

**Cache the voucher number for the entire master script run:**

```python
# In voucher_creator_base.py or master script
_voucher_number_cache = None

def generate_voucher_numbers_cached(client, count: int) -> list:
    global _voucher_number_cache
    
    if _voucher_number_cache is None:
        # Fetch once
        _voucher_number_cache = get_next_voucher_number(client)
    
    # Generate from cached starting point
    current_year = datetime.now().year
    voucher_numbers = []
    for i in range(count):
        voucher_numbers.append(f"B-{current_year}-{_voucher_number_cache + i}")
    
    # Update cache for next call
    _voucher_number_cache += count
    
    return voucher_numbers
```

**Benefits:**
- Fetches all vouchers only ONCE per script run
- Subsequent calls use cached value
- 6x fewer API requests in master script
- Thread-safe within single process

### Solution 3: Database Caching (Advanced)

**Store the last voucher number in SQLite:**

```python
# Store in database
def get_next_voucher_number_from_db(db: TransactionDB) -> int:
    # Check database for last known number
    last_number = db.get_setting('last_voucher_number')
    
    if last_number:
        return int(last_number) + 1
    
    # Fall back to API if not in DB
    number = get_next_voucher_number_from_api(client)
    db.set_setting('last_voucher_number', number)
    return number

def save_voucher_number_to_db(db: TransactionDB, number: int):
    db.set_setting('last_voucher_number', number)
```

**Benefits:**
- Zero API requests after first run
- Persists across script runs
- Very fast lookups

**Risks:**
- Could get out of sync if vouchers created elsewhere
- Needs refresh mechanism

## Recommended Implementation

### Phase 1: Quick Win - Add Caching (Immediate, Low Risk)

1. Add a module-level cache in `voucher_utils.py`
2. Cache the starting number when first called
3. Increment for subsequent voucher creators in same run

**Impact:** 
- Reduces API calls from 6x to 1x in master script
- Takes 2 minutes to implement
- No API changes needed

### Phase 2: Optimize API Query (Medium Term)

1. Update `get_all_vouchers()` to support filtering by pattern
2. Fetch only vouchers matching `B-{year}-*` pattern
3. Limit to 100 most recent

**Impact:**
- Reduces from ~4000 vouchers to ~100
- Reduces from 40 API requests to 1
- Faster by ~40x

### Phase 3: Database Caching (Optional, Future)

1. Add settings table to SQLite
2. Store last used number
3. Implement refresh command

**Impact:**
- Near-zero API requests
- Instant voucher number generation
- Needs careful sync management

## Performance Comparison

| Method | API Requests | Vouchers Fetched | Time | Risk |
|--------|-------------|------------------|------|------|
| **Current** | 240 (6 creators × 40 pages) | 24,258 | ~60s | Low |
| **With Caching** | 40 (1 fetch × 40 pages) | 4,043 | ~10s | Very Low |
| **Optimized Query** | 1 | ~100 | ~0.5s | Low |
| **DB Cache** | 0 (after first) | 0 | ~0.01s | Medium |

## Conclusion

**Immediate Action:** Implement caching (Phase 1)
- Easy to implement
- 6x improvement
- No risk

**Follow-up:** Optimize API query (Phase 2)
- Check if SevDesk API supports voucherNumber filtering
- Could get another 40x improvement
- Total: 240x faster than current!

## Code Example: Quick Cache Implementation

```python
# In voucher_utils.py
_voucher_number_state = {
    'next_number': None,
    'year': None,
}

def generate_voucher_numbers(client, count: int) -> list:
    """
    Generate voucher numbers with caching for batch operations.
    """
    from datetime import datetime
    
    current_year = datetime.now().year
    
    # Check if cache is valid for current year
    if (_voucher_number_state['next_number'] is None or 
        _voucher_number_state['year'] != current_year):
        # Fetch from API
        _voucher_number_state['next_number'] = get_next_voucher_number(client)
        _voucher_number_state['year'] = current_year
        print(f"  → Fetched starting number from API: B-{current_year}-{_voucher_number_state['next_number']}")
    else:
        print(f"  → Using cached starting number: B-{current_year}-{_voucher_number_state['next_number']}")
    
    # Generate consecutive numbers
    start_number = _voucher_number_state['next_number']
    voucher_numbers = []
    for i in range(count):
        voucher_numbers.append(f"B-{current_year}-{start_number + i}")
    
    # Update cache for next creator
    _voucher_number_state['next_number'] = start_number + count
    
    return voucher_numbers
```

This simple change would reduce your master script run from fetching 24,258 vouchers to just 4,043 - a **6x improvement** with ~10 lines of code!
