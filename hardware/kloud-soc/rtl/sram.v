module sram (
    input  wire        clk,
    input  wire [9:0]  addr,
    input  wire [31:0] wdata,
    input  wire [3:0]  wstrb,
    output reg  [31:0] rdata
);

reg [31:0] mem [0:1023];
integer i;

initial begin
    for (i = 0; i < 1024; i = i + 1)
        mem[i] = 32'h00000000;
end

always @(posedge clk) begin
    if (wstrb[0]) mem[addr][7:0]   <= wdata[7:0];
    if (wstrb[1]) mem[addr][15:8]  <= wdata[15:8];
    if (wstrb[2]) mem[addr][23:16] <= wdata[23:16];
    if (wstrb[3]) mem[addr][31:24] <= wdata[31:24];
end

always @(*) begin
    rdata = mem[addr];
end

endmodule
