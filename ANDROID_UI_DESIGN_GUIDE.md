# Android Rider App - UI Design Guide

## 🎨 Design System

### Brand Identity
- **Primary Color**: Amber #F59E0B (ANOMAAH brand)
- **Style**: Modern, clean, Material Design 3
- **Typography**: Sans-serif-medium
- **Language**: English only

### Color Palette

```xml
<!-- Primary (Amber) -->
<color name="primary">#F59E0B</color>
<color name="primary_dark">#D97706</color>
<color name="primary_darker">#B45309</color>
<color name="primary_light">#FBBF24</color>
<color name="primary_lighter">#FDE68A</color>
<color name="primary_surface">#FFFBEB</color>

<!-- Semantic Colors -->
<color name="success">#10B981</color>      <!-- Green -->
<color name="error">#EF4444</color>        <!-- Red -->
<color name="warning">#F59E0B</color>      <!-- Amber -->
<color name="info">#3B82F6</color>         <!-- Blue -->

<!-- Neutrals -->
<color name="background">#F8FAFC</color>
<color name="surface">#FFFFFF</color>
<color name="text_primary">#0F172A</color>
<color name="text_secondary">#475569</color>
<color name="text_hint">#94A3B8</color>
<color name="border">#E2E8F0</color>
```

---

## 📱 Screen Designs

### 1. Login Screen

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║   [ANOMAAH Logo]              ║  │
│  ║                               ║  │
│  ║   ANOMAAH                     ║  │
│  ║   RIDER APP                   ║  │
│  ╚═══════════════════════════════╝  │ ← Amber gradient
│                                     │
│  Welcome Back                       │
│  Sign in with your phone           │
│  and passcode                       │
│                                     │
│  Phone Number                       │
│  ┌───────────────────────────────┐  │
│  │ 054 XXX XXXX                  │  │
│  └───────────────────────────────┘  │
│                                     │
│  5-Digit Passcode                   │
│  ┌───────────────────────────────┐  │
│  │     • • • • •                 │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃      SIGN IN                 ┃  │ ← Amber button
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                                     │
│  Your company admin provides        │
│  your passcode                      │
└─────────────────────────────────────┘
```

**Features**:
- Clean amber gradient header
- Large ANOMAAH branding
- Simple 2-field form
- Bold amber CTA button
- Help text at bottom

---

### 2. Orders List

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║ My Orders        [🟢 Online] ║  │ ← Amber header
│  ║ 3 active orders              ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  [All] [Pending] [Active] [Done]   │ ← Tabs
│  ━━━━                               │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Order #abc123    [Assigned]  │  │ ← Order card
│  │                               │  │
│  │ 🟢 Oxford Street, Osu         │  │
│  │ 🔴 Airport Road               │  │
│  │                               │  │
│  │ GH₵ 25.00         2 mins ago │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Order #def456  [Picked Up]   │  │
│  │                               │  │
│  │ 🟢 Madina                     │  │
│  │ 🔴 Circle                     │  │
│  │                               │  │
│  │ GH₵ 18.50         15 mins ago│  │
│  └───────────────────────────────┘  │
│                                     │
│  [Orders] [Track] [₵] [Profile]    │ ← Bottom nav
└─────────────────────────────────────┘
```

**Features**:
- Amber gradient header with online status
- Tab filtering (All, Pending, Active, Done)
- Material cards with rounded corners
- Status badges with colors
- Location indicators (🟢 pickup, 🔴 dropoff)
- Fee and time prominently displayed
- Bottom navigation

---

