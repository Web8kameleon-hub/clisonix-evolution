package com.clisonix.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.clisonix.app.ui.viewmodel.ModuleHealthUi
import com.clisonix.app.ui.viewmodel.OceanCuriosityUiState

@Composable
fun OceanCuriosityScreen(
    state: OceanCuriosityUiState,
    onQueryChange: (String) -> Unit,
    onRequestModule: (String) -> Unit,
    onRefresh: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Text("Ocean Curiosity", style = MaterialTheme.typography.headlineMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Porta hyrëse e Clisonix. Shkruaj kërkesën dhe sistemi do të route-ojë te moduli i duhur.",
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        item {
            OutlinedTextField(
                value = state.query,
                onValueChange = onQueryChange,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Kërko modul (ocean, jona, neural, alba)") },
                singleLine = true,
            )
        }

        item {
            Row(modifier = Modifier.fillMaxWidth()) {
                Button(
                    onClick = { onRequestModule(state.query) },
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Ekzekuto Posta Link")
                }
                Spacer(modifier = Modifier.padding(4.dp))
                Button(
                    onClick = onRefresh,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Refresh")
                }
            }
        }

        item {
            if (state.isRefreshing) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    CircularProgressIndicator()
                    Text("Duke marrë të dhëna live...")
                }
            }

            state.lastError?.let {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Gabim: $it",
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }

        item {
            Divider()
            Text("Ocean Payload Cache", style = MaterialTheme.typography.titleMedium)
            Text(
                text = state.oceanPayload?.take(180) ?: "Nuk ka cache ende.",
                style = MaterialTheme.typography.bodySmall,
            )
            Text(
                text = "UpdatedAt: ${state.oceanUpdatedAtEpochMs ?: "-"}",
                style = MaterialTheme.typography.labelSmall,
            )
        }

        item {
            Divider()
            Text("Module Endpoint Health", style = MaterialTheme.typography.titleMedium)
        }

        items(state.health, key = { it.route }) { item ->
            ModuleHealthRow(item)
        }
    }
}

@Composable
private fun ModuleHealthRow(item: ModuleHealthUi) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(text = item.moduleName, style = MaterialTheme.typography.titleSmall)
        Text(text = item.endpoint, style = MaterialTheme.typography.bodySmall)
        Text(
            text = if (item.isHealthy) {
                "Healthy (HTTP ${item.statusCode ?: "?"})"
            } else {
                "Unhealthy (${item.errorMessage ?: "HTTP ${item.statusCode ?: "?"}"})"
            },
            color = if (item.isHealthy) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}
