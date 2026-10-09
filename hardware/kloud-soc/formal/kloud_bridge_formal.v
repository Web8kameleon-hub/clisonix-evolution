module kloud_bridge_formal;
  reg clk = 1'b0;
  always @($global_clock) begin
    clk <= ~clk;
  end

  reg past_valid = 1'b0;
  always @(posedge clk) begin
    past_valid <= 1'b1;
  end

  (* anyseq *) reg reset;
  (* anyseq *) reg sovereign_ready;
  (* anyseq *) reg [31:0] pulse_count;
  (* anyseq *) reg sync_ok;
  (* anyseq *) reg mesh_node_registered;

  wire sovereign_ack;
  wire proof_of_life;
  wire connected_monitored;
  wire synchronized;
  wire mesh_ok;

  kloud_bridge_hw dut (
    .clk(clk),
    .reset(reset),
    .sovereign_ready(sovereign_ready),
    .sovereign_ack(sovereign_ack),
    .pulse_count(pulse_count),
    .sync_ok(sync_ok),
    .mesh_node_registered(mesh_node_registered),
    .proof_of_life(proof_of_life),
    .connected_monitored(connected_monitored),
    .synchronized(synchronized),
    .mesh_ok(mesh_ok)
  );

  always @(posedge clk) begin
    if (!past_valid) begin
      assume(reset);
    end

    if (reset) begin
      assert(!sovereign_ack);
      assert(!proof_of_life);
      assert(!connected_monitored);
      assert(!synchronized);
      assert(!mesh_ok);
    end

    if (past_valid && !$past(reset) && $past(sovereign_ready)) begin
      assert(sovereign_ack);
    end

    if (past_valid && !$past(reset) && $past(sovereign_ack)) begin
      assert(sovereign_ack);
    end

    if (past_valid && !$past(reset) && $past(sync_ok)) begin
      assert(synchronized);
    end

    if (past_valid && !$past(reset) && $past(mesh_node_registered)) begin
      assert(mesh_ok);
      assert(proof_of_life);
    end

    if (past_valid && !$past(reset) && ($past(pulse_count) > 32'd0)) begin
      assert(connected_monitored);
    end
  end

endmodule
