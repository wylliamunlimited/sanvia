package com.sanvia.healthconnect

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord

class MainActivity : ComponentActivity() {
    private lateinit var healthConnectClient: HealthConnectClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize Health Connect client
        healthConnectClient = HealthConnectClient.getOrCreate(this)

        setContent {
            MaterialTheme {
                Surface(
                        modifier = Modifier.fillMaxSize(),
                        color = MaterialTheme.colorScheme.background
                ) { HealthConnectScreen(healthConnectClient) }
            }
        }
    }
}

@Composable
fun HealthConnectScreen(healthConnectClient: HealthConnectClient) {
    var isConnected by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

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

                    // Check if Health Connect is available
                    if (!HealthConnectClient.isAvailable(this)) {
                        errorMessage = "Health Connect is not available on this device"
                        isLoading = false
                        return@Button
                    }

                    // Request permissions
                    val permissionController = healthConnectClient.permissionController

                    val permissions =
                            setOf(
                                    HealthPermission.getReadPermission(StepsRecord::class),
                                    HealthPermission.getReadPermission(HeartRateRecord::class),
                                    HealthPermission.getReadPermission(SleepSessionRecord::class),
                                    HealthPermission.getReadPermission(
                                            ActiveCaloriesBurnedRecord::class
                                    ),
                                    HealthPermission.getReadPermission(DistanceRecord::class),
                                    HealthPermission.getReadPermission(
                                            ExerciseSessionRecord::class
                                    ),
                                    HealthPermission.getReadPermission(Vo2MaxRecord::class),
                                    HealthPermission.getReadPermission(RespiratoryRateRecord::class)
                            )

                    LaunchedEffect(Unit) {
                        try {
                            val granted = permissionController.getGrantedPermissions()

                            val missingPermissions = permissions.filter { it !in granted }.toSet()

                            if (missingPermissions.isNotEmpty()) {
                                val activityResultLauncher =
                                        rememberLauncherForActivityResult(
                                                ActivityResultContracts.StartActivityForResult()
                                        ) {
                                            // Optional: handle result here
                                        }

                                val requestIntent =
                                        permissionController.createRequestPermissionIntent(
                                                missingPermissions
                                        )
                                activityResultLauncher.launch(requestIntent)
                            }

                            // Send granted permission list to backend
                            val grantedNow = permissionController.getGrantedPermissions()
                            val token =
                                    "Bearer YOUR_FIREBASE_ID_TOKEN" // Replace or fetch dynamically
                            val healthService = HealthConnectService.create()

                            val response =
                                    healthService.connectHealthConnect(
                                            token,
                                            HealthConnectData(
                                                    userId = "YOUR_USER_ID", // replace with actual
                                                    deviceId =
                                                            "android-device-id", // use Build.SERIAL
                                                    // or
                                                    // Settings.Secure.ANDROID_ID
                                                    permissions = grantedNow.toList()
                                            )
                                    )

                            if (response.status == "success") {
                                isConnected = true
                            } else {
                                errorMessage = response.message
                            }
                        } catch (e: Exception) {
                            errorMessage = e.message
                        } finally {
                            isLoading = false
                        }
                    }
                },
                enabled = !isLoading && !isConnected
        ) { Text(if (isLoading) "Connecting..." else "Connect") }

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