### 3. Order Details (Enhanced)

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║ ← Order #abc123   [Assigned] ║  │ ← Amber header
│  ║   10 mins ago                ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │     Delivery Fee               │  │ ← Fee card
│  │     GH₵ 25.00                 │  │   (amber bg)
│  │     📏 5.2 km                  │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Customer                       │  │ ← Customer card
│  │ ┌─┐ Kwame Mensah        [📞] │  │
│  │ └─┘ +233 24 XXX XXXX          │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 🟢 Pickup Location  12 mins   │  │ ← Pickup card
│  │   Oxford Street, Osu          │  │
│  │   [  🗺️  Navigate  ]          │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 🔴 Drop-off Location  25 mins │  │ ← Dropoff card
│  │   Airport Road                │  │
│  │   [  🗺️  Navigate  ]          │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃    ✅ Accept Order           ┃  │ ← Primary action
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │   (green)
│  ┌───────────────────────────────┐  │
│  │    Update Status               │  │ ← Secondary
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │    Cancel Order                │  │ ← Tertiary
│  └───────────────────────────────┘  │   (red text)
└─────────────────────────────────────┘
```

**Features**:
- Back button in header
- Large fee display with amber background
- Customer info with call button
- Pickup/dropoff cards with ETA
- Navigate buttons for each location
- Context-aware action buttons:
  - Pending: "Accept Order" (green)
  - Accepted: "Mark Picked Up" (green)
  - Picked Up: "Mark Delivered" (green)
  - All: "Update Status" (outlined)
  - All: "Cancel Order" (red text)

---

### 4. Status Update Dialog

```
┌─────────────────────────────────────┐
│                                     │
│     Update Order Status             │
│     Order #abc123                   │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  ○ ✅ Accepted - Going to pickup   │
│  ○ 📦 Picked Up - Package collected│
│  ● 🚴 In Transit - On the way      │ ← Selected
│  ○ ✅ Delivered - Order complete   │
│                                     │
│  ┌─────────────┐  ┏━━━━━━━━━━━━┓  │
│  │   Cancel    │  ┃   Update   ┃  │
│  └─────────────┘  ┗━━━━━━━━━━━━┛  │
│                     ↑ Green button  │
└─────────────────────────────────────┘
```

**Features**:
- Modal dialog
- Radio button selection
- Emoji + descriptive text
- Cancel (outlined) and Update (green) buttons

---

### 5. Earnings

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║ My Earnings                   ║  │ ← Amber header
│  ╚═══════════════════════════════╝  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   💰 Total Earnings           │  │ ← Total card
│  │      GH₵ 1,250.00             │  │   (amber bg)
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────┐  ┌─────────────────┐│
│  │ Available │  │ Pending Payout  ││ ← Split cards
│  │ GH₵ 350   │  │ GH₵ 900         ││
│  └───────────┘  └─────────────────┘│
│                                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃    Request Payout            ┃  │ ← Amber button
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                                     │
│  Payout History                     │
│  ────────────────────────────────  │
│  ┌───────────────────────────────┐  │
│  │ ✅ Jan 20  GH₵ 500  Completed │  │ ← History list
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ ⏳ Jan 15  GH₵ 450  Pending   │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ ✅ Jan 10  GH₵ 380  Completed │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Orders] [Track] [₵] [Profile]    │
└─────────────────────────────────────┘
```

**Features**:
- Large total earnings card (amber)
- Split view: Available vs Pending
- Prominent "Request Payout" button
- Payout history with status icons
- Color-coded statuses

---

### 6. Payout Request Dialog

```
┌─────────────────────────────────────┐
│                                     │
│        Request Payout               │
│  Transfer earnings to your mobile   │
│        money account                │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Available Balance           │  │ ← Amber card
│  │      GH₵ 350.00               │  │
│  └───────────────────────────────┘  │
│                                     │
│  Payout Amount                      │
│  ┌───────────────────────────────┐  │
│  │        150.00                 │  │ ← Amount input
│  └───────────────────────────────┘  │
│                                     │
│  Mobile Money Number                │
│  ┌───────────────────────────────┐  │
│  │   +233 24 412 3456            │  │ ← Phone display
│  └───────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ℹ️ Payout will be processed    ││ ← Info banner
│  │   within 24 hours to your      ││   (blue bg)
│  │   registered mobile money      ││
│  │   account                       ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────┐  ┏━━━━━━━━━━━━━┓ │
│  │   Cancel    │  ┃   Request   ┃ │
│  └─────────────┘  ┗━━━━━━━━━━━━━┛ │
│                     ↑ Amber button  │
└─────────────────────────────────────┘
```

**Features**:
- Available balance prominently displayed
- Large amount input field
- Pre-filled phone number
- Informative banner (blue background)
- Clear action buttons

---

