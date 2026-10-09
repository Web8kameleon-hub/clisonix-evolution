module ulx3s_top (
    input  wire clk_25mhz,
    input  wire btn0,
    output wire uart_tx
);

    wire clk = clk_25mhz;
    wire resetn = ~btn0;

    soc_top soc (
        .clk(clk),
        .resetn(resetn),
        .uart_tx(uart_tx)
    );

endmodule
