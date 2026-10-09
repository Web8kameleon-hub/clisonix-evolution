module soc_top (
    input  wire clk,
    input  wire resetn,
    output wire uart_tx
);

    wire        trap;
    wire        mem_valid;
    wire        mem_instr;
    wire        mem_ready;
    wire [31:0] mem_addr;
    wire [31:0] mem_wdata;
    wire [3:0]  mem_wstrb;
    wire [31:0] mem_rdata;

    reg  pulse_enable;
    reg  sync_start;
    reg  mesh_reg;
    reg  uart_tx_stb;
    reg  [7:0] uart_tx_data;

    wire [31:0] rom_data;
    wire [10:0] rom_addr = mem_addr[12:2];

    wire [31:0] pulse_count;
    wire        sync_ok;
    wire        connected_monitored;
    wire        synchronized;
    wire        mesh_ok;
    wire        proof_of_life;
    wire        mesh_node_registered = mesh_reg;
    wire        uart_ready;

    wire        sram_selected = (mem_addr[31:16] == 16'h0001);
    wire [31:0] sram_rdata;

    assign mem_ready = mem_valid;

    picorv32 #(
        .ENABLE_MUL(0),
        .ENABLE_DIV(0),
        .ENABLE_IRQ(0),
        .PROGADDR_RESET(32'h0000_0000)
    ) cpu (
        .clk(clk),
        .resetn(resetn),
        .trap(trap),
        .mem_valid(mem_valid),
        .mem_instr(mem_instr),
        .mem_ready(mem_ready),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_wstrb(mem_wstrb),
        .mem_rdata(mem_rdata),
        .irq(32'b0),
        .eoi()
    );

    rom rom_inst (
        .clk(clk),
        .addr(rom_addr),
        .data(rom_data)
    );

    sram sram_inst (
        .clk(clk),
        .addr(mem_addr[11:2]),
        .wdata(mem_wdata),
        .wstrb((mem_valid && sram_selected) ? mem_wstrb : 4'b0000),
        .rdata(sram_rdata)
    );

    uart_tx_core #(
        .CLK_HZ(25000000),
        .BAUD(115200)
    ) uart_inst (
        .clk(clk),
        .reset(~resetn),
        .data(uart_tx_data),
        .valid(uart_tx_stb),
        .ready(uart_ready),
        .tx(uart_tx)
    );

    pulse_engine pulse_inst (
        .clk(clk),
        .reset(~resetn),
        .pulse_enable(pulse_enable),
        .pulse_count(pulse_count)
    );

    sync_engine sync_inst (
        .clk(clk),
        .reset(~resetn),
        .start(sync_start),
        .sync_ok(sync_ok)
    );

    kloud_bridge_hw bridge_inst (
        .clk(clk),
        .reset(~resetn),
        .sovereign_ready(sync_ok),
        .sovereign_ack(),
        .pulse_count(pulse_count),
        .sync_ok(sync_ok),
        .mesh_node_registered(mesh_node_registered),
        .proof_of_life(proof_of_life),
        .connected_monitored(connected_monitored),
        .synchronized(synchronized),
        .mesh_ok(mesh_ok)
    );

    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            pulse_enable <= 1'b0;
            sync_start   <= 1'b0;
            mesh_reg     <= 1'b0;
            uart_tx_stb  <= 1'b0;
            uart_tx_data <= 8'h00;
        end else begin
            uart_tx_stb <= 1'b0;

            if (mem_valid && (mem_wstrb != 4'b0000)) begin
                case (mem_addr[31:16])
                    16'h1000: pulse_enable <= mem_wdata[0];
                    16'h1001: sync_start   <= mem_wdata[0];
                    16'h1002: mesh_reg     <= mem_wdata[0];
                    16'h1004: begin
                        if (uart_ready) begin
                            uart_tx_data <= mem_wdata[7:0];
                            uart_tx_stb  <= 1'b1;
                        end
                    end
                    default: begin end
                endcase
            end
        end
    end

    assign mem_rdata = (mem_addr[31:16] == 16'h0000) ? rom_data :
                       (mem_addr[31:16] == 16'h0001) ? sram_rdata :
                       (mem_addr[31:16] == 16'h1000) ? pulse_count :
                       (mem_addr[31:16] == 16'h1001) ? {31'b0, sync_ok} :
                       (mem_addr[31:16] == 16'h1002) ? {31'b0, mesh_node_registered} :
                       (mem_addr[31:16] == 16'h1003) ? {28'b0, proof_of_life, mesh_ok, synchronized, connected_monitored} :
                       (mem_addr[31:16] == 16'h1004) ? {31'b0, uart_ready} :
                       32'h00000000;

endmodule
