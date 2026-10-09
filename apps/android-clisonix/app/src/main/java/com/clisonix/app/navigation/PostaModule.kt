package com.clisonix.app.navigation

data class PostaModule(
    val name: String,
    val route: String,
    val endpoint: String,
)

object ClisonixModules {
    val ocean = PostaModule(
        name = "Ocean Curiosity",
        route = "clisonix://module/ocean",
        endpoint = "https://api.clisonix.com/v1/ocean-curiosity",
    )

    val all = listOf(
        ocean,
        PostaModule(
            name = "JONA Intelligence",
            route = "clisonix://module/jona",
            endpoint = "https://api.clisonix.com/v1/jona-audio",
        ),
        PostaModule(
            name = "Neural Brain",
            route = "clisonix://module/neural",
            endpoint = "https://api.clisonix.com/v1/neural-brain",
        ),
        PostaModule(
            name = "ALBA Collection",
            route = "clisonix://module/alba",
            endpoint = "https://api.clisonix.com/v1/alba-data",
        ),
        PostaModule(
            name = "Protocol Kitchen",
            route = "clisonix://module/protocol-kitchen",
            endpoint = "https://api.clisonix.com/v1/protocol-kitchen",
        ),
        PostaModule(
            name = "Reporting Engine",
            route = "clisonix://module/reporting",
            endpoint = "https://api.clisonix.com/v1/reporting",
        ),
    )
}
