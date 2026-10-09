// Minimal RISC-V smoke-test source.
int add(int a, int b) {
    return a + b;
}

int main(void) {
    volatile int x = add(20, 22);
    return x == 42 ? 0 : 1;
}
