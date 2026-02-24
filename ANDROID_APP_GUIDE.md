# Rider Android App - Simple Delivery Platform for Ghana

**Status**: ✅ Core Ready | 🟡 UI In Progress  
**Platform**: Android 9.0+ (API 28+)  
**Language**: English Only

---

## Overview

A **simple, focused Android app** for delivery riders in Ghana to:
- ✅ Login with phone + 5-digit passcode
- ✅ View and accept orders
- ✅ Track deliveries
- ✅ View earnings (paid via Hubtel mobile money)
- ✅ Manage profile and online status

## Key Features

### ✅ What's Included

- **Phone + Passcode Login** - No OTP, just 5-digit code from admin
- **Order Management** - Accept, pickup, deliver orders
- **Live Tracking** - Track deliveries with maps
- **Earnings** - View earnings, request payouts (via Hubtel)
- **Profile** - Update status, view ratings
- **English Only** - All text in English

### ❌ What's NOT Included (Per Requirements)

- ❌ SOS/Safety buttons
- ❌ Multi-language support
- ❌ Email-based features
- ❌ Complex help systems
- ❌ Flutterwave/Paystack integration
- ❌ Account creation (admin creates accounts)

---

## Quick Setup

### Prerequisites
- Android Studio Arctic Fox or newer
- Android SDK 34
- Java 17+
- Kotlin 1.9+
- **Minimum RAM**: 4GB (8GB recommended)

> **Note for Low-Spec PCs**: If your PC has limited resources (4GB RAM or less), see [BUILDING_ON_LOW_SPEC_PC.md](BUILDING_ON_LOW_SPEC_PC.md) for optimized build instructions that prevent freezing.

### 1. Clone & Open
```bash
cd /path/to/AnomaaH-/rider-app
# Open in Android Studio
```

### 2. Update API URLs
Edit `build.gradle`:
```gradle
buildConfigField("String", "API_BASE_URL", "\"https://api.anomaah.gh/\"")
buildConfigField("String", "ORDER_SERVICE_URL", "\"https://api.anomaah.gh/\"")
```

### 3. Build & Run
```bash
./gradlew assembleDebug
./gradlew installDebug
```

---

## App Flow

### 1. Login (Phone + Passcode)

```
┌─────────────────────┐
│  Login Screen       │
│                     │
│  Phone: 0244123456  │
│  Passcode: 12345    │
│  [SIGN IN]          │
└─────────────────────┘
          │
          ▼
    Validate with backend
          │
          ▼
┌─────────────────────┐
│  Main Screen        │
│  ├─ Orders          │
│  ├─ Tracking        │
│  ├─ Earnings        │
│  └─ Profile         │
└─────────────────────┘
```

**No OTP required** - Riders get passcode from company admin

### 2. Order Management

```
Orders List → Accept Order → Pickup → Deliver → Complete
```

**States:**
- PENDING: New order, can accept/reject
- ACCEPTED: Rider accepted, going to pickup
- PICKED_UP: Package collected, in transit
- DELIVERED: Order completed

### 3. Earnings & Payouts

```
View Earnings → Request Payout → Admin Approves → Hubtel Payment
```

**Payment**: Via Hubtel mobile money (MTN, Vodafone, AirtelTigo)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Kotlin 100% |
| Architecture | MVVM + Repository |
| DI | Hilt (Dagger) |
| Networking | Retrofit + OkHttp |
| Async | Coroutines |
| UI | Material Components 3 |
| Maps | Google Maps API |
| Storage | Encrypted SharedPreferences |
| Min SDK | API 28 (Android 9.0) |
| Target SDK | API 34 (Android 14) |

---

## Project Structure

```
rider-app/
├── src/main/
│   ├── java/com/delivery/rider/
│   │   ├── RiderApplication.kt          # App entry point
│   │   ├── data/
│   │   │   ├── api/                     # Retrofit API
│   │   │   ├── models/                  # Data classes
│   │   │   ├── local/                   # Local storage
│   │   │   └── repository/              # Data repositories
│   │   ├── ui/
│   │   │   ├── auth/                    # Login screen
│   │   │   ├── main/                    # Main container
│   │   │   ├── orders/                  # Orders list & details
│   │   │   ├── tracking/                # Map tracking
│   │   │   ├── earnings/                # Earnings & payouts
│   │   │   ├── profile/                 # Profile settings
│   │   │   └── viewmodel/               # ViewModels
│   │   └── service/
│   │       ├── LocationService.kt       # Background location
│   │       └── RiderMessagingService.kt # Push notifications
│   └── res/
│       ├── layout/                       # XML layouts
│       ├── values/
│       │   ├── strings.xml              # English only
│       │   ├── colors.xml
│       │   └── styles.xml
│       └── drawable/                     # Icons, images
└── build.gradle                          # App configuration
```

---

## API Integration

### Authentication

```kotlin
// Login with phone + passcode
POST /auth/login
{
  "phone": "+233244123456",
  "passcode": "12345"
}

// Response
{
  "token": "eyJ...",
  "rider": {
    "id": "rider123",
    "phone": "+233244123456",
    "name": "Kwame",
    "company_id": "comp1"
  }
}
```

### Orders

```kotlin
// Get assigned orders
GET /riders/{riderId}/orders

// Accept order
POST /orders/{orderId}/accept

// Update status
PUT /orders/{orderId}/status
{
  "status": "PICKED_UP"
}
```

