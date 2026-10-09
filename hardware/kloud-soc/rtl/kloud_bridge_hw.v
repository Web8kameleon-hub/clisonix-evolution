module kloud_bridge_hw (
    input  wire        clk,
    input  wire        reset,
    input  wire        sovereign_ready,
    output reg         sovereign_ack,
    input  wire [31:0] pulse_count,
    input  wire        sync_ok,
    input  wire        mesh_node_registered,
    output reg         proof_of_life,
    output reg         connected_monitored,
    output reg         synchronized,
    output reg         mesh_ok
);

always @(posedge clk or posedge reset) begin
    if (reset) begin
        sovereign_ack       <= 1'b0;
        proof_of_life       <= 1'b0;
        connected_monitored <= 1'b0;
        synchronized        <= 1'b0;
        mesh_ok             <= 1'b0;
    end else begin
        if (sovereign_ready)
            sovereign_ack <= 1'b1;

        if (pulse_count > 32'd0)
            connected_monitored <= 1'b1;

        if (sync_ok)
            synchronized <= 1'b1;

        if (mesh_node_registered) begin
            mesh_ok <= 1'b1;
            proof_of_life <= 1'b1;
        end
    end
end

endmodule
