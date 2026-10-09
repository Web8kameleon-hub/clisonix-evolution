#define PULSE_BASE 0x10000000u
#define SYNC_BASE 0x10001000u
#define MESH_BASE 0x10002000u
#define KLOUD_BASE 0x10003000u
#define UART_BASE 0x10004000u

volatile unsigned int *pulse_ctrl = (unsigned int *)PULSE_BASE;
volatile unsigned int *sync_ctrl = (unsigned int *)SYNC_BASE;
volatile unsigned int *mesh_ctrl = (unsigned int *)MESH_BASE;
volatile unsigned int *kloud_status = (unsigned int *)KLOUD_BASE;
volatile unsigned int *uart_status = (unsigned int *)UART_BASE;
volatile unsigned int *uart_tx = (unsigned int *)UART_BASE;

void pulse_init(void) { *pulse_ctrl = 1u; }
void sync_init(void) { *sync_ctrl = 1u; }
void mesh_register(void) { *mesh_ctrl = 1u; }

static void uart_wait_ready(void)
{
    while ((*uart_status & 0x1u) == 0u)
    {
    }
}

static void uart_putc(char ch)
{
    uart_wait_ready();
    *uart_tx = (unsigned int)(unsigned char)ch;
}

static void uart_puts(const char *text)
{
    while (*text)
    {
        if (*text == '\n')
        {
            uart_putc('\r');
        }
        uart_putc(*text++);
    }
}

void sovereign_handshake(void)
{
    while ((kloud_status[0] & 0x1u) == 0u)
    {
    }
}

void supervisor_main(void)
{
    uart_puts("KLOUd Supervisor Booting...\n");
    pulse_init();
    uart_puts("Pulse OK\n");
    sync_init();
    uart_puts("Sync start\n");
    sovereign_handshake();
    uart_puts("Sovereign ACK\n");
    mesh_register();
    uart_puts("Mesh Registered\n");

    while (1)
    {
        uart_puts("Bridge Ready\n");
        for (volatile unsigned int delay = 0; delay < 500000u; ++delay)
        {
        }
    }
}
