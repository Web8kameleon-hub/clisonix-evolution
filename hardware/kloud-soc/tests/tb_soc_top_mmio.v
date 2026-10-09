`timescale 1ns/1ps

module tb_soc_top_mmio;
  reg clk = 1'b0;
  reg resetn = 1'b0;
  wire uart_tx;

  reg saw_uart_stb = 1'b0;
  reg [31:0] read_data = 32'd0;

  soc_top dut (
    .clk(clk),
    .resetn(resetn),
    .uart_tx(uart_tx)
  );

  always #5 clk = ~clk;

  always @(posedge clk) begin
    if (dut.uart_tx_stb) begin
      saw_uart_stb <= 1'b1;
    end
  end

  task mmio_write(input [31:0] addr, input [31:0] data);
    begin
      force dut.mem_valid = 1'b1;
      force dut.mem_wstrb = 4'hF;
      force dut.mem_addr = addr;
      force dut.mem_wdata = data;
      @(posedge clk);
      release dut.mem_valid;
      release dut.mem_wstrb;
      release dut.mem_addr;
      release dut.mem_wdata;
      @(posedge clk);
    end
  endtask

  task mmio_read(input [31:0] addr, output [31:0] data);
    begin
      force dut.mem_valid = 1'b1;
      force dut.mem_wstrb = 4'h0;
      force dut.mem_addr = addr;
      force dut.mem_wdata = 32'h0000_0000;
      @(posedge clk);
      #1 data = dut.mem_rdata;
      release dut.mem_valid;
      release dut.mem_wstrb;
      release dut.mem_addr;
      release dut.mem_wdata;
      @(posedge clk);
    end
  endtask

  initial begin
    $dumpfile("out/tb_soc_top_mmio.vcd");
    $dumpvars(0, tb_soc_top_mmio);

    repeat (3) @(posedge clk);
    resetn = 1'b1;
    repeat (3) @(posedge clk);

    // Enable pulse engine and observe counter progression.
    mmio_write(32'h1000_0000, 32'h0000_0001);
    repeat (6) @(posedge clk);
    mmio_read(32'h1000_0000, read_data);
    if (read_data < 32'd3) begin
      $fatal(1, "pulse counter did not advance, value=%0d", read_data);
    end

    // Start sync and verify status register.
    mmio_write(32'h1001_0000, 32'h0000_0001);
    repeat (3) @(posedge clk);
    mmio_read(32'h1001_0000, read_data);
    if (read_data[0] != 1'b1) begin
      $fatal(1, "sync status not asserted");
    end

    // Register mesh and verify mirror register.
    mmio_write(32'h1002_0000, 32'h0000_0001);
    repeat (2) @(posedge clk);
    mmio_read(32'h1002_0000, read_data);
    if (read_data[0] != 1'b1) begin
      $fatal(1, "mesh register did not latch");
    end

    // Verify bridge summary bits.
    mmio_read(32'h1003_0000, read_data);
    if (read_data[3:0] != 4'b1111) begin
      $fatal(1, "bridge summary bits not fully asserted, value=%b", read_data[3:0]);
    end

    // Trigger UART path and ensure strobe observed.
    mmio_write(32'h1004_0000, 32'h0000_0041);
    repeat (2) @(posedge clk);
    if (!saw_uart_stb) begin
      $fatal(1, "uart write strobe was not observed");
    end

    $display("PASS: soc_top MMIO map checks");
    $finish;
  end
endmodule
