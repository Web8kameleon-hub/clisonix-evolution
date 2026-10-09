package com.clisonix.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.clisonix.app.navigation.PostaModule

@Composable
fun PostaLinkScreen(
    module: PostaModule,
    endpointHealthy: Boolean?,
    endpointStatusCode: Int?,
    onOpenLink: (PostaModule) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.Top,
    ) {
        Text("Posta Link", style = MaterialTheme.typography.headlineSmall)
        Spacer(modifier = Modifier.height(12.dp))
        Text("Moduli: ${module.name}")
        Text("Link: ${module.route}")
        Text("API: ${module.endpoint}")
        Text(
            text = when (endpointHealthy) {
                true -> "Health: Healthy (HTTP ${endpointStatusCode ?: "?"})"
                false -> "Health: Unhealthy (HTTP ${endpointStatusCode ?: "?"})"
                null -> "Health: No data"
            },
            color = when (endpointHealthy) {
                true -> MaterialTheme.colorScheme.primary
                false -> MaterialTheme.colorScheme.error
                null -> MaterialTheme.colorScheme.onSurfaceVariant
            },
        )
        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { onOpenLink(module) },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Hap Modulin")
        }
    }
}
