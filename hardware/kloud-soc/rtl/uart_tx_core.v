module uart_tx_core #(
    parameter integer CLK_HZ = 25000000,
    parameter integer BAUD   = 115200
) (
    input  wire       clk,
    input  wire       reset,
    input  wire [7:0] data,
    input  wire       valid,
    output reg        ready,
    output reg        tx
);

    localparam integer CLKS_PER_BIT = CLK_HZ / BAUD;

    reg [15:0] clk_count;
    reg [3:0]  bit_index;
    reg [9:0]  shift_reg;
    reg        busy;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            clk_count <= 16'd0;
            bit_index <= 4'd0;
            shift_reg <= 10'h3ff;
            busy      <= 1'b0;
            ready     <= 1'b1;
            tx        <= 1'b1;
        end else begin
            if (!busy) begin
                ready <= 1'b1;
                tx    <= 1'b1;

                if (valid) begin
                    busy      <= 1'b1;
                    ready     <= 1'b0;
                    clk_count <= 16'd0;
                    bit_index <= 4'd0;
                    shift_reg <= {1'b1, data, 1'b0};
                    tx        <= 1'b0;
                end
            end else begin
                if (clk_count == CLKS_PER_BIT - 1) begin
                    clk_count <= 16'd0;
                    tx        <= shift_reg[1];
                    shift_reg <= {1'b1, shift_reg[9:1]};

                    if (bit_index == 4'd9) begin
                        busy      <= 1'b0;
                        ready     <= 1'b1;
                        bit_index <= 4'd0;
                        tx        <= 1'b1;
                    end else begin
                        bit_index <= bit_index + 4'd1;
                    end
                end else begin
                    clk_count <= clk_count + 16'd1;
                end
            end
        end
    end

endmodule
