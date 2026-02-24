# Quick Setup Guide: Status Sync & Maps

## ✅ What Was Fixed

### 1. Rider Status Sync Issue
- **Problem**: Rider online on app, offline on dashboard
- **Fixed**: Added heartbeat service + API Gateway routing

### 2. Map Configuration  
- **Problem**: Need Google Maps primary, Mapbox fallback
- **Fixed**: Implemented dual provider system with automatic fallback

---

## 🚀 Quick Start

### Backend Setup (5 minutes)

1. **Update environment variables** in `.env`:
```bash
# Add this line
RIDER_STATUS_SERVICE_URL=http://localhost:8800
```

2. **No code changes needed** - API Gateway already updated!

3. **Restart services**:
```bash
docker-compose restart api-gateway
```

### Android App Setup (10 minutes)

#### Step 1: Get API Keys

**Google Maps** (Primary):
1. Go to: https://console.cloud.google.com/
2. Enable "Maps SDK for Android"
3. Create API key
4. Copy your key: `AIzaSy...`

**Mapbox** (Fallback - Optional):
1. Go to: https://account.mapbox.com/
2. Copy access token: `pk.ey...`

#### Step 2: Configure Keys

Create/edit `rider-app/local.properties`:
```properties
# Required for Google Maps (primary)
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_KEY_HERE

# Optional for Mapbox (fallback)  
MAPBOX_ACCESS_TOKEN=YOUR_MAPBOX_TOKEN_HERE
```

#### Step 3: Build & Install

```bash
cd rider-app

# Debug build (development)
./gradlew assembleDebug
./gradlew installDebug

# Or open in Android Studio and click Run
```

---

## 🧪 Testing

### Test 1: Status Sync

1. **Open rider app** → Login
2. **Toggle online** in Profile
3. **Open company dashboard** → Check rider list
4. **✅ Should show**: Rider online in real-time

### Test 2: Maps

1. **Open rider app** → Go to Tracking tab
2. **✅ Should see**: Toast message "Using Google Maps"
3. **If Google fails**: App automatically falls back to Mapbox
4. **If both fail**: Shows OpenStreetMap (basic)

---

## 📱 How It Works

### Status Heartbeat Service

```
Rider App
  ↓
  Opens → Starts RiderStatusService
  ↓
  Every 5 minutes → Sends "online" to API Gateway
  ↓
  API Gateway → Routes to Status Service
  ↓
  Status Service → Updates database
  ↓
  Company Dashboard → Fetches from Status Service
  ↓
  ✅ Shows accurate real-time status
```

### Map Provider Selection

```
1. Try Google Maps
   ↓ (if fails)
2. Try Mapbox  
   ↓ (if fails)
3. Use OSM WebView
```

---

## 🔧 Troubleshooting

### Status not syncing?

**Check logs**:
```bash
# Android app logs
adb logcat | grep "RiderStatusService"

# Backend logs
docker logs anomaah-api-gateway
```

**Common fixes**:
- Restart rider app
- Check API Gateway is running
- Verify STATUS_SERVICE_URL is set
- Check network connectivity

### Maps not loading?

**Error: "Map initialization failed"**
- ✅ Check Google Maps API key in `local.properties`
- ✅ Verify Maps SDK is enabled in Google Cloud
- ✅ Check billing is enabled (required for production)

**Fallback to Mapbox**:
- App automatically tries Mapbox if Google fails
- Add Mapbox token to `local.properties` for better experience

**Emergency OSM**:
- If both fail, app shows OpenStreetMap
- Basic functionality, no API key needed

---

## 💰 Cost Considerations

### Google Maps
- **Free**: Up to $200 credit/month (~28,000 requests)
- **After free tier**: $7 per 1,000 requests
- **Billing required**: Must enable in Google Cloud

### Mapbox
- **Free tier**: 50,000 requests/month
- **After free tier**: $0.50 per 1,000 requests
- **No billing required**: For free tier

### Recommendation
- **Development**: Use free tiers
- **Production**: Google Maps primary (best UX) + Mapbox fallback (cost-effective)

---

## 📊 Monitoring

### Check Rider Status
```bash
# Get single rider
curl https://api.anomaah.gh/status/RIDER_ID

# Get all riders for company
curl https://api.anomaah.gh/status/company/COMPANY_ID
```

### View Android Logs
```bash
# Status updates
adb logcat | grep "RiderStatus"

# Map provider
adb logcat | grep "MapManager"

# All app logs
adb logcat | grep "RiderApp"
```

---

## 🎯 Expected Behavior

### Status Sync ✅
- Rider goes online → Dashboard updates within 5 seconds
- Rider goes offline → Dashboard updates within 5 seconds  
- App in background → Status maintained (heartbeat continues)
- App killed → Status goes offline after 10 minutes
- Heartbeat every 5 minutes keeps status fresh

### Maps ✅
- Google Maps loads (best experience)
- Traffic layer enabled
- Smooth animations
- Falls back to Mapbox if needed
- OSM as emergency fallback

---

## 📝 Files Changed

### Backend
- ✅ `services/api_gateway/main.py` - Added status routes

### Android App
- ✅ `rider-app/build.gradle` - Map dependencies & config
- ✅ `rider-app/src/main/AndroidManifest.xml` - Services & keys
- ✅ `RiderApplication.kt` - Lifecycle management
- ✅ `RiderStatusService.kt` - Heartbeat service (NEW)
- ✅ `TrackingFragment.kt` - Uses MapManager
- ✅ `ui/map/MapProvider.kt` - Interface (NEW)
- ✅ `ui/map/GoogleMapsProvider.kt` - Primary (NEW)
- ✅ `ui/map/MapboxProvider.kt` - Fallback (NEW)
- ✅ `ui/map/MapManager.kt` - Orchestrator (NEW)

---

## 🆘 Need Help?

**Issue**: Rider still showing offline on dashboard
- Solution: Check logs, restart app, verify API Gateway routes

**Issue**: Maps not loading
- Solution: Add API keys to `local.properties`, check billing

**Issue**: Build errors
- Solution: Sync Gradle, clean build, invalidate caches

**Issue**: Background service not working
- Solution: Check battery optimization settings, grant permissions

---

## ✅ Final Checklist

Before deploying to production:

- [ ] Google Maps API key configured
- [ ] Mapbox token configured (optional but recommended)
- [ ] Status service environment variables set
- [ ] API Gateway restarted with new routes
- [ ] Test status sync (rider → dashboard)
- [ ] Test maps (all 3 providers)
- [ ] Check Android app logs for errors
- [ ] Monitor API usage and costs

---

**Status**: ✅ **Ready for Testing & Deployment**

**Next Steps**:
1. Configure API keys
2. Test on development
3. Deploy to production
4. Monitor for 24 hours

Made with ❤️ for smooth operations 🇬🇭
