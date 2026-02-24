package com.delivery.rider.ui.map

import android.content.Context
import android.util.Log
import android.view.ViewGroup
import android.widget.FrameLayout
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.MapView
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLngBounds
import com.google.android.gms.maps.model.MarkerOptions
import com.google.android.gms.maps.model.PolylineOptions
import com.delivery.rider.R

/**
 * Google Maps implementation - Primary map provider.
 * Provides full navigation features with Google Maps SDK.
 */
class GoogleMapsProvider : MapProvider {
    
    private var mapView: MapView? = null
    private var googleMap: GoogleMap? = null
    private val TAG = "GoogleMapsProvider"
    
    override fun initialize(context: Context, container: ViewGroup) {
        try {
            mapView = MapView(context).apply {
                layoutParams = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT
                )
                onCreate(null)
                onResume()
                
                getMapAsync { map ->
                    googleMap = map
                    map.apply {
                        uiSettings.isZoomControlsEnabled = true
                        uiSettings.isMyLocationButtonEnabled = true
                        uiSettings.isCompassEnabled = true
                        isTrafficEnabled = true  // Show traffic layer
                    }
                    Log.d(TAG, "Google Maps initialized successfully")
                }
            }
            
            container.removeAllViews()
            container.addView(mapView)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize Google Maps", e)
            throw e
        }
    }
    
    override fun showLocation(lat: Double, lng: Double, zoom: Float, title: String?) {
        googleMap?.let { map ->
            val location = com.google.android.gms.maps.model.LatLng(lat, lng)
            
            // Add marker
            map.addMarker(
                MarkerOptions()
                    .position(location)
                    .title(title ?: "Location")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_ORANGE))
            )
            
            // Move camera
            map.animateCamera(CameraUpdateFactory.newLatLngZoom(location, zoom))
        }
    }
    
    override fun showRoute(pickup: LatLng, dropoff: LatLng, currentLocation: LatLng?) {
        googleMap?.let { map ->
            map.clear()
            
            val pickupGms = com.google.android.gms.maps.model.LatLng(pickup.latitude, pickup.longitude)
            val dropoffGms = com.google.android.gms.maps.model.LatLng(dropoff.latitude, dropoff.longitude)
            
            // Add pickup marker (green)
            map.addMarker(
                MarkerOptions()
                    .position(pickupGms)
                    .title("Pickup")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN))
            )
            
            // Add dropoff marker (red)
            map.addMarker(
                MarkerOptions()
                    .position(dropoffGms)
                    .title("Dropoff")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED))
            )
            
            // Add current location if available (blue)
            currentLocation?.let {
                val currentGms = com.google.android.gms.maps.model.LatLng(it.latitude, it.longitude)
                map.addMarker(
                    MarkerOptions()
                        .position(currentGms)
                        .title("You are here")
                        .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE))
                )
            }
            
            // Draw simple route line (for actual routing, use Directions API)
            val polylineOptions = PolylineOptions()
                .add(pickupGms)
                .add(dropoffGms)
                .color(android.graphics.Color.parseColor("#F59E0B"))  // Amber
                .width(10f)
            
            map.addPolyline(polylineOptions)
            
            // Fit camera to show all markers
            val boundsBuilder = LatLngBounds.Builder()
            boundsBuilder.include(pickupGms)
            boundsBuilder.include(dropoffGms)
            currentLocation?.let {
                boundsBuilder.include(com.google.android.gms.maps.model.LatLng(it.latitude, it.longitude))
            }
            
            val bounds = boundsBuilder.build()
            map.animateCamera(CameraUpdateFactory.newLatLngBounds(bounds, 100))
        }
    }
    
    override fun updateCurrentLocation(lat: Double, lng: Double) {
        googleMap?.let { map ->
            val location = com.google.android.gms.maps.model.LatLng(lat, lng)
            map.animateCamera(CameraUpdateFactory.newLatLngZoom(location, 16f))
        }
    }
    
    override fun clear() {
        googleMap?.clear()
    }
    
    override fun destroy() {
        mapView?.onDestroy()
        mapView = null
        googleMap = null
    }
    
    override fun getName(): String = "Google Maps"
}
