//! Entrypoint për sidecar-in: pipeline real-time me NO_FAKE_DATA_POLICY

mod internal {
    pub mod telemetry;
    pub mod trust;
    pub mod policy;
    pub mod pipeline;
}

use actix_web::{web, App, HttpServer, Responder, HttpResponse};
use internal::telemetry::TelemetryEvent;
use internal::pipeline::{process_event, PipelineResult};

async fn ingest(event: web::Json<TelemetryEvent>) -> impl Responder {
    let result: PipelineResult = process_event(event.into_inner());
    HttpResponse::Ok().json(result)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("[Clisonix-Security] Sidecar pipeline started (NO_FAKE_DATA_POLICY)");
    HttpServer::new(|| {
        App::new()
            .route("/ingest", web::post().to(ingest))
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
