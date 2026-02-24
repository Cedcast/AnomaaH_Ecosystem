package com.delivery.rider.ui.map

import android.content.Context
import android.view.ViewGroup

/**
 * Map provider abstraction to support multiple map backends.
 * Primary: Google Maps
 * Fallback: Mapbox
 * Emergency: OSM in WebView
 */
interface MapProvider {
    
    /**
     * Initialize the map view and add to container
     */
    fun initialize(context: Context, container: ViewGroup)
    
    /**
     * Show a single location on the map with optional zoom
     */
    fun showLocation(lat: Double, lng: Double, zoom: Float = 15f, title: String? = null)
    
    /**
     * Show route between pickup and dropoff locations
     */
    fun showRoute(pickup: LatLng, dropoff: LatLng, currentLocation: LatLng? = null)
    
    /**
     * Update rider's current location
     */
    fun updateCurrentLocation(lat: Double, lng: Double)
    
    /**
     * Clear all markers and overlays
     */
    fun clear()
    
    /**
     * Cleanup and release resources
     */
    fun destroy()
    
    /**
     * Get provider name
     */
    fun getName(): String
}

/**
 * Simple lat/lng data class
 */
data class LatLng(
    val latitude: Double,
    val longitude: Double
)
