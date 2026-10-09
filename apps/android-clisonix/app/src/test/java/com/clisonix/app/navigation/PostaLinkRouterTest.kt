package com.clisonix.app.navigation

import org.junit.Assert.assertEquals
import org.junit.Test

class PostaLinkRouterTest {

    @Test
    fun resolveModuleFromQuery_matchesNeuralKeywords() {
        val result = PostaLinkRouter.resolveModuleFromQuery("need eeg brain insights", ClisonixModules.all)

        assertEquals("clisonix://module/neural", result.route)
    }

    @Test
    fun resolveModuleFromQuery_matchesReportingKeyword() {
        val result = PostaLinkRouter.resolveModuleFromQuery("generate report for session", ClisonixModules.all)

        assertEquals("clisonix://module/reporting", result.route)
    }

    @Test
    fun resolveModuleFromQuery_fallsBackToOcean() {
        val result = PostaLinkRouter.resolveModuleFromQuery("unknown-module-keyword", ClisonixModules.all)

        assertEquals("clisonix://module/ocean", result.route)
    }
}
