package com.sanvia.healthconnect.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

interface HealthConnectService {
    @POST("healthconnect/connect")
    suspend fun connectHealthConnect(
            @Header("Authorization") token: String,
            @Body data: HealthConnectData
    ): HealthConnectResponse

    @GET("healthconnect/sleep")
    suspend fun getSleepData(
            @Header("Authorization") token: String,
            @Query("start_time") startTime: String,
            @Query("end_time") endTime: String
    ): HealthDataResponse

    @GET("healthconnect/steps")
    suspend fun getStepsData(
            @Header("Authorization") token: String,
            @Query("start_time") startTime: String,
            @Query("end_time") endTime: String
    ): HealthDataResponse

    @GET("healthconnect/heart-rate")
    suspend fun getHeartRateData(
            @Header("Authorization") token: String,
            @Query("start_time") startTime: String,
            @Query("end_time") endTime: String
    ): HealthDataResponse

    companion object {
        private const val BASE_URL =
                "https://api.sanvia.app/" 

        fun create(): HealthConnectService {
            return Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build()
                    .create(HealthConnectService::class.java)
        }
    }
}

data class HealthConnectData(
        val userId: String,
        val deviceId: String,
        val permissions: List<String>
)

data class HealthConnectResponse(
        val status: String,
        val message: String,
        val userId: String,
        val connectedAt: String
)

data class HealthDataResponse(
        val status: String,
        val dataType: String,
        val userId: String,
        val startTime: String,
        val endTime: String,
        val data: List<Any>
)
