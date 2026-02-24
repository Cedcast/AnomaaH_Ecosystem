# Earnings Sync Implementation and Testing Guide

## Problem Identified

The Android rider app was calling `GET /earnings/{rider_id}` but this endpoint didn't exist in the backend, causing the earnings screen to fail.

## Solution Implemented

### 1. Added Earnings Calculation Endpoint

**Location**: `services/order_service/main.py`

**Endpoint**: `GET /earnings/{rider_id}?period=monthly`

**Functionality**:
- Queries all DELIVERED orders for the specified rider
- Groups earnings by date
- Calculates daily breakdown with amount, order count, and distance
- Returns weekly_total, monthly_total, and total_earnings
- Automatically syncs rider.total_earnings with actual delivered orders

**Response Format**:
```json
{
  "success": true,
  "data": {
    "daily": [
      {
        "date": "2024-02-24",
        "amount": 45.50,
        "orders": 3,
        "distance": 12.5,
        "delivery_time": 0
      }
    ],
    "weekly_total": 125.00,
    "monthly_total": 450.00,
    "total_earnings": 1250.00
  }
}
```

### 2. Updated Rider Earnings on Order Delivery

**Location**: `services/order_service/main.py` - `update_order_status()` function

**Change**: When an order status is changed to DELIVERED:
```python
if new_status == OrderStatus.DELIVERED:
    order.delivered_at = datetime.utcnow()
    
    # Update rider's total earnings
    if order.assigned_rider_id:
        rider_rec = db.query(Rider).filter(Rider.id == order.assigned_rider_id).first()
        if rider_rec:
            rider_rec.total_earnings = (rider_rec.total_earnings or 0.0) + order.price_ghs
```

**Impact**: Rider earnings are automatically updated in real-time when they complete deliveries.

### 3. Added API Gateway Routing

**Location**: `services/api_gateway/main.py`

**Route**: `GET /earnings/{rider_id}`

**Functionality**: Proxies earnings requests from the Android app to the order service.

This ensures the Android app (which uses the gateway URL) can access the earnings endpoint.

## Android App Compatibility

The Android app expects:

```kotlin
data class EarningsResponse(
    val daily: List<Earnings>,
    val weeklyTotal: Float,
    val monthlyTotal: Float,
    val totalEarnings: Float
)
```

