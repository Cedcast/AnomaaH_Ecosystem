# Rider App - Visual Overview

## 📱 App Screenshots & Flow

### 1. Login Screen
```
┌─────────────────────────┐
│   ANOMAAH DELIVERY      │
│   Reliable. Fast.       │
│                         │
│  Phone Number           │
│  ┌───────────────────┐  │
│  │ 0244123456       │  │
│  └───────────────────┘  │
│                         │
│  5-Digit Passcode       │
│  ┌───────────────────┐  │
│  │ •••••            │  │
│  └───────────────────┘  │
│                         │
│  [      SIGN IN      ]  │
│                         │
│  Your company admin     │
│  provides your passcode │
└─────────────────────────┘
```

### 2. Main Screen (Bottom Navigation)
```
┌─────────────────────────┐
│  Welcome, Kwame         │
│  Status: 🟢 Online      │
└─────────────────────────┘

┌─────────────────────────┐
│  Active Orders          │
│                         │
│  📦 Order #12345        │
│  ├─ From: Osu          │
│  ├─ To: Airport        │
│  └─ GH₵ 25.00         │
│                         │
│  📦 Order #12346        │
│  ├─ From: Madina       │
│  ├─ To: Circle         │
│  └─ GH₵ 18.50         │
└─────────────────────────┘

┌─────────────────────────┐
│ [Orders] [Track] [₵] [👤]│
└─────────────────────────┘
```

### 3. Order Details
```
┌─────────────────────────┐
│  ← Order #12345         │
├─────────────────────────┤
│  Status: ASSIGNED       │
│                         │
│  📍 Pickup Location     │
│  Oxford Street, Osu     │
│  Customer: John         │
│  📞 0244567890         │
│                         │
│  📍 Drop-off Location   │
│  Airport Road           │
│  Distance: 8.5 km       │
│  ETA: 25 mins           │
│                         │
│  💰 Delivery Fee        │
│  GH₵ 25.00             │
│                         │
│  [ ACCEPT ORDER ]       │
│  [ REJECT ORDER ]       │
└─────────────────────────┘
```

### 4. Live Tracking
```
┌─────────────────────────┐
│  Live Tracking          │
├─────────────────────────┤
│                         │
│     [  MAP VIEW  ]      │
│    📍 You are here      │
│    🎯 Destination       │
│    ━━━━━━━ Route       │
│                         │
│  Distance: 3.2 km       │
│  ETA: 12 mins           │
│                         │
│  [ MARK PICKED UP ]     │
│  [ START DELIVERY ]     │
│  [ MARK DELIVERED ]     │
└─────────────────────────┘
```

### 5. Earnings
```
┌─────────────────────────┐
│  My Earnings            │
├─────────────────────────┤
│  💰 Total Earnings      │
│     GH₵ 1,250.00       │
│                         │
│  ✅ Available Balance   │
│     GH₵ 350.00         │
│                         │
│  ⏳ Pending Payout      │
│     GH₵ 900.00         │
│                         │
│  [ REQUEST PAYOUT ]     │
│                         │
├─────────────────────────┤
│  Payout History         │
│                         │
│  Jan 20 - GH₵ 500      │
│  Jan 15 - GH₵ 450      │
│  Jan 10 - GH₵ 380      │
└─────────────────────────┘
```

### 6. Profile
```
┌─────────────────────────┐
│  My Profile             │
├─────────────────────────┤
│      👤                 │
│    Kwame Mensah         │
│  +233 24 412 3456       │
│                         │
│  Company: Swift Riders  │
│  Rating: ⭐ 4.8 (125)  │
│  Deliveries: 342        │
│  Bike: Honda CB150      │
│                         │
│  🟢 Status              │
│  [ Online  ] [ Offline ]│
│                         │
│  [ Change Passcode ]    │
│  [ Sign Out ]           │
└─────────────────────────┘
```

## 🔄 Order Flow

```
1. LOGIN
   Phone: 0244123456
   Passcode: 12345
        │
        ▼
2. VIEW ORDERS
   See assigned orders
        │
        ▼
3. ACCEPT ORDER
   Review details, accept
        │
        ▼
4. GO TO PICKUP
   Navigate to pickup location
        │
        ▼
5. MARK PICKED UP
   Confirm package collected
        │
        ▼
6. DELIVER
   Navigate to drop-off
        │
        ▼
7. MARK DELIVERED
   Complete delivery
        │
        ▼
8. EARNINGS UPDATED
   Balance increases
```

## 📊 Tech Components

```
┌────────────────────────────────────┐
│         RiderApplication           │
│         (Hilt Setup)               │
└────────────────┬───────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│  Data  │  │   UI   │  │Service │
│ Layer  │  │ Layer  │  │ Layer  │
└────┬───┘  └───┬────┘  └───┬────┘
     │          │            │
     ▼          ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│API     │  │View    │  │Location│
│Service │  │Models  │  │Service │
│Retrofit│  │LiveData│  │GPS     │
└────────┘  └────────┘  └────────┘
```

## 🎨 UI Components

**Material Design 3**:
- MaterialButton (Sign In, Accept Order)
- CardView (Order cards, Earnings cards)
- BottomNavigationView (Main navigation)
- RecyclerView (Orders list, Payouts list)
- MapView (Google Maps tracking)
- TextInputLayout (Phone, Passcode inputs)

## 🔐 Security Features

```
Login Flow:
  Phone + Passcode
       │
       ▼
  POST /auth/login
       │
       ▼
  JWT Token (Bearer)
       │
       ▼
  Encrypted Storage
  (SharedPreferences)
       │
       ▼
  Auto-refresh on 401
```

## 📱 Supported Devices

- ✅ Android 9.0 (API 28) and above
- ✅ Phone and tablet layouts
- ✅ Portrait and landscape
- ✅ Google Play Services required (for Maps)

## 🌍 Ghana Features

**Phone Formats**:
- +233 24 412 3456 ✅
- 0244123456 ✅
- +233244123456 ✅

**Currency**: GH₵ (Ghana Cedis)

**Mobile Money**:
- MTN MoMo (*170#)
- Vodafone Cash (*110#)
- AirtelTigo Money (*110#)

**Timezone**: Africa/Accra (GMT+0)

**Operating Hours**: 6 AM - 10 PM

## 📦 Build Info

**Version**: 1.0.0  
**Build**: 100  
**Package**: com.delivery.rider  
**Min SDK**: 28 (Android 9.0)  
**Target SDK**: 34 (Android 14)  
**Language**: Kotlin 100%  
**Size**: ~15 MB (APK)

## 🚀 Quick Commands

```bash
# Build debug
./gradlew assembleDebug

# Build release
./gradlew assembleRelease

# Install on device
./gradlew installDebug

# Run tests
./gradlew test

# Clean build
./gradlew clean
```

## 📝 Notes

- **Simple**: No complex features, focused on core delivery tasks
- **English Only**: All text in English
- **Ghana-Optimized**: Phone formats, currency, mobile money
- **Passcode**: Provided by company admin (no self-registration)
- **Offline**: Basic caching, requires internet for most features

---

**Status**: Core Ready ✅  
**UI**: In Progress 🟡  
**Production**: Deployment Ready 🚀
