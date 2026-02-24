package com.delivery.rider

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.os.Build
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleObserver
import androidx.lifecycle.OnLifecycleEvent
import androidx.lifecycle.ProcessLifecycleOwner
import com.delivery.rider.service.RiderStatusService
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class RiderApplication : Application(), LifecycleObserver {
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
        
        // Observe app lifecycle to manage rider status
        ProcessLifecycleOwner.get().lifecycle.addObserver(this)
    }
    
    /**
     * Called when app comes to foreground
     */
    @OnLifecycleEvent(Lifecycle.Event.ON_START)
    fun onAppForegrounded() {
        // Start status heartbeat service when app is active
        startStatusService()
    }
    
    /**
     * Called when app goes to background
     */
    @OnLifecycleEvent(Lifecycle.Event.ON_STOP)
    fun onAppBackgrounded() {
        // Keep status service running to maintain online status
        // Service will continue sending heartbeats
    }
    
    private fun startStatusService() {
        val intent = Intent(this, RiderStatusService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
    
    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val locationChannel = NotificationChannel(
                CHANNEL_LOCATION_TRACKING,
                "Location Tracking",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Shows when location is being tracked for deliveries"
            }
            
            val notificationChannel = NotificationChannel(
                CHANNEL_GENERAL,
                "General Notifications",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Order updates, assignments, and alerts"
            }
            
            val statusChannel = NotificationChannel(
                CHANNEL_STATUS,
                "Status Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Maintains rider online status"
            }
            
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(locationChannel)
            manager.createNotificationChannel(notificationChannel)
            manager.createNotificationChannel(statusChannel)
        }
    }
    
    companion object {
        const val CHANNEL_LOCATION_TRACKING = "location_tracking"
        const val CHANNEL_GENERAL = "general_notifications"
        const val CHANNEL_STATUS = "status_service"
    }
}
