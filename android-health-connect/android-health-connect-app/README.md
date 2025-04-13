# Sanvia Health Connect Android App

This Android app serves as a bridge between the Health Connect API and the Sanvia backend. It allows users to connect their health data from various sources and sync it with the Sanvia platform.

## Prerequisites

- Android Studio Hedgehog | 2023.1.1 or later
- Android SDK 33 or later
- Kotlin 1.8.0 or later
- A device running Android 8.0 (API level 26) or later with Health Connect installed

## Setup

1. Clone the repository
2. Open the project in Android Studio
3. Update the `BASE_URL` in `HealthConnectService.kt` to point to your backend server
4. Build and run the app on your device

## Features

- Connect to Health Connect
- Request necessary permissions
- Sync health data including:
  - Sleep data
  - Steps data
  - Heart rate data
- Send data to Sanvia backend

## Implementation Details

The app uses:
- Health Connect SDK for accessing health data
- Retrofit for API communication
- Jetpack Compose for UI
- Kotlin Coroutines for asynchronous operations

## Permissions

The app requires the following Health Connect permissions:
- READ_HEART_RATE
- READ_SLEEP
- READ_STEPS
- READ_ACTIVE_CALORIES_BURNED
- READ_DISTANCE
- READ_EXERCISE_SESSION
- READ_VO2_MAX
- READ_RESPIRATORY_RATE

## Development

To add new health data types:
1. Add the corresponding permission to AndroidManifest.xml
2. Create a new data model class
3. Add a new endpoint to HealthConnectService
4. Update the UI to display the new data type

## Testing

1. Install the app on a device with Health Connect
2. Grant the necessary permissions
3. Test the connection flow
4. Verify data syncing with the backend

## Troubleshooting

If you encounter issues:
1. Check if Health Connect is installed and up to date
2. Verify all permissions are granted
3. Check the network connection
4. Review the logs for error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 