### 7. Profile

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║ My Profile                    ║  │ ← Amber header
│  ╚═══════════════════════════════╝  │
│                                     │
│        👤                           │ ← Avatar
│    Kwame Mensah                     │
│  +233 24 412 3456                   │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Company: Swift Riders           ││ ← Info cards
│  │ Rating: ⭐ 4.8 (125 reviews)    ││
│  │ Deliveries: 342 completed       ││
│  │ Bike: Honda CB150               ││
│  └─────────────────────────────────┘│
│                                     │
│  🟢 Status                          │
│  ┌─────────┐  ┌──────────┐         │ ← Toggle
│  │ Online  │  │ Offline  │         │
│  └─────────┘  └──────────┘         │
│                                     │
│  ┌───────────────────────────────┐  │
│  │    Change Passcode             │  │ ← Actions
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │    Sign Out                    │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Orders] [Track] [₵] [Profile]    │
└─────────────────────────────────────┘
```

**Features**:
- Centered avatar and name
- Info cards with stats
- Online/offline toggle
- Action buttons (outlined)
- Sign out option

---

## 🎨 UI Components

### Material Cards

```xml
<com.google.android.material.card.MaterialCardView
    app:cardCornerRadius="16dp"
    app:cardElevation="1dp"
    app:strokeColor="@color/border"
    app:strokeWidth="1dp">
```

**Variants**:
- **Standard**: White bg, border, 1dp elevation
- **Amber**: `primary_surface` bg, no border
- **Success**: `success_bg` bg
- **Error**: `error_bg` bg
- **Info**: `info_bg` bg

### Buttons

**Primary (Amber)**:
```xml
<Button
    android:background="@drawable/btn_primary"
    android:textColor="@color/white" />
```

**Success (Green)**:
```xml
<Button
    android:background="@drawable/btn_success"
    android:textColor="@color/white" />
```

**Error (Red)**:
```xml
<Button
    android:background="@drawable/btn_error"
    android:textColor="@color/white" />
```

**Outlined**:
```xml
<Button
    style="@style/Anomaah.Button.Outlined"
    android:textColor="@color/text_primary" />
```

### Status Badges

```xml
<TextView
    android:background="@drawable/badge_pending"
    android:textColor="@color/status_pending_text" />
```

**Variants**:
- `badge_pending` - Amber background
- `badge_assigned` - Blue background
- `badge_in_transit` - Purple background
- `badge_delivered` - Green background
- `badge_cancelled` - Red background

### Typography

**Headers**: 20-24sp, bold, `text_primary`
**Body**: 14-16sp, regular, `text_primary`
**Secondary**: 13-14sp, regular, `text_secondary`
**Caption**: 12sp, regular, `text_hint`
**Huge**: 32-36sp, bold (for amounts)

---

## 🎯 Design Principles

### 1. Clarity
- Large, readable text
- Clear hierarchy
- Obvious actions

### 2. Simplicity
- Minimal steps
- Focus on core tasks
- No unnecessary features

### 3. Consistency
- Amber brand color throughout
- Same card style everywhere
- Consistent button styles

### 4. Feedback
- Loading states
- Success/error messages
- Status updates

### 5. Accessibility
- High contrast
- Large touch targets (44dp minimum)
- Clear labels

---

## 📐 Spacing

**Standard Padding**: 16dp
**Large Padding**: 20-24dp
**Card Margin**: 12-16dp
**Section Spacing**: 16-20dp
**Button Height**: 48-56dp
**Icon Size**: 24dp (small), 40dp (large)

---

## 🇬🇭 Ghana-Specific

**Currency**: Always show "GH₵" before amounts
**Phone**: Format as "+233 24 412 3456"
**Language**: English only
**Icons**: Use emoji for quick visual cues
**Mobile Money**: MTN, Vodafone, AirtelTigo logos

---

## 🚀 Implementation Status

### ✅ Complete
- Color scheme
- Base styles
- Login screen
- Orders list
- Order card
- Payout adapter

### 🟡 In Progress
- Order details enhanced
- Dialogs (status update, payout)
- Button variants
- Profile enhancements

### ⏳ Next
- Tracking screen with map
- Animations
- Loading states
- Error states
- Empty states

---

**Design System Version**: 1.0  
**Last Updated**: 2026-02-24  
**Brand**: ANOMAAH Delivery

**Made with ❤️ for Ghanaian riders** 🇬🇭
