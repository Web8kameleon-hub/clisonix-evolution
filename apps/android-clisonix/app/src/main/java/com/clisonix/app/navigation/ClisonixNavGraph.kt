package com.clisonix.app.navigation

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.clisonix.app.ui.screens.OceanCuriosityScreen
import com.clisonix.app.ui.screens.PostaLinkScreen
import com.clisonix.app.ui.viewmodel.OceanCuriosityViewModel

@Composable
fun ClisonixNavGraph(context: Context) {
    val navController = rememberNavController()
    val router = remember { PostaLinkRouter(context) }
    val oceanViewModel: OceanCuriosityViewModel = viewModel()
    val oceanState = oceanViewModel.uiState.collectAsStateWithLifecycle()

    NavHost(
        navController = navController,
        startDestination = "ocean_curiosity",
    ) {
        composable("ocean_curiosity") {
            OceanCuriosityScreen(
                state = oceanState.value,
                onQueryChange = oceanViewModel::onQueryChange,
                onRequestModule = { query ->
                    val target = router.resolveFromQuery(query)
                    val route = target.route.substringAfterLast('/')
                    navController.navigate("posta_links/$route")
                },
                onRefresh = oceanViewModel::refreshAll,
            )
        }

        composable(
            route = "posta_links/{moduleKey}",
            arguments = listOf(navArgument("moduleKey") { type = NavType.StringType }),
        ) { backStack ->
            val key = backStack.arguments?.getString("moduleKey").orEmpty()
            val module = ClisonixModules.all.firstOrNull { it.route.endsWith("/$key") } ?: ClisonixModules.ocean
            val health = oceanState.value.health.firstOrNull { it.route == module.route }
            PostaLinkScreen(
                module = module,
                endpointHealthy = health?.isHealthy,
                endpointStatusCode = health?.statusCode,
                onOpenLink = { router.openModule(it) },
            )
        }
    }
}
