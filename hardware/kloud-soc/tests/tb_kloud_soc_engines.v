`timescale 1ns/1ps

module tb_kloud_soc_engines;
  reg clk = 1'b0;
  reg reset = 1'b1;

  reg pulse_enable = 1'b0;
  wire [31:0] pulse_count;

  reg sync_start = 1'b0;
  wire sync_ok;

  reg sovereign_ready = 1'b0;
  reg [31:0] bridge_pulse_count = 32'd0;
  reg bridge_sync_ok = 1'b0;
  reg mesh_node_registered = 1'b0;

  wire sovereign_ack;
  wire proof_of_life;
  wire connected_monitored;
  wire synchronized;
  wire mesh_ok;

  always #5 clk = ~clk;

  pulse_engine pulse_dut (
    .clk(clk),
    .reset(reset),
    .pulse_enable(pulse_enable),
    .pulse_count(pulse_count)
  );

  sync_engine sync_dut (
    .clk(clk),
    .reset(reset),
    .start(sync_start),
    .sync_ok(sync_ok)
  );

  kloud_bridge_hw bridge_dut (
    .clk(clk),
    .reset(reset),
    .sovereign_ready(sovereign_ready),
    .sovereign_ack(sovereign_ack),
    .pulse_count(bridge_pulse_count),
    .sync_ok(bridge_sync_ok),
    .mesh_node_registered(mesh_node_registered),
    .proof_of_life(proof_of_life),
    .connected_monitored(connected_monitored),
    .synchronized(synchronized),
    .mesh_ok(mesh_ok)
  );

  initial begin
    $dumpfile("out/tb_kloud_soc_engines.vcd");
    $dumpvars(0, tb_kloud_soc_engines);

    repeat (3) @(posedge clk);
    reset = 1'b0;

    pulse_enable = 1'b1;
    repeat (5) @(posedge clk);
    pulse_enable = 1'b0;

    if (pulse_count != 32'd5) begin
      $fatal(1, "pulse_engine count mismatch: expected 5, got %0d", pulse_count);
    end

    sync_start = 1'b1;
    @(posedge clk);
    sync_start = 1'b0;
    repeat (2) @(posedge clk);

    if (!sync_ok) begin
      $fatal(1, "sync_engine did not assert sync_ok");
    end

    bridge_pulse_count = pulse_count;
    bridge_sync_ok = sync_ok;
    sovereign_ready = 1'b1;
    mesh_node_registered = 1'b1;
    repeat (2) @(posedge clk);

    if (!sovereign_ack) begin
      $fatal(1, "bridge did not assert sovereign_ack");
    end

    if (!connected_monitored) begin
      $fatal(1, "bridge did not assert connected_monitored");
    end

    if (!synchronized) begin
      $fatal(1, "bridge did not assert synchronized");
    end

    if (!mesh_ok || !proof_of_life) begin
      $fatal(1, "bridge did not assert mesh/proof signals");
    end

    $display("PASS: kloud-soc engine simulation checks");
    $finish;
  end
endmodule