Our implementation returns exactly this format (with snake_case converted to camelCase by the app's JSON deserializer).

## Testing Checklist

### Backend API Testing

- [ ] **Test 1: Earnings endpoint exists**
  ```bash
  curl http://localhost:8500/earnings/RIDER_ID?period=monthly
  ```
  Expected: 200 OK with earnings data

- [ ] **Test 2: Earnings calculation accuracy**
  - Create test order with price_ghs = 50.00
  - Assign to test rider
  - Mark as DELIVERED
  - Call earnings endpoint
  - Verify: weekly_total, monthly_total, and total_earnings all include the 50.00

- [ ] **Test 3: Rider earnings update on delivery**
  - Check rider.total_earnings before delivery
  - Mark order as DELIVERED
  - Check rider.total_earnings after delivery
  - Verify: increased by order.price_ghs

- [ ] **Test 4: Period filtering**
  - Test with period=daily (today only)
  - Test with period=weekly (last 7 days)
  - Test with period=monthly (last 30 days)
  - Test with period=all (all time)

- [ ] **Test 5: Multiple orders aggregation**
  - Deliver 3 orders on same day (50, 75, 100 GHS)
  - Check daily array has one entry with amount=225.00, orders=3

- [ ] **Test 6: Empty earnings**
  - Call for rider with no delivered orders
  - Verify: Returns empty daily array, all totals = 0.0

- [ ] **Test 7: API Gateway routing**
  ```bash
  curl http://localhost:8000/earnings/RIDER_ID?period=monthly
  ```
  Expected: Same response as direct order service call

### Android App Testing

- [ ] **Test 8: App can fetch earnings**
  - Login as rider
  - Navigate to Earnings screen
  - Verify: No crash, earnings display correctly

- [ ] **Test 9: Earnings sync with backend**
  - Note earnings amount in app
  - Complete a delivery via backend
  - Pull to refresh earnings screen
  - Verify: Amount increased by delivery price

- [ ] **Test 10: Period filter works**
  - Test switching between daily/weekly/monthly views
  - Verify: Totals update correctly

- [ ] **Test 11: Payout request validation**
  - Try requesting payout > available balance
  - Verify: Proper error handling

### Integration Testing

- [ ] **Test 12: End-to-end flow**
  1. Customer books delivery (price: 100 GHS)
  2. Rider accepts order
  3. Rider picks up order
  4. Rider marks in transit
  5. Rider delivers order
  6. Check rider earnings endpoint: +100 GHS
  7. Check rider profile: total_earnings updated
  8. Android app refreshes: shows new earnings

- [ ] **Test 13: Multiple riders**
  - Create 3 riders
  - Assign different orders to each
  - Verify each rider only sees their own earnings

- [ ] **Test 14: Company isolation**
  - Rider from Company A delivers order
  - Rider from Company B queries earnings
  - Verify: No cross-contamination

### Performance Testing

- [ ] **Test 15: Large dataset**
  - Rider with 100+ delivered orders
  - Call earnings endpoint
  - Verify: Response time < 2 seconds

- [ ] **Test 16: Concurrent requests**
  - 10 riders requesting earnings simultaneously
  - Verify: No database locks or timeouts

## Manual Testing Script

```bash
#!/bin/bash
# Quick manual test of earnings functionality

BASE_URL="http://localhost:8500"
RIDER_ID="test-rider-123"

echo "1. Creating test order..."
ORDER_ID=$(curl -s -X POST "$BASE_URL/orders/create" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "test-payment",
    "pickup_address": "123 Main St",
    "dropoff_address": "456 Elm St",
    "distance_km": 5.5,
    "eta_min": 30,
    "price_ghs": 50.00,
    "pickup_lat": 5.6037,
    "pickup_lng": -0.1870,
    "dropoff_lat": 5.6137,
    "dropoff_lng": -0.1970
  }' | jq -r '.data.id')

echo "Order created: $ORDER_ID"

echo "2. Assigning to rider..."
curl -s -X POST "$BASE_URL/orders/$ORDER_ID/assign" \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": "'$RIDER_ID'",
    "company_id": "test-company"
  }'

echo "3. Marking as DELIVERED..."
curl -s -X POST "$BASE_URL/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "DELIVERED"}'

echo "4. Checking earnings..."
curl -s "$BASE_URL/earnings/$RIDER_ID?period=monthly" | jq '.'

echo "Test complete!"
```

## Known Issues and Limitations

1. **Historical Data**: Existing orders before this implementation won't have updated rider earnings. Run a migration script if needed.

2. **Payout History**: The `/payouts/{rider_id}` endpoint still needs implementation in payment service.

3. **Transaction Ledger**: No detailed transaction history yet - just aggregated totals.

4. **Currency**: Hardcoded to GHS - no multi-currency support.

5. **Delivery Time**: The `delivery_time` field in daily earnings is always 0 (not tracked yet).

## Deployment Checklist

- [x] Earnings endpoint implemented in order service
- [x] Earnings auto-update on order delivery
- [x] API gateway routing added
- [x] Response format matches Android app expectations
- [ ] Backend API tests passing
- [ ] Android app tests passing
- [ ] Integration tests passing
- [ ] Performance tests passing
- [ ] Database migration for existing orders (if needed)
- [ ] Monitoring and logging configured
- [ ] Documentation updated

## Critical for Tomorrow's Deployment

### Must Test Before Deploying:

1. **Create a real order and complete the flow** - Ensure earnings update correctly
2. **Test Android app login and earnings screen** - No crashes or blank screens
3. **Verify all calculations are accurate** - Check math on multiple orders
4. **Test error cases** - Invalid rider ID, no orders, etc.
5. **Check production URLs** - Ensure Android app points to correct endpoints

### Quick Smoke Test (5 minutes):

```bash
# 1. Start all services
docker-compose up -d

# 2. Create and complete an order
./scripts/test-earnings.sh

# 3. Check rider app
# - Login as test rider
# - Open earnings screen
# - Verify amount matches backend

# 4. If all pass → Ready to deploy
```

## Rollback Plan

If earnings feature fails in production:

1. **Immediate**: Revert the 3 file changes (order_service/main.py, api_gateway/main.py)
2. **Temporary**: Display static earnings from rider.total_earnings field
3. **Fix Forward**: Add better error handling and retry logic

## Support

For issues:
1. Check logs: `docker-compose logs order_service`
2. Test endpoint directly: `curl http://order-service:8500/earnings/RIDER_ID`
3. Verify database: `SELECT total_earnings FROM riders WHERE id='RIDER_ID'`

---

**Status**: ✅ Implementation Complete  
**Ready for Testing**: Yes  
**Deployment Risk**: Low (backward compatible, new feature)  
**Last Updated**: 2024-02-24
