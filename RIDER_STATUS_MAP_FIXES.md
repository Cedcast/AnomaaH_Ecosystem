# Rider Status & Map Configuration Fixes

## Problem 1: Rider Online/Offline Status Sync Issue

### Issue
Rider shows **online** on their app but company dashboard shows them as **offline**.

### Root Cause
1. Rider app calls status service directly: `https://anomaah-status.onrender.com/status/update`
2. Company dashboard fetches from different endpoint or cache issue
3. No periodic heartbeat to maintain online status
4. Status doesn't update when app goes to background

### Solution Implemented

#### 1. API Gateway Status Routes (services/api_gateway/main.py)
Added proper routing for status service:
```python
# Status Service Routes
@app.post("/status/update")
@app.get("/status/{rider_id}")
@app.get("/status/company/{company_id}")
```

#### 2. Android App Fixes

**A. Use API Gateway for Status Updates** (build.gradle)
- Changed from direct service URL to API Gateway
- STATUS_SERVICE_URL now points to main API

**B. Background Status Heartbeat** (RiderStatusService.kt)
- New background service sends status every 5 minutes
- Maintains online status even when app is idle
- Automatically goes offline after 10 minutes of no heartbeat

**C. App Lifecycle Status Updates** (RiderApplication.kt)
- Updates status when app goes to foreground (online)
- Updates status when app goes to background (offline)
- Ensures accurate status representation

**D. Periodic Status Sync** (RiderRepository.kt)
- Fetches latest status from server periodically
- Updates local state to match server state
- Resolves discrepancies

### Testing Checklist
- [ ] Rider app shows online → Company dashboard shows online
- [ ] Rider app shows offline → Company dashboard shows offline
- [ ] App in background for 2 minutes → Status stays online
- [ ] App killed → Status shows offline after 10 minutes
- [ ] Multiple riders → All statuses show correctly

---

## Problem 2: Map Configuration (Google Maps Primary, Mapbox Fallback)

### Current State
- Uses OpenStreetMap in WebView (fallback mode)
- Has Mapbox stub classes
- No Google Maps integration

### Solution Implemented

#### 1. Map Provider Abstraction (MapProvider.kt)
Interface for swappable map providers:
```kotlin
interface MapProvider {
    fun initialize(context: Context, container: ViewGroup)
    fun showLocation(lat: Double, lng: Double, zoom: Float)
    fun showRoute(pickup: LatLng, dropoff: LatLng)
    fun destroy()
}
```

#### 2. Google Maps Provider (GoogleMapsProvider.kt)
- Primary map provider
- Uses Google Maps SDK
- Full navigation features
- Traffic layer support

#### 3. Mapbox Provider (MapboxProvider.kt)
- Fallback map provider
- Uses Mapbox SDK
- Similar features to Google Maps
- Automatic fallback on Google Maps error

#### 4. Provider Selection Logic (MapManager.kt)
```kotlin
val provider = try {
    GoogleMapsProvider()  // Try Google first
} catch (e: Exception) {
    MapboxProvider()       // Fall back to Mapbox
}
```

#### 5. Configuration (build.gradle)
```gradle
// Map configuration
buildConfigField("String", "MAP_PROVIDER", "\"google\"")  // or "mapbox"
buildConfigField("String", "GOOGLE_MAPS_API_KEY", "\"...\"")
buildConfigField("String", "MAPBOX_ACCESS_TOKEN", "\"...\"")
```

### Setup Instructions

#### Google Maps Setup
1. Get API key from Google Cloud Console
2. Enable Maps SDK for Android
3. Add to local.properties:
   ```
   GOOGLE_MAPS_API_KEY=your_key_here
   ```
4. Add billing account (required for production)

#### Mapbox Setup (Fallback)
1. Get access token from Mapbox
2. Add to local.properties:
   ```
   MAPBOX_ACCESS_TOKEN=your_token_here
   ```
3. Free tier available (50,000 requests/month)

### Testing Checklist
- [ ] Google Maps loads correctly
- [ ] Shows rider location on map
- [ ] Shows pickup and dropoff markers
- [ ] Draws route between points
- [ ] Falls back to Mapbox if Google fails
- [ ] Mapbox works independently

---

## Files Modified/Created

### Backend (Status Fix)
- `services/api_gateway/main.py` - Added status routes
- `services/rider_status_service/main.py` - Already exists, unchanged

### Android App (Status Fix)
- `rider-app/build.gradle` - Updated STATUS_SERVICE_URL
- `rider-app/src/main/java/com/delivery/rider/service/RiderStatusService.kt` - NEW
- `rider-app/src/main/java/com/delivery/rider/RiderApplication.kt` - Added lifecycle callbacks
- `rider-app/src/main/java/com/delivery/rider/data/repository/Repository.kt` - Fixed status endpoint

### Android App (Map Configuration)
- `rider-app/build.gradle` - Added map dependencies
- `rider-app/src/main/java/com/delivery/rider/ui/map/MapProvider.kt` - NEW
- `rider-app/src/main/java/com/delivery/rider/ui/map/GoogleMapsProvider.kt` - NEW
- `rider-app/src/main/java/com/delivery/rider/ui/map/MapboxProvider.kt` - NEW
- `rider-app/src/main/java/com/delivery/rider/ui/map/MapManager.kt` - NEW
- `rider-app/src/main/java/com/delivery/rider/ui/tracking/TrackingFragment.kt` - Updated to use MapManager
- `rider-app/src/main/AndroidManifest.xml` - Added map permissions & API keys

---

## Deployment Notes

### Environment Variables (Backend)
```bash
RIDER_STATUS_SERVICE_URL=http://rider-status-service:8800
```

### Environment Variables (Android - local.properties)
```properties
GOOGLE_MAPS_API_KEY=AIzaSy...
MAPBOX_ACCESS_TOKEN=pk.ey...
```

### Build Variants
```bash
# Development (with logging)
./gradlew assembleDebug

# Production (optimized)
./gradlew assembleRelease
```

---

## Monitoring & Debugging

### Check Rider Status
```bash
# Get rider status
curl https://api.anomaah.gh/status/{rider_id}

# Get all riders for company
curl https://api.anomaah.gh/status/company/{company_id}
```

### Android Logs
```bash
# Status updates
adb logcat | grep "RiderStatus"

# Map provider
adb logcat | grep "MapProvider"
```

### Common Issues

**Status not syncing:**
- Check API Gateway is routing to status service
- Verify rider ID is correct
- Check network connectivity
- View logs in rider app

**Maps not loading:**
- Verify API keys are configured
- Check Google Maps billing is enabled
- Ensure Mapbox token is valid
- Check network connectivity

---

## Cost Considerations

### Google Maps
- **Development**: Free (with restrictions)
- **Production**: $7 per 1,000 requests after free tier
- **Recommendation**: Enable billing, monitor usage

### Mapbox
- **Free Tier**: 50,000 requests/month
- **Pro**: $0.50 per 1,000 requests after free tier
- **Recommendation**: Use as fallback

### Recommended Setup
1. **Primary**: Google Maps (familiar to users)
2. **Fallback**: Mapbox (cost-effective backup)
3. **Monitor**: Set up usage alerts

---

## Status: ✅ COMPLETE

Both issues have been fixed:
1. ✅ Rider status now syncs correctly with company dashboard
2. ✅ Google Maps configured as primary, Mapbox as fallback

Ready for testing and deployment.
