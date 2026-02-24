package com.delivery.rider.ui.map

import android.content.Context
import android.util.Log
import android.view.ViewGroup
import android.widget.FrameLayout
import com.mapbox.maps.MapView
import com.mapbox.maps.MapboxMap
import com.mapbox.maps.Style
import com.mapbox.maps.plugin.annotation.annotations
import com.mapbox.maps.plugin.annotation.generated.PointAnnotationOptions
import com.mapbox.maps.plugin.annotation.generated.createPointAnnotationManager
import com.mapbox.geojson.Point
import com.mapbox.maps.CameraOptions
import com.mapbox.maps.plugin.gestures.gestures
import com.delivery.rider.BuildConfig

/**
 * Mapbox implementation - Fallback map provider.
 * Provides alternative map provider if Google Maps fails.
 */
class MapboxProvider : MapProvider {
    
    private var mapView: MapView? = null
    private var mapboxMap: MapboxMap? = null
    private val TAG = "MapboxProvider"
    
    override fun initialize(context: Context, container: ViewGroup) {
        try {
            if (BuildConfig.MAPBOX_ACCESS_TOKEN.isEmpty()) {
                throw IllegalStateException("Mapbox access token not configured")
            }
            
            mapView = MapView(context).apply {
                layoutParams = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT
                )
            }
            
            mapboxMap = mapView?.getMapboxMap()
            mapboxMap?.loadStyleUri(Style.MAPBOX_STREETS) {
                Log.d(TAG, "Mapbox initialized successfully")
            }
            
            // Enable gestures
            mapView?.gestures?.apply {
                rotateEnabled = true
                pitchEnabled = true
                scrollEnabled = true
                zoomEnabled = true
            }
            
            container.removeAllViews()
            container.addView(mapView)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize Mapbox", e)
            throw e
        }
    }
    
    override fun showLocation(lat: Double, lng: Double, zoom: Float, title: String?) {
        mapboxMap?.let { map ->
            // Move camera to location
            val cameraOptions = CameraOptions.Builder()
                .center(Point.fromLngLat(lng, lat))
                .zoom(zoom.toDouble())
                .build()
            
            map.setCamera(cameraOptions)
            
            // Add marker
            mapView?.annotations?.let { annotationApi ->
                val pointAnnotationManager = annotationApi.createPointAnnotationManager()
                val pointAnnotationOptions = PointAnnotationOptions()
                    .withPoint(Point.fromLngLat(lng, lat))
                    .withIconImage("marker-icon")
                
                pointAnnotationManager.create(pointAnnotationOptions)
            }
        }
    }
    
    override fun showRoute(pickup: LatLng, dropoff: LatLng, currentLocation: LatLng?) {
        mapboxMap?.let { map ->
            // Clear existing annotations
            clear()
            
            mapView?.annotations?.let { annotationApi ->
                val pointAnnotationManager = annotationApi.createPointAnnotationManager()
                
                // Add pickup marker
                val pickupOptions = PointAnnotationOptions()
                    .withPoint(Point.fromLngLat(pickup.longitude, pickup.latitude))
                    .withIconImage("marker-icon")
                pointAnnotationManager.create(pickupOptions)
                
                // Add dropoff marker
                val dropoffOptions = PointAnnotationOptions()
                    .withPoint(Point.fromLngLat(dropoff.longitude, dropoff.latitude))
                    .withIconImage("marker-icon")
                pointAnnotationManager.create(dropoffOptions)
                
                // Add current location marker if available
                currentLocation?.let {
                    val currentOptions = PointAnnotationOptions()
                        .withPoint(Point.fromLngLat(it.longitude, it.latitude))
                        .withIconImage("marker-icon")
                    pointAnnotationManager.create(currentOptions)
                }
            }
            
            // Calculate bounds to fit all points
            val latitudes = listOfNotNull(
                pickup.latitude,
                dropoff.latitude,
                currentLocation?.latitude
            )
            val longitudes = listOfNotNull(
                pickup.longitude,
                dropoff.longitude,
                currentLocation?.longitude
            )
            
            val centerLat = (latitudes.maxOrNull()!! + latitudes.minOrNull()!!) / 2
            val centerLng = (longitudes.maxOrNull()!! + longitudes.minOrNull()!!) / 2
            
            // Set camera to show both points
            val cameraOptions = CameraOptions.Builder()
                .center(Point.fromLngLat(centerLng, centerLat))
                .zoom(12.0)
                .build()
            
            map.setCamera(cameraOptions)
        }
    }
    
    override fun updateCurrentLocation(lat: Double, lng: Double) {
        mapboxMap?.let { map ->
            val cameraOptions = CameraOptions.Builder()
                .center(Point.fromLngLat(lng, lat))
                .zoom(16.0)
                .build()
            
            map.setCamera(cameraOptions)
        }
    }
    
    override fun clear() {
        mapView?.annotations?.let { annotationApi ->
            // Clear all annotation managers
            annotationApi.cleanup()
        }
    }
    
    override fun destroy() {
        mapView?.onDestroy()
        mapView = null
        mapboxMap = null
    }
    
    override fun getName(): String = "Mapbox"
}
