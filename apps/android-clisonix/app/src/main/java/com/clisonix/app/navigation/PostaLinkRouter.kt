package com.clisonix.app.navigation

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.browser.customtabs.CustomTabsIntent

class PostaLinkRouter(private val context: Context) {

    fun openModule(module: PostaModule) {
        val deepLinkIntent = Intent(Intent.ACTION_VIEW, Uri.parse(module.route)).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }

        val canHandleDeepLink = deepLinkIntent.resolveActivity(context.packageManager) != null
        if (canHandleDeepLink) {
            context.startActivity(deepLinkIntent)
            return
        }

        openInCustomTab(module.webFallbackUrl())
    }

    fun resolveFromQuery(query: String): PostaModule {
        return resolveModuleFromQuery(query, ClisonixModules.all)
    }

    private fun openInCustomTab(url: String) {
        val customTab = CustomTabsIntent.Builder().build()
        customTab.intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        customTab.launchUrl(context, Uri.parse(url))
    }

    private fun PostaModule.webFallbackUrl(): String {
        val key = route.substringAfterLast('/').ifBlank { "ocean" }
        return "https://www.clisonix.com/modules/$key"
    }

    companion object {
        fun resolveModuleFromQuery(query: String, modules: List<PostaModule>): PostaModule {
            val normalized = query.lowercase()
            val ocean = modules.firstOrNull { it.route.endsWith("/ocean") } ?: modules.first()
            val jona = modules.firstOrNull { it.route.endsWith("/jona") }
            val neural = modules.firstOrNull { it.route.endsWith("/neural") }
            val alba = modules.firstOrNull { it.route.endsWith("/alba") }
            val protocolKitchen = modules.firstOrNull { it.route.endsWith("/protocol-kitchen") }
            val reporting = modules.firstOrNull { it.route.endsWith("/reporting") }

            return when {
                normalized.contains("ocean") -> ocean
                normalized.contains("jona") || normalized.contains("audio") -> jona ?: ocean
                normalized.contains("neural") || normalized.contains("brain") || normalized.contains("eeg") -> neural ?: ocean
                normalized.contains("alba") || normalized.contains("collection") -> alba ?: ocean
                normalized.contains("protocol") -> protocolKitchen ?: ocean
                normalized.contains("report") -> reporting ?: ocean
                else -> ocean
            }
        }
    }
}
