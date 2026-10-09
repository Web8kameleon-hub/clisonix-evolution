module sync_engine(
    input  wire clk,
    input  wire reset,
    input  wire start,
    output reg  sync_ok
);

reg [7:0] state;

always @(posedge clk or posedge reset) begin
    if (reset) begin
        state <= 8'd0;
        sync_ok <= 1'b0;
    end else begin
        case (state)
            8'd0: if (start) state <= 8'd1;
            8'd1: begin
                sync_ok <= 1'b1;
                state <= 8'd2;
            end
            default: state <= state;
        endcase
    end
end

endmodule
