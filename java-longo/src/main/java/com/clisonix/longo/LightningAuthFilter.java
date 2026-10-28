package com.clisonix.longo;

import com.sun.net.httpserver.Filter;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * Verifikon cookie-t e sesionit duke i dërguar ato te Lightning SPP.
 * Nuk ka fake auth: nëse Lightning kthen 200, përdoruesi është i vlefshëm.
 */
public final class LightningAuthFilter extends Filter {
    private final String lightningBaseUrl;
    private final HttpClient httpClient;

    public LightningAuthFilter(String lightningBaseUrl) {
        this.lightningBaseUrl = lightningBaseUrl.replaceAll("/+$", "");
        this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();
    }

    @Override
    public void doFilter(HttpExchange exchange, Chain chain) throws IOException {
        String path = exchange.getRequestURI().getPath();

        // Endpoint-et publike (pa auth)
        if (path.equals("/health") || path.startsWith("/v1/auth/")) {
            chain.doFilter(exchange);
            return;
        }

        String cookie = exchange.getRequestHeaders().getFirst("Cookie");
        if (cookie == null || cookie.isBlank()) {
            sendUnauthorized(exchange);
            return;
        }

        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(lightningBaseUrl + "/api/account"))
                .header("Cookie", cookie)
                .timeout(Duration.ofSeconds(8))
                .GET()
                .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                // Përdoruesi është i vlefshëm sipas Lightning
                exchange.setAttribute("lightning-verified", "true");
                chain.doFilter(exchange);
            } else {
                sendUnauthorized(exchange);
            }
        } catch (Exception e) {
            sendUnauthorized(exchange);
        }
    }

    private void sendUnauthorized(HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        byte[] body = "{\"error\":\"unauthorized\",\"message\":\"Lightning session invalid\"}".getBytes();
        exchange.sendResponseHeaders(401, body.length);
        exchange.getResponseBody().write(body);
        exchange.close();
    }

    @Override
    public String description() {
        return "Lightning Session Auth Filter";
    }
}
