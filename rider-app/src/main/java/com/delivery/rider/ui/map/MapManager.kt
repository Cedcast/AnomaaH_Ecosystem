package com.delivery.rider.ui.map

import android.content.Context
import android.util.Log
import android.view.ViewGroup
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import com.delivery.rider.BuildConfig

/**
 * MapManager handles map provider selection and fallback logic.
 * Priority:
 * 1. Google Maps (primary)
 * 2. Mapbox (fallback)
 * 3. OSM WebView (emergency)
 */
class MapManager(
    private val context: Context,
    private val container: ViewGroup
) {
    
    private var currentProvider: MapProvider? = null
    private val TAG = "MapManager"
    
    /**
     * Initialize map with automatic provider selection and fallback
     */
    fun initialize(): MapProvider {
        // Try Google Maps first
        if (BuildConfig.MAP_PROVIDER == "google" || BuildConfig.MAP_PROVIDER.isEmpty()) {
            try {
                Log.d(TAG, "Attempting to initialize Google Maps...")
                val provider = GoogleMapsProvider()
                provider.initialize(context, container)
                currentProvider = provider
                Log.i(TAG, "✅ Using Google Maps")
                return provider
            } catch (e: Exception) {
                Log.w(TAG, "⚠️ Google Maps failed: ${e.message}, trying Mapbox...")
            }
        }
        
        // Try Mapbox as fallback
        try {
            Log.d(TAG, "Attempting to initialize Mapbox...")
            val provider = MapboxProvider()
            provider.initialize(context, container)
            currentProvider = provider
            Log.i(TAG, "✅ Using Mapbox (fallback)")
            return provider
        } catch (e: Exception) {
            Log.w(TAG, "⚠️ Mapbox failed: ${e.message}, falling back to OSM...")
        }
        
        // Emergency fallback: OSM in WebView
        if (BuildConfig.USE_OSM_FALLBACK) {
            try {
                Log.d(TAG, "Using OSM WebView fallback...")
                val provider = OSMWebViewProvider()
                provider.initialize(context, container)
                currentProvider = provider
                Log.i(TAG, "✅ Using OSM WebView (emergency fallback)")
                return provider
            } catch (e: Exception) {
                Log.e(TAG, "❌ All map providers failed!", e)
                throw IllegalStateException("No map provider available", e)
            }
        }
        
        throw IllegalStateException("No map provider configured or available")
    }
    
    /**
     * Get current active provider
     */
    fun getProvider(): MapProvider? = currentProvider
    
    /**
     * Destroy current provider and cleanup resources
     */
    fun destroy() {
        currentProvider?.destroy()
        currentProvider = null
    }
}

/**
 * Emergency fallback: OpenStreetMap in WebView.
 * Used when both Google Maps and Mapbox fail.
 */
class OSMWebViewProvider : MapProvider {
    
    private var webView: WebView? = null
    private var currentLat = 5.6037  // Accra, Ghana
    private var currentLng = -0.1870
    
    override fun initialize(context: Context, container: ViewGroup) {
        webView = WebView(context).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            settings.javaScriptEnabled = true
            webViewClient = WebViewClient()
            loadDataWithBaseURL(null, getOSMHtml(currentLat, currentLng), "text/html", "utf-8", null)
        }
        
        container.removeAllViews()
        container.addView(webView)
    }
    
    override fun showLocation(lat: Double, lng: Double, zoom: Float, title: String?) {
        currentLat = lat
        currentLng = lng
        webView?.loadUrl("javascript:map.setView([$lat, $lng], ${zoom.toInt()});")
    }
    
    override fun showRoute(pickup: LatLng, dropoff: LatLng, currentLocation: LatLng?) {
        // Basic implementation: just center between pickup and dropoff
        val centerLat = (pickup.latitude + dropoff.latitude) / 2
        val centerLng = (pickup.longitude + dropoff.longitude) / 2
        showLocation(centerLat, centerLng, 13f)
    }
    
    override fun updateCurrentLocation(lat: Double, lng: Double) {
        showLocation(lat, lng, 16f)
    }
    
    override fun clear() {
        // WebView doesn't support dynamic marker clearing easily
    }
    
    override fun destroy() {
        webView?.destroy()
        webView = null
    }
    
    override fun getName(): String = "OpenStreetMap (WebView)"
    
    private fun getOSMHtml(lat: Double, lng: Double): String {
        return """
            <!DOCTYPE html>
            <html>
            <head>
              <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
              <style>html, body { height:100%; margin:0; padding:0; }</style>
              <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
              <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            </head>
            <body>
              <div id="map" style="width:100%;height:100%"></div>
              <script>
                var map = L.map('map').setView([$lat, $lng], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                  maxZoom: 19,
                  attribution: '© OpenStreetMap'
                }).addTo(map);
                
                // Add marker at current location
                L.marker([$lat, $lng]).addTo(map);
              </script>
            </body>
            </html>
        """.trimIndent()
    }
}
