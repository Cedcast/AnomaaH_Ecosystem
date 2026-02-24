package com.delivery.rider.service

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.os.Handler
import android.os.Looper
import android.util.Log
import com.delivery.rider.data.repository.RiderRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Background service to maintain rider online status with periodic heartbeats.
 * Sends status update every 5 minutes to keep rider marked as online.
 * Company dashboard can use this to show accurate real-time rider availability.
 */
@AndroidEntryPoint
class RiderStatusService : Service() {
    
    @Inject
    lateinit var riderRepository: RiderRepository
    
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val handler = Handler(Looper.getMainLooper())
    private val heartbeatInterval = 5 * 60 * 1000L  // 5 minutes
    
    private val heartbeatRunnable = object : Runnable {
        override fun run() {
            sendStatusHeartbeat()
            handler.postDelayed(this, heartbeatInterval)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "RiderStatusService created")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "RiderStatusService started")
        
        // Start periodic heartbeat
        handler.postDelayed(heartbeatRunnable, heartbeatInterval)
        
        // Send immediate heartbeat
        sendStatusHeartbeat()
        
        // Restart service if killed by system
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "RiderStatusService destroyed")
        
        // Stop heartbeat
        handler.removeCallbacks(heartbeatRunnable)
        
        // Send offline status
        sendOfflineStatus()
        
        // Cancel coroutines
        serviceScope.cancel()
    }
    
    private fun sendStatusHeartbeat() {
        serviceScope.launch {
            try {
                riderRepository.updateStatus("online").onSuccess {
                    Log.d(TAG, "Status heartbeat sent: online")
                }.onFailure { e ->
                    Log.e(TAG, "Status heartbeat failed: ${e.message}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Status heartbeat error", e)
            }
        }
    }
    
    private fun sendOfflineStatus() {
        serviceScope.launch {
            try {
                riderRepository.updateStatus("offline").onSuccess {
                    Log.d(TAG, "Offline status sent")
                }.onFailure { e ->
                    Log.e(TAG, "Offline status failed: ${e.message}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Offline status error", e)
            }
        }
    }
    
    companion object {
        private const val TAG = "RiderStatusService"
    }
}
