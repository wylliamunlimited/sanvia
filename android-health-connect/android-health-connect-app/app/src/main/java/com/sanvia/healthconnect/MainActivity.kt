package com.sanvia.healthconnect

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.health.connect.client.HealthConnectClient.Companion.getSdkStatus
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.sanvia.healthconnect.api.HealthConnectData
import com.sanvia.healthconnect.api.HealthConnectService
// import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.TimeoutCancellationException

private const val TAG = "MainActivity"
private const val HEALTH_CONNECT_SETTINGS = "android.settings.HEALTH_CONNECT_SETTINGS"
private const val HEALTH_CONNECT_PACKAGE = "com.google.android.apps.healthdata"

class MainActivity : ComponentActivity() {
    private var healthConnectClient: HealthConnectClient? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        try {
            FirebaseApp.initializeApp(this)
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing Firebase: ${e.message}", e)
        }

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val context = LocalContext.current
                    var showSettingsDialog by remember { mutableStateOf(false) }

                    if (showSettingsDialog) {
                        AlertDialog(
                            onDismissRequest = { showSettingsDialog = false },
                            title = { Text("Health Connect Access") },
                            text = { 
                                Text("Health Connect is now part of system settings. You can access it through:\n\n" +
                                     "1. Settings > Apps > Health Connect\n" +
                                     "2. Quick Settings menu (swipe down and edit tiles)")
                            },
                            confirmButton = {
                                Button(
                                    onClick = {
                                        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                                            data = Uri.fromParts("package", HEALTH_CONNECT_PACKAGE, null)
                                        }
                                        if (true) {
                                            context.startActivity(intent)
                                        } else {
                                            // Fallback to Health Connect in Play Store
                                            val fallbackIntent = Intent(Intent.ACTION_VIEW).apply {
                                                data = Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata")
                                                setPackage("com.android.vending")
                                            }
                                            context.startActivity(fallbackIntent)
                                        }
                                        showSettingsDialog = false
                                    }
                                ) {
                                    Text("Open Settings")
                                }
                            },
                            dismissButton = {
                                TextButton(onClick = { showSettingsDialog = false }) {
                                    Text("Cancel")
                                }
                            }
                        )
                    }

                    val availability =
                        try {
                            val status = getSdkStatus(context)
                            Log.d(TAG, "Health Connect SDK Status: $status")
                            status
                        } catch (e: Exception) {
                            Log.e(TAG, "Error checking Health Connect availability: ${e.message}", e)
                            HealthConnectClient.SDK_UNAVAILABLE
                        }

                    when (availability) {
                        HealthConnectClient.SDK_UNAVAILABLE -> {
                            ErrorScreen(
                                message = "Please install or update Health Connect from the Play Store",
                                onOpenSettings = { showSettingsDialog = true }
                            )
                        }
                        HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> {
                            ErrorScreen(
                                message = "Please update Health Connect from the Play Store",
                                onOpenSettings = { showSettingsDialog = true }
                            )
                        }
                        HealthConnectClient.SDK_AVAILABLE -> {
                            var client by remember { mutableStateOf<HealthConnectClient?>(null) }

                            LaunchedEffect(Unit) {
                                try {
                                    client = HealthConnectClient.getOrCreate(context)
                                    Log.d(TAG, "Health Connect client created successfully")
                                } catch (e: Exception) {
                                    Log.e(TAG, "Error creating HealthConnectClient: ${e.message}", e)
                                }
                            }

                            if (client != null) {
                                HealthConnectScreen(client!!)
                            } else {
                                ErrorScreen(
                                    message = "Please check Health Connect settings and try again",
                                    onOpenSettings = { showSettingsDialog = true }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ErrorScreen(
    message: String,
    onOpenSettings: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.error
        )

        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onOpenSettings) {
            Text("Open Settings")
        }
    }
}

@Composable
fun HealthConnectScreen(healthConnectClient: HealthConnectClient) {
    var isConnected by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val permissionController = healthConnectClient.permissionController

    // Create the permission launcher at the Composable level
    val permissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(DistanceRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        HealthPermission.getReadPermission(Vo2MaxRecord::class),
        HealthPermission.getReadPermission(RespiratoryRateRecord::class)
    )

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { granted ->
        // Handle permission result
        if (granted.values.all { it }) {
            isConnected = true
        } else {
            errorMessage = "Not all permissions were granted"
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(text = "Sanvia Health Connect", style = MaterialTheme.typography.headlineMedium)

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                isLoading = true
                errorMessage = null


                val sdkStatus = getSdkStatus(context)

                if (sdkStatus != HealthConnectClient.SDK_AVAILABLE) {
                    errorMessage = when (sdkStatus) {
                        HealthConnectClient.SDK_UNAVAILABLE -> "Health Connect app not installed or no viable integration"
                        HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> "Health Connect needs an update"
                        else -> "Health Connect is not available on this device"
                    }
                    isLoading = false
                    return@Button
                }
                // Request permissions
                // Get Firebase token and handle permissions
                FirebaseAuth.getInstance().currentUser?.getIdToken(true)
                    ?.addOnCompleteListener { task ->
                        if (task.isSuccessful) {
                            val idToken = task.result?.token
                            val uid = FirebaseAuth.getInstance().currentUser?.uid
                            
                            if (idToken != null && uid != null) {
                                val tokenHeader = "Bearer $idToken"
                                val deviceId = Settings.Secure.getString(
                                    context.contentResolver, 
                                    Settings.Secure.ANDROID_ID
                                )

                                scope.launch {
                                    try {
                                        withTimeout(30000) { // 30 second timeout
                                            // Check and request permissions
                                            val granted = permissionController.getGrantedPermissions()
                                            val missingPermissions = permissions.filter { it !in granted }.toSet()

                                            if (missingPermissions.isNotEmpty()) {
                                                permissionLauncher.launch(missingPermissions.toTypedArray())
                                            }

                                            // Send granted permissions to backend
                                            val grantedNow = permissionController.getGrantedPermissions()
                                            val healthService = HealthConnectService.create()

                                            val response = healthService.connectHealthConnect(
                                                token = tokenHeader,
                                                data = HealthConnectData(
                                                    userId = uid,
                                                    deviceId = deviceId,
                                                    permissions = grantedNow.toList()
                                                )
                                            )

                                            withContext(Dispatchers.Main) {
                                                if (response.status == "success") {
                                                    isConnected = true
                                                } else {
                                                    errorMessage = response.message
                                                }
                                            }
                                        }
                                    } catch (e: TimeoutCancellationException) {
                                        withContext(Dispatchers.Main) {
                                            errorMessage = "Connection timed out. Please try again."
                                        }
                                    } catch (e: Exception) {
                                        withContext(Dispatchers.Main) {
                                            errorMessage = e.message ?: "An unknown error occurred"
                                        }
                                    } finally {
                                        isLoading = false
                                    }
                                }
                            } else {
                                errorMessage = "Failed to get Firebase credentials"
                                isLoading = false
                            }
                        } else {
                            errorMessage = "Auth error: ${task.exception?.message}"
                            isLoading = false
                        }
                    }
            },
            enabled = !isLoading && !isConnected
        ) {
            Text(if (isLoading) "Connecting..." else "Connect")
        }

        if (errorMessage != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = errorMessage!!, color = MaterialTheme.colorScheme.error)
        }

        if (isConnected) {
            Spacer(modifier = Modifier.height(16.dp))
            Text("Connected to Health Connect")
        }
    }
}