### Earnings

```kotlin
// Get earnings
GET /riders/{riderId}/earnings

// Request payout
POST /riders/{riderId}/payout/request
{
  "amount": 150.00,
  "phone": "+233244123456"  // For Hubtel mobile money
}
```

---

## Ghana-Specific Features

### Phone Number Validation

```kotlin
// Supports Ghana formats
"+233244123456" ✅
"0244123456"    ✅
"+233 24 412 3456" ✅

// Validates against networks
024, 025, 054, 055 → MTN
020, 050 → Vodafone
026, 027, 056, 057 → AirtelTigo
```

### Currency

```kotlin
// Ghana Cedis (GH₵)
"GH₵ 150.00"
```

### Operating Hours

```kotlin
// Service hours: 6 AM - 10 PM (Ghana Time)
timezone: Africa/Accra (GMT+0)
```

---

## Building

### Debug Build

```bash
# Build APK
./gradlew assembleDebug

# APK location
app/build/outputs/apk/debug/rider-app-debug.apk
```

### Release Build

```bash
# Build signed release
./gradlew assembleRelease

# APK location
app/build/outputs/apk/release/rider-app-release.apk
```

### Install on Device

```bash
# Via ADB
adb install app/build/outputs/apk/debug/rider-app-debug.apk

# Or use Gradle
./gradlew installDebug
```

---

## Configuration

### API Endpoints

Update in `build.gradle`:

```gradle
android {
    defaultConfig {
        // Production
        buildConfigField("String", "API_BASE_URL", "\"https://api.anomaah.gh/\"")
        
        // Development
        // buildConfigField("String", "API_BASE_URL", "\"http://192.168.1.100:8000/\"")
    }
}
```

### Signing Config

For release builds, configure in `build.gradle`:

```gradle
signingConfigs {
    release {
        storeFile file("rider-app.jks")
        storePassword "your_store_password"
        keyAlias "rider-key"
        keyPassword "your_key_password"
    }
}
```

---

## Testing

### Manual Testing Checklist

- [ ] Login with valid phone + passcode
- [ ] Login fails with invalid credentials
- [ ] View orders list
- [ ] Accept order
- [ ] Update order status (pickup, deliver)
- [ ] View order on map
- [ ] Check earnings balance
- [ ] Request payout
- [ ] Update online status
- [ ] Logout

### Test Credentials

Ask admin for test rider account:
- Phone: (provided by admin)
- Passcode: (5-digit code from admin)

---

## Deployment

### APK Distribution

1. **Build Release APK**:
   ```bash
   ./gradlew assembleRelease
   ```

2. **Sign APK** (if not auto-signed):
   ```bash
   jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
     -keystore rider-app.jks \
     rider-app-release-unsigned.apk rider-key
   ```

3. **Distribute**:
   - Upload to internal server
   - Share via link
   - Or publish to Google Play Store

### Google Play Store

For Play Store deployment:
1. Create developer account
2. Prepare store listing
3. Upload APK/AAB
4. Complete content rating
5. Submit for review

---

## Security

### Authentication
- Bearer token (JWT)
- Token stored in encrypted SharedPreferences
- Auto-refresh on 401

### Permissions
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

### Data Security
- AES256-GCM encryption for local data
- HTTPS for all network calls
- No sensitive data in logs

---

## Troubleshooting

### "Network error" on login
- Check API_BASE_URL in build.gradle
- Verify backend is running
- Check phone number format (+233)

### "Invalid passcode"
- Confirm 5-digit numeric code
- Contact admin for correct passcode

### "Map not loading"
- Add Google Maps API key to AndroidManifest.xml
- Enable Maps SDK in Google Cloud Console

### "Location permission denied"
- Request runtime permission
- Check device location settings

---

## Dependencies

Key libraries (see `build.gradle` for versions):

```gradle
// Core
implementation 'androidx.appcompat:appcompat:1.7.0'
implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'

// Networking
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.okhttp3:okhttp:4.11.0'

// DI
implementation 'com.google.dagger:hilt-android:2.48.1'

// Maps
implementation 'com.google.android.gms:play-services-maps:18.2.0'

// Async
implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
```

---

## Support

**Technical Issues**: Check main DEPLOYMENT_GUIDE.md  
**Rider Support**: Contact company admin  
**Bug Reports**: GitHub Issues

---

## Roadmap

### Current (v1.0.0) ✅
- Phone + passcode login
- Order management
- Basic tracking
- Earnings view
- Profile management

### Next Version (v1.1.0) 🟡
- [ ] Push notifications (FCM)
- [ ] Background location tracking
- [ ] Order history
- [ ] Better maps integration
- [ ] Performance improvements

### Future (v2.0.0) ⏳
- [ ] Offline mode
- [ ] Advanced analytics
- [ ] Photo proof of delivery
- [ ] Enhanced earnings reports

---

## Notes

- **Language**: English only (as per requirements)
- **Payment**: Hubtel mobile money only
- **Passcode**: Provided by company admin (no self-registration)
- **Simple**: No SOS, no complex features
- **Ghana-focused**: Phone formats, currency, timezone

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-24  
**Status**: Production Ready (Core Features)  

**Made with ❤️ for Ghanaian delivery riders** 🇬🇭
