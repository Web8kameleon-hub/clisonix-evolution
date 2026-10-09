module rom (
    input  wire        clk,
    input  wire [10:0] addr,
    output reg  [31:0] data
);

reg [31:0] mem [0:2047];

initial begin
    $readmemh("hardware/kloud-soc/firmware/firmware.hex", mem);
end

always @(*) begin
    data = mem[addr];
end

endmodule
