package com.clisonix.app.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.clisonix.app.data.ClisonixApiClient
import com.clisonix.app.data.ClisonixRepository
import com.clisonix.app.data.local.ClisonixDatabase
import com.clisonix.app.navigation.ClisonixModules
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ModuleHealthUi(
    val route: String,
    val moduleName: String,
    val endpoint: String,
    val isHealthy: Boolean,
    val statusCode: Int?,
    val errorMessage: String?,
    val checkedAtEpochMs: Long,
)

data class OceanCuriosityUiState(
    val query: String = "",
    val isRefreshing: Boolean = false,
    val lastError: String? = null,
    val oceanPayload: String? = null,
    val oceanUpdatedAtEpochMs: Long? = null,
    val health: List<ModuleHealthUi> = emptyList(),
)

class OceanCuriosityViewModel(application: Application) : AndroidViewModel(application) {
    private val repository = ClisonixRepository(
        api = ClisonixApiClient.api,
        dao = ClisonixDatabase.get(application).dao(),
    )

    private val query = MutableStateFlow("")
    private val isRefreshing = MutableStateFlow(false)
    private val lastError = MutableStateFlow<String?>(null)

    val uiState: StateFlow<OceanCuriosityUiState> = combine(
        query,
        isRefreshing,
        lastError,
        repository.observeOceanCache().map { it?.payload to it?.updatedAtEpochMs },
        repository.observeModuleHealth().map { list ->
            list.map {
                ModuleHealthUi(
                    route = it.route,
                    moduleName = it.moduleName,
                    endpoint = it.endpoint,
                    isHealthy = it.isHealthy,
                    statusCode = it.statusCode,
                    errorMessage = it.errorMessage,
                    checkedAtEpochMs = it.checkedAtEpochMs,
                )
            }
        },
    ) { queryValue, refreshing, error, ocean, health ->
        OceanCuriosityUiState(
            query = queryValue,
            isRefreshing = refreshing,
            lastError = error,
            oceanPayload = ocean.first,
            oceanUpdatedAtEpochMs = ocean.second,
            health = health,
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = OceanCuriosityUiState(),
    )

    init {
        refreshAll()
    }

    fun onQueryChange(value: String) {
        query.value = value
    }

    fun refreshAll() {
        viewModelScope.launch {
            isRefreshing.update { true }
            lastError.update { null }
            runCatching {
                repository.refreshOceanCuriosity()
                repository.refreshModuleHealth(ClisonixModules.all)
            }.onFailure {
                lastError.update { error -> error ?: it.message ?: "Unknown error" }
            }
            isRefreshing.update { false }
        }
    }
}
