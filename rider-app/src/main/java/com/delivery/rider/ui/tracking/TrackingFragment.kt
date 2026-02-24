package com.delivery.rider.ui.tracking

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.delivery.rider.R
import com.delivery.rider.ui.viewmodel.TrackingViewModel
import androidx.fragment.app.viewModels
import com.delivery.rider.ui.map.MapManager
import com.delivery.rider.ui.map.MapProvider
import dagger.hilt.android.AndroidEntryPoint

/**
 * TrackingFragment displays live tracking on a map.
 * Uses MapManager to automatically select best available map provider:
 * 1. Google Maps (primary)
 * 2. Mapbox (fallback)
 * 3. OSM WebView (emergency)
 */
@AndroidEntryPoint
class TrackingFragment : Fragment() {
    
    private val viewModel: TrackingViewModel by viewModels()
    private var mapManager: MapManager? = null
    private var mapProvider: MapProvider? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_tracking, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupMapView()
        observeViewModel()
    }

    private fun setupMapView() {
        val container = view?.findViewById<FrameLayout>(R.id.mapContainer) ?: return
        
        try {
            // Initialize map with automatic provider selection
            mapManager = MapManager(requireContext(), container)
            mapProvider = mapManager?.initialize()
            
            // Show success message with provider name
            mapProvider?.let {
                Toast.makeText(
                    requireContext(),
                    "Using ${it.getName()}",
                    Toast.LENGTH_SHORT
                ).show()
            }
            
            // Show default location (Accra, Ghana)
            mapProvider?.showLocation(5.6037, -0.1870, 13f, "Accra")
            
        } catch (e: Exception) {
            Toast.makeText(
                requireContext(),
                "Map initialization failed: ${e.message}",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private fun observeViewModel() {
        // Observe tracking data from ViewModel
        viewModel.currentLocation.observe(viewLifecycleOwner) { location ->
            location?.let {
                mapProvider?.updateCurrentLocation(it.latitude, it.longitude)
            }
        }
        
        viewModel.activeRoute.observe(viewLifecycleOwner) { route ->
            route?.let {
                // Show route on map
                mapProvider?.showRoute(it.pickup, it.dropoff, it.currentLocation)
            }
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        mapManager?.destroy()
        mapManager = null
        mapProvider = null
    }
}
