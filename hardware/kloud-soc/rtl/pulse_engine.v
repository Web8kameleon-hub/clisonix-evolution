module pulse_engine(
    input  wire       clk,
    input  wire       reset,
    input  wire       pulse_enable,
    output reg [31:0] pulse_count
);

always @(posedge clk or posedge reset) begin
    if (reset)
        pulse_count <= 32'd0;
    else if (pulse_enable)
        pulse_count <= pulse_count + 32'd1;
end

endmodule